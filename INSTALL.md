# Installing Ham Pilot v0.3.5

## Supported hardware

Diymore 2.8-inch ESP32-32E, 4 MB flash, ILI9341/ILI9341V LCD and XPT2046 touch.
The firmware uses landscape 320 x 240. USB must support data as well as power.
Pin assignments: LCD CS15/DC2/SCK14/MOSI13/MISO12/backlight21; touch
CS33/SCK25/MOSI32/MISO39. No additional wiring is needed on this supported board.
No VHF functions or CAT connection are included.

## Windows flashing

1. Install Python 3 and, if Windows needs it, the board vendor's CH340 USB driver.
2. Download and extract Ham-Pilot-v0.3.5-firmware.zip from Releases.
3. In a terminal install the uploader: `py -m pip install esptool==5.3.1`.
4. Find the board's COM port in Windows Device Manager. Close software using it.
5. In PowerShell, from the extracted folder, run `./Flash-HamPilot.ps1 -Port COM6`,
   replacing COM6 with your board's port. Use your normal PowerShell script policy;
   alternatively run the manual command below.

The script checks the four firmware files against SHA256SUMS before writing.
It does not write an NVS/settings image or a filesystem image and does not erase
the whole flash. On an existing Ham Pilot board the saved profile/calibration
are retained. If replacing unrelated firmware, keep a private backup first.

## Manual flashing / Linux / macOS

Install Python and esptool 5.3.1, then use the correct serial port:

```text
python -m esptool --chip esp32 --port YOUR_PORT --baud 460800 --before default-reset --after hard-reset write-flash --flash-mode dio --flash-freq 80m --flash-size 4MB 0x1000 bootloader.bin 0x8000 partitions.bin 0xe000 boot_app0.bin 0x10000 ham-pilot.bin
```

Do not substitute the application binary at address zero. Do not use a full
device backup as a public firmware image. If connecting fails, follow the board
vendor's BOOT/RESET procedure and retry, or reduce the baud rate to 115200.

## First start

The Ham Pilot title appears briefly. A new board asks for three touch targets.
Tap and release each one, then enter your station and Wi-Fi in Settings and Save.
On the Wi-Fi page or password keyboard, tap Show to check the password.
Editing starts with the existing value; tap Done, Back, then Save settings &
restart to apply corrections. Calls, locator and place are blank on fresh installations. UK time zone and UK
cluster reporting prefixes are initial defaults; change them for your location.
The on-device Web setup page gives the address and device-specific login.

Let the board connect and accumulate live reports. Stored schedules and outlook
may be absent until their first successful downloads. No reports is not a closed
band. The clock obtains internet time. The PC may then be disconnected.

Settings > Reset can prepare another profile; profile reset retains Wi-Fi and
touch calibration, while Reset everything also clears Wi-Fi when saved. A saved
reset is deliberate; normal firmware updating does not reset your station.
