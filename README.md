# Raspberry Pi Network Monitor

A simple network monitoring tool with a web dashboard, authentication, and relay control.

## Features

- Periodically pings a configurable list of IPs/hosts
- Web dashboard to view status, add/remove devices, change intervals
- Login-protected access
- Relay output (GPIO) triggered if a device goes offline for set intervals
- Easy to use and run on Raspberry Pi

## Setup

1. **Clone the repo**  
   `git clone https://github.com/joshuahuggard96/network-monitor-pi.git`

2. **Install dependencies**  
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run the app**  
   ```bash
   python3 app.py
   ```
   The dashboard will be available at `http://raspberrypi.local:5000` or at your Pi's IP address.

4. **Login**  
   Default user: `admin`  
   Default pass: `admin`  
   (Change password in `config.json` or via the Settings tab for security!)

5. **Configure GPIO relay**  
   - Connect your relay to the GPIO pin (default: 17).
   - Change pin in `config.json` if needed.

## Customization

- Add devices via dashboard or by editing `devices.json`
- Change ping interval and offline threshold in dashboard or in `config.json`
- Set relay for devices (checkbox)
- Device list is stored in `devices.json`
- All other settings and users are stored in `config.json`

## Notes

This project is designed to run only on Raspberry Pi OS with GPIO support.

## Security

Change the default password in `config.json` or via the Settings tab after first login.
Use a strong password!

## License

MIT
