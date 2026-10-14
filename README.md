# Ham Pilot

**An HF propagation, DX spotting and shack clock display for the Diymore 2.8-inch ESP32-32E touchscreen.**

By **G1CEC - Chris Raynerd**. Copyright 2026.

**Release status:** The first firmware package is prepared as a draft. Hardware verification of a reported Settings/Wi-Fi touch issue is pending USB reconnection. No public firmware download has been published yet.

## Download and install

Download **Ham-Pilot-v0.3.4-firmware.zip** from [Releases](https://github.com/chrisraynerd/ham-pilot/releases).
Read [INSTALL.md](INSTALL.md) before flashing. The supported board has a 320 x 240
ILI9341 display, XPT2046 resistive touch and 4 MB ESP32 flash. Similar-looking
boards with other display or touch controllers may need different firmware.

## What it shows

- PSK Propagation from your chosen location: recent nearby receiver reports by HF band.
- Six-row DX spots, prominent countries, coloured modes and tap-to-open details.
- Observed propagation paths with day/night shading and the Sun's overhead position.
- UTC/local clock, sunrise/sunset, and selected major contests now/next.
- HamQSL HF day/night outlook with SFI and K.
- Info menu with DXpedition and contest calendars, plus source/licence credits.
- On-device and authenticated local web settings; independent page durations.

It needs **2.4 GHz Wi-Fi and internet access**, but no radio/CAT connection or
permanently connected computer. HF bands are 80, 40, 30, 20, 17, 15, 12 and 10 m.
Nearby PSK reception is evidence from those receivers, not a guarantee at your
antenna. A cluster spot is an operator's report. No reports does not mean closed.

## First use and controls

Fresh installations have blank station fields. Calibrate touch, then enter your
callsign, home Maidenhead locator, place and Wi-Fi in Settings. You can also join
HAM-Display-Setup using the password shown on the device, open http://192.168.4.1,
and sign in as `ham` using that same device password. Saved profiles remain on
the device during normal updates. Choose your local time zone and reporting
station filters; the initial time zone and cluster filter are UK-oriented.

Tap the bottom-left clock for Settings; tap Info for calendars. Tap a DX row for
details and Back to return. Tap a page header/blank area to advance. Hold roughly
one second to pause/resume, or four seconds for Settings. Each page can have its
own duration. Browsing Info or details pauses automatic rotation temporarily.

## Use, sharing and source

You may build your own device and use the firmware noncommercially under
[LICENSE.md](LICENSE.md). **Commercial use of Ham Pilot's application code,
including selling devices running it, requires separate permission.** Third-party
rights remain intact; see [NOTICE.md](NOTICE.md).

This is the public **firmware and documentation** repository. The editable Ham
Pilot application is developed privately. Release assets include the required
library sources/notices and application object files/instructions for LGPL
relinking. Those are not an editable Ham Pilot application project.

ADIF import and new-DXCC alerts are **planned, not included in v0.3.4**.
Report bugs through Issues with the firmware version and board details. Do not
attach Wi-Fi passwords, full flash backups, private logs or device login details.

Data/service credits are in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
