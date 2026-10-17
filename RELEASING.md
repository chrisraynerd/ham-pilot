# Publishing firmware and updating the website

The editable Ham Pilot application stays in its private repository. This public
repository holds documentation, release assets and the website updater only.

1. Build and test the firmware on the supported CYD. Verify that existing station,
   Wi-Fi and touch settings survive an ordinary update. A build alone is not a
   hardware test.
2. Prepare the explicit four-image firmware ZIP, matching relinking objects,
   third-party library sources/notices and corresponding core/SDK archives.
   Verify checksums, the installer and relinking before upload. Exclude application
   source, merged/read-back images, credentials and user logs.
3. Create a **draft** public GitHub release tagged `vMAJOR.MINOR.PATCH`. Attach:
   `Ham-Pilot-vVERSION-firmware.zip`, `Ham-Pilot-vVERSION-relink.zip`,
   `Ham-Pilot-vVERSION-third-party-source.zip`, the matching
   `arduino-esp32-VERSION.zip`, `esp-idf-vVERSION.zip`, and
   `SHA256SUMS-release.txt` covering all five ZIP archives.
4. Review the complete draft and publish it as a stable release when approved.
   Publishing is the website deployment approval. Drafts and prereleases do not
   update the installer.

The Raynerd web server checks this repository's GitHub **latest stable release**
every five minutes (plus a small scheduling delay), even when Chris's PC is off.
It verifies every archive checksum, the four firmware checksums, ESP32 flash
headers, image sizes and the saved-settings partition layout. Only the explicit
firmware files, instructions and licence notices are extracted.

The complete version is installed before an atomic change of the current-version
link. Failed downloads, malformed packages and checksum failures retain the
working installer. Interrupted activation can resume. Versioned firmware URLs
remain available, so a release published during someone else's installation
cannot mix images from two versions. Automatic downgrades are refused.

The website reads `/downloads/ham-pilot/latest/manifest.json` and
`/downloads/ham-pilot/latest/release.json`; its version labels and manual downloads
follow the same release. Individual images use immutable versioned URLs. No
private repository credentials or SSH keys are stored in GitHub for this process.
This updates the installer for visitors; existing CYDs update only when their
owners choose to install firmware.

Server maintenance: `systemctl status ham-pilot-sync.timer`,
`systemctl start ham-pilot-sync.service`, and
`journalctl -u ham-pilot-sync.service`. The updater runs as an unprivileged user;
the website's normal HTML release and the firmware storage are separate.

Updater implementation: `tools/sync_website_release.py`. Run its tests on Linux:
`cd tools && python3 -m unittest -v test_sync_website_release`.
