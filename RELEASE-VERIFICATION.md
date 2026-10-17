# v0.3.5 verification - 17 October 2026

- Tested on the supported 4 MB ESP32-32E / ILI9341 / XPT2046 CYD.
- First browser installation of the v0.3.4 candidate succeeded on a fresh board;
  blank station defaults and setup were verified. The user confirmed the physical
  Settings > Wi-Fi button opens the correct page.
- v0.3.5 was installed by USB with written hashes verified. Station settings and
  touch calibration survived. After correcting the password with the new controls,
  Wi-Fi, internet time, PSK, cluster and HamQSL worked; the user confirmed full
  operation. Real populated PSK and six-row DX layouts were inspected.
- Application SHA256:
  `64cf5905b32c29b0b4b700f1073c8f74468d7964928043cb3aa818db3ecfdec4`.
  The supplied relinking objects reproduce that exact image. Firmware package
  checksums and uploader VerifyOnly checks passed.
- The public v0.3.5 release includes firmware, matching objects/relinking tools,
  third-party sources/notices and core/SDK source archives. Application source,
  saved settings and device backups are excluded.
- Six updater integration tests passed on the Linux web server: successful
  publication/idempotence, corrupt-download retention, draft/prerelease rejection,
  unsafe archive rejection, interrupted-activation recovery, and preservation of
  earlier version images. Real published GitHub assets were then downloaded,
  verified and activated by the unprivileged service. Its five-minute timer is
  enabled and a subsequent check correctly reported the installer current.
- The website's installer now points to the automatically maintained latest
  manifest, with immutable versioned image URLs. Live version labels and loading
  of the Connect & install control were verified in the browser. All 313 hosted
  website checks passed. A further physical USB flash through the website was
  not performed for v0.3.5; the identical image was already running on the device.
