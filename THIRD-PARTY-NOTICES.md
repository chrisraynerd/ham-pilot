# Third-party notices and corresponding materials

Ham Pilot's noncommercial licence applies to its own application, not to the
components below. Original licences and mandatory rights remain applicable.

| Component | Version / source | Terms and credit |
|---|---|---|
| ESP32 Arduino core and bundled Arduino libraries | 3.3.12 | LGPL-2.1-or-later; Arduino Team, Espressif Systems and other credited contributors. Complete corresponding source is attached to the release. |
| ESP-IDF / SDK | 5.5.5, IDF b774170ff46; lib-builder 6671d0b | Apache-2.0 and component-specific licences; Espressif and other authors. Licence texts are under licences/esp-idf. Upstream SDK source is attached for reference; bundled submodules and Wi-Fi binaries retain their upstream terms. |
| Adafruit GFX | 1.12.6 | BSD-2-Clause, Copyright 2012 Adafruit Industries. No GNU FreeFont-derived font is linked into this release. |
| Adafruit ILI9341 | 1.6.4 | BSD; Limor Fried / Adafruit Industries; original notice reproduced. |
| Adafruit BusIO | 1.17.4 | MIT; Adafruit Industries and contributors. |
| XPT2046_Touchscreen | 1.4 | MIT; Copyright 2015 Paul Stoffregen. |
| ArduinoJson | 7.4.3 | MIT; Benoit Blanchon. |
| PubSubClient | 2.8 | MIT; Copyright 2008-2020 Nicholas O'Leary. |
| Noto Sans compact font | 16-pixel, weight 400, width 95, ASCII bitmap conversion | SIL OFL 1.1; Copyright 2022 The Noto Project Authors. Font data remains OFL, including the modified bitmap form. Original font/source and licence accompany the third-party source asset. |
| Callsign/country tables | AD1C cty.csv, retrieved 14 October 2026 | Jim Reisert AD1C; MIT permission notice reproduced in licences/. Prefix assignments can be ambiguous or change. |
| World outline | Natural Earth 1:110m land, reduced to a bitmap | Public domain; https://www.naturalearthdata.com/about/terms-of-use/ |

Full licence texts are in [licences/](licences/). Relevant Arduino library and
third-party source archives, compiled application/library objects, core archive,
link manifest and a working relinking script accompany the same release. You may
modify LGPL-covered libraries and relink with the application objects; debugging
such modifications by reverse engineering is permitted. No additional Ham Pilot
restriction overrides those LGPL rights. No application source is included.

The relinking package contains instructions to rebuild the Arduino libraries and
replace their objects/core archive. Its manifest identifies the board settings
and toolchain versions used. The original library sources are unmodified.

## Live services and data attribution

- PSK Reporter: Philip Gladstone N1DQ; MQTT feed: Tom M0LTE, https://www.mqtt.pskreporter.info/ .
- Conventional DX cluster: https://dxc.hamserve.uk/ ; regional reporting-station filter.
- HF outlook and indices: N0NBH / HAMQSL.com, https://www.hamqsl.com/solar.html . Underlying data credits NOAA SWPC / Space Weather Canada. General ratings are not local measurements.
- DXpeditions: G7RDX / Bill Feidt NG3K; https://g7rdx.co.uk/dxpedition-calendar/ . Scheduled operations are not proof of current reception.
- Contests: ContestClock / W4GGJ, https://contestclock.com/data ; calendar data CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ . Ham Pilot filters and shortens schedules; provider/sponsor information remains authoritative. Live calendar records are downloaded on the user's device, not bundled in this release.
- Approximate solar geometry: NOAA calculation details, https://gml.noaa.gov/grad/solcalc/calcdetails.html .
- Country data: https://www.country-files.com/cty/cty.csv . The standard permission notice is also distributed with WSJT-X's cty.dat copyright materials.

Core source: https://github.com/espressif/arduino-esp32/tree/3.3.12 .
SDK source: https://github.com/espressif/esp-idf/tree/v5.5.5 .
Noto source: https://github.com/notofonts/latin-greek-cyrillic .
