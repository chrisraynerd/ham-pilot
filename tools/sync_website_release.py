"""Publish checked stable GitHub firmware assets to an independent web directory.

Run as an unprivileged systemd service. No GitHub token, app source or USB access
is needed. Publishing a stable release in the public repository is the approval.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import struct
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import zipfile

REPO = 'chrisraynerd/ham-pilot'
PARTS = {'bootloader.bin': 4096, 'partitions.bin': 32768,
         'boot_app0.bin': 57344, 'ham-pilot.bin': 65536}
LIMITS = {'bootloader.bin': 28672, 'partitions.bin': 4096,
          'boot_app0.bin': 8192, 'ham-pilot.bin': 1966080}
DOCS = {'INSTALL.md', 'LICENSE.md', 'NOTICE.md', 'THIRD-PARTY-NOTICES.md',
        'Flash-HamPilot.ps1', 'SHA256SUMS'}


def download(url, limit):
    host = urlsplit(url)
    if host.scheme != 'https' or host.hostname not in ('api.github.com', 'github.com'):
        raise ValueError('Unexpected release download origin')
    request = Request(url, headers={'User-Agent': 'Ham-Pilot-Website-Sync',
                                   'Accept': 'application/vnd.github+json' if host.hostname == 'api.github.com' else '*/*'})
    with urlopen(request, timeout=90) as response:
        target = urlsplit(response.url)
        if target.scheme != 'https' or not (target.hostname in ('api.github.com', 'github.com')
                or target.hostname.endswith('.githubusercontent.com')):
            raise ValueError('Unexpected release redirect origin')
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Release download exceeds size limit')
    return data


def checksums(data):
    entries = {}
    for line in data.decode('ascii').splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'([a-fA-F0-9]{64})  ([A-Za-z0-9_.-]+)', line)
        if not match or match[2] in entries:
            raise ValueError('Invalid or duplicate checksum entry')
        entries[match[2]] = match[1].lower()
    return entries


def extract_firmware(archive_path, destination):
    with zipfile.ZipFile(archive_path) as archive:
        names = set()
        total = 0
        for item in archive.infolist():
            name = PurePosixPath(item.filename)
            if name.is_absolute() or '..' in name.parts or '\\' in item.filename:
                raise ValueError('Unsafe firmware archive path')
            if stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError('Firmware archive contains a symbolic link')
            if item.is_dir():
                continue
            if item.filename in names:
                raise ValueError('Duplicate firmware archive path')
            names.add(item.filename)
            if item.filename not in PARTS and item.filename not in DOCS and not (
                    len(name.parts) > 1 and name.parts[0] == 'licences'):
                raise ValueError('Unexpected file in firmware package: ' + item.filename)
            total += item.file_size
            if item.file_size > 8 * 1024**2 or total > 64 * 1024**2:
                raise ValueError('Unpacked firmware package exceeds size limit')
            target = destination / item.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(item) as source, target.open('wb') as output:
                shutil.copyfileobj(source, output)
        if not (set(PARTS) | DOCS).issubset(names):
            raise ValueError('Incomplete firmware package')
    validate_firmware(destination)


def validate_firmware(root):
    expected = checksums((root / 'SHA256SUMS').read_bytes())
    if set(expected) != set(PARTS):
        raise ValueError('Firmware checksums must cover exactly four images')
    for name, offset in PARTS.items():
        data = (root / name).read_bytes()
        if not data or len(data) > LIMITS[name] or hashlib.sha256(data).hexdigest() != expected[name]:
            raise ValueError('Invalid firmware size or checksum: ' + name)
        end = (offset + len(data) + 4095) // 4096 * 4096
        if offset < 0xe000 and end > 0x9000:
            raise ValueError('Firmware would overwrite saved NVS settings')
        if name in ('bootloader.bin', 'ham-pilot.bin') and data[:1] + data[2:4] != bytes([0xe9, 2, 0x2f]):
            raise ValueError('Firmware requires ESP32 DIO/80MHz/4MB headers')
    table = (root / 'partitions.bin').read_bytes()
    entries = {}
    for at in range(0, len(table) - 31, 32):
        magic, kind, subtype, offset, size, label, flags = struct.unpack('<HBBII16sI', table[at:at+32])
        if magic != 0x50aa:
            break
        entries[label.rstrip(b'\0')] = (kind, subtype, offset, size)
    if entries.get(b'nvs') != (1, 2, 0x9000, 0x5000) or entries.get(b'app0') != (0, 16, 0x10000, 1966080):
        raise ValueError('Partition layout would change saved settings or the application slot')


def release_version(release):
    tag = release.get('tag_name', '')
    if release.get('draft') or release.get('prerelease') or not release.get('published_at'):
        raise ValueError('Only published stable releases may update the installer')
    if not re.fullmatch(r'v\d+\.\d+\.\d+', tag):
        raise ValueError('Stable release must use a vMAJOR.MINOR.PATCH tag')
    return tag[1:]


def sync(state, fetch=download):
    release = json.loads(fetch(f'https://api.github.com/repos/{REPO}/releases/latest', 2 * 1024**2))
    version = release_version(release)
    current = state / 'current'
    if current.exists():
        previous = json.loads((current / 'release.json').read_text())
        if tuple(map(int, version.split('.'))) <= tuple(map(int, previous['version'].split('.'))):
            print('Installer already current:', previous['version'])
            return previous
    assets = {}
    for asset in release.get('assets', []):
        name = asset['name']
        if name in assets:
            raise ValueError('Duplicate release asset')
        prefix = f'https://github.com/{REPO}/releases/download/v{version}/'
        if not asset['browser_download_url'].startswith(prefix):
            raise ValueError('Release asset is outside the approved repository/tag')
        assets[name] = asset['browser_download_url']
    aliases = {f'Ham-Pilot-{suffix}.zip': f'Ham-Pilot-v{version}-{suffix}.zip'
               for suffix in ('firmware', 'relink', 'third-party-source')}
    for alias, pattern in [('arduino-esp32-source.zip', r'arduino-esp32-\d+\.\d+\.\d+\.zip'),
                           ('esp-idf-source.zip', r'esp-idf-v\d+\.\d+\.\d+\.zip')]:
        matches = [name for name in assets if re.fullmatch(pattern, name)]
        if len(matches) != 1:
            raise ValueError('Missing or ambiguous corresponding source archive')
        aliases[alias] = matches[0]
    needed = set(aliases.values()) | {'SHA256SUMS-release.txt'}
    if not needed.issubset(assets):
        raise ValueError('Release lacks firmware, relinking or licence source materials')
    expected = checksums(fetch(assets['SHA256SUMS-release.txt'], 65536))
    if not set(aliases.values()).issubset(expected):
        raise ValueError('Release checksums do not cover all required archives')
    releases = state / 'releases'
    releases.mkdir(parents=True, exist_ok=True)
    target = releases / ('v' + version)
    if target.exists():
        # Recover a complete download left behind by interruption before activation.
        saved = json.loads((target / 'release.json').read_text())
        if saved['version'] != version or saved['releaseId'] != release['id']:
            raise ValueError('Existing version belongs to a different release')
        validate_firmware(target)
        for alias, original in aliases.items():
            if hashlib.sha256((target / alias).read_bytes()).hexdigest() != expected[original]:
                raise ValueError('Existing version archive checksum mismatch')
        activate(state, target)
        return saved
    with tempfile.TemporaryDirectory(prefix='.incoming-', dir=state) as temporary:
        stage = Path(temporary)
        for alias, original in aliases.items():
            data = fetch(assets[original], 128 * 1024**2)
            if hashlib.sha256(data).hexdigest() != expected[original]:
                raise ValueError('Release archive checksum mismatch: ' + original)
            (stage / alias).write_bytes(data)
        extract_firmware(stage / 'Ham-Pilot-firmware.zip', stage)
        manifest = {'name': 'Ham Pilot', 'version': version,
                    'new_install_prompt_erase': True, 'new_install_improv_wait_time': 0,
                    'builds': [{'chipFamily': 'ESP32', 'parts': [
                        {'path': f'/downloads/ham-pilot/releases/v{version}/{name}', 'offset': offset}
                        for name, offset in PARTS.items()]}]}
        metadata = {'version': version, 'tag': 'v' + version,
                    'githubRelease': f'https://github.com/{REPO}/releases/tag/v{version}',
                    'releaseId': release['id'], 'publishedAt': release['published_at'],
                    'applicationSha256': hashlib.sha256((stage / 'ham-pilot.bin').read_bytes()).hexdigest()}
        (stage / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        (stage / 'release.json').write_text(json.dumps(metadata, indent=2) + '\n')
        (stage / 'SHA256SUMS-release.txt').write_text(''.join(
            f'{expected[original]}  {alias}\n' for alias, original in aliases.items()))
        for path in stage.rglob('*'):
            path.chmod(0o755 if path.is_dir() else 0o644)
        stage.chmod(0o755)
        # Rename the complete immutable version before atomically changing current.
        stage.rename(target)
    activate(state, target)
    print('Installer updated to', version, metadata['applicationSha256'])
    return metadata


def activate(state, target):
    next_link = state / 'current.next'
    next_link.unlink(missing_ok=True)
    next_link.symlink_to(target, target_is_directory=True)
    os.replace(next_link, state / 'current')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir', type=Path, default=Path('/var/lib/ham-pilot'))
    args = parser.parse_args()
    args.state_dir.mkdir(parents=True, exist_ok=True)
    # A second timer/manual invocation must never race an update.
    import fcntl
    with (args.state_dir / '.sync.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        sync(args.state_dir.resolve())
