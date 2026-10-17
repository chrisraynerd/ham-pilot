"""End-to-end publisher tests with synthetic firmware and a fake GitHub feed."""
import hashlib
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile
from unittest.mock import patch
import sync_website_release as publisher


def fixture(version='0.3.5', unsafe=False):
    table = b''.join(struct.pack('<HBBII16sI', 0x50aa, *values, label, 0)
                     for values, label in [((1, 2, 0x9000, 0x5000), b'nvs'),
                                           ((0, 16, 0x10000, 1966080), b'app0')])
    binaries = {name: b'\xe9\x00\x02\x2f' + name.encode() for name in publisher.PARTS}
    binaries['partitions.bin'] = table
    sums = ''.join(hashlib.sha256(value).hexdigest() + '  ' + name + '\n' for name, value in binaries.items())
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as archive:
        for name, value in binaries.items():
            archive.writestr(name, value)
        for name in publisher.DOCS - {'SHA256SUMS'}:
            archive.writestr(name, 'Synthetic test fixture')
        archive.writestr('SHA256SUMS', sums)
        if unsafe:
            archive.writestr('../outside.bin', b'bad')
    files = {f'Ham-Pilot-v{version}-firmware.zip': stream.getvalue(),
             f'Ham-Pilot-v{version}-relink.zip': b'fixture objects',
             f'Ham-Pilot-v{version}-third-party-source.zip': b'fixture sources',
             'arduino-esp32-3.3.12.zip': b'fixture core', 'esp-idf-v5.5.5.zip': b'fixture sdk'}
    files['SHA256SUMS-release.txt'] = ''.join(hashlib.sha256(value).hexdigest() + '  ' + name + '\n'
                                             for name, value in files.items()).encode()
    release = {'id': 123, 'tag_name': 'v' + version, 'draft': False, 'prerelease': False,
               'published_at': '2026-10-17T00:00:00Z', 'assets': [
                   {'name': name, 'browser_download_url': f'https://github.com/{publisher.REPO}/releases/download/v{version}/{name}'}
                   for name in files]}

    def fetch(url, limit):
        return json.dumps(release).encode() if url.endswith('/latest') else files[url.rsplit('/', 1)[1]]
    return release, files, fetch


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.state = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_valid_release_and_idempotence(self):
        _, _, fetch = fixture()
        publisher.sync(self.state, fetch)
        target = self.state / 'releases/v0.3.5'
        self.assertEqual((self.state / 'current').resolve(), target)
        manifest = json.loads((target / 'manifest.json').read_text())
        self.assertTrue(manifest['new_install_prompt_erase'])
        self.assertEqual(manifest['builds'][0]['parts'][-1], {
            'path': '/downloads/ham-pilot/releases/v0.3.5/ham-pilot.bin', 'offset': 65536})
        publisher.sync(self.state, fetch)

    def test_bad_checksum_retains_current(self):
        _, _, fetch = fixture()
        publisher.sync(self.state, fetch)
        _, files, bad = fixture('0.3.6')
        files['Ham-Pilot-v0.3.6-firmware.zip'] += b'corrupt'
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            publisher.sync(self.state, bad)
        self.assertEqual((self.state / 'current').resolve().name, 'v0.3.5')

    def test_draft_and_prerelease_cannot_publish(self):
        for flag in ('draft', 'prerelease'):
            release, _, fetch = fixture()
            release[flag] = True
            with self.assertRaisesRegex(ValueError, 'stable'):
                publisher.sync(self.state, fetch)
        self.assertFalse((self.state / 'current').exists())

    def test_zip_traversal_cannot_publish(self):
        _, _, fetch = fixture(unsafe=True)
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            publisher.sync(self.state, fetch)
        self.assertFalse((self.state / 'current').exists())
        self.assertFalse((self.state.parent / 'outside.bin').exists())

    def test_interrupted_activation_can_resume(self):
        _, _, fetch = fixture()
        with patch.object(publisher, 'activate', side_effect=OSError('interrupted')):
            with self.assertRaises(OSError):
                publisher.sync(self.state, fetch)
        self.assertFalse((self.state / 'current').exists())
        publisher.sync(self.state, fetch)
        self.assertEqual((self.state / 'current').resolve().name, 'v0.3.5')

    def test_update_keeps_old_manifest_images_available(self):
        publisher.sync(self.state, fixture()[2])
        publisher.sync(self.state, fixture('0.3.6')[2])
        self.assertEqual((self.state / 'current').resolve().name, 'v0.3.6')
        self.assertTrue((self.state / 'releases/v0.3.5/ham-pilot.bin').is_file())
        publisher.sync(self.state, fixture()[2])
        self.assertEqual((self.state / 'current').resolve().name, 'v0.3.6')


if __name__ == '__main__':
    unittest.main()
