# Network Monitor Pi

A Python-based network monitoring tool with a Flask web dashboard and socket relay output. It continuously monitors device connectivity and sends status updates to a relay controller via TCP socket.

## Features

- **Web Dashboard**: Real-time HTML interface with HTMX auto-refreshing showing network status
- **Device Monitoring**: Track multiple devices (Router, DNS servers, connected devices) with online/offline status
- **Continuous Background Monitoring**: Threaded monitoring without blocking main application
- **Socket Relay Output**: Sends network status to external relay controller via TCP socket
- **Real-Time Updates**: Dashboard refreshes automatically every 500ms
- **Device Management**: Easy configuration of devices in `devices.py`
- **Responsive Design**: Clean, simple interface showing relay status and device states
- **Thread-Safe Operations**: Safe concurrent access to monitoring results

## Project Structure

```
network-monitor-pi/
├── app.py              # Main Flask application with HTMX dashboard
├── devices.py          # Device list configuration
├── templates/
│   └── index.html      # Web dashboard interface (uses HTMX)
├── static/
│   ├── css/
│   │   └── style.css   # Dashboard styling
│   └── htmx/
│       └── htmx-1.9.12.js  # HTMX library for dynamic updates
├── README.md           # This file
└── requirements.txt    # Python dependencies
```

## Requirements

- Python 3.6+
- Flask - Web framework for dashboard
- ping3 - ICMP ping functionality for device monitoring
- Network connectivity for pinging devices
- TCP socket access for relay output

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/joshuahuggard96/network-monitor-pi.git
   cd network-monitor-pi
   ```

2. **Install Python dependencies**
   ```bash
   # For Windows
   pip install -r requirements.txt

   # For Linux/WSL
   pip3 install -r requirements.txt
   ```
   Or install manually:
   ```bash
   pip install flask ping3
   ```

3. **Configure devices** (optional)
   Edit `devices.py` to add/modify devices to monitor:
   ```python
   device_list = {
       "Router": {
           "ip": "10.5.32.1",
           "status": None,
           "last_online": None
       },
       # Add more devices here
   }
   ```

4. **Configure socket relay output** (optional)
   Edit `app.py` to change relay host/port:
   ```python
   Host = '127.0.0.1'  # Relay controller IP
   Port = 7000          # Relay controller port
   ```

## Usage

### Starting the Application
```bash
# Windows
python app.py

# Linux/macOS
python3 app.py
```

The application will:
1. Start the Flask web server on `http://localhost:5000`
2. Begin monitoring devices in `devices.py`
3. Send relay status to the configured socket server
4. Display monitoring activity in the console

### Web Dashboard Access
- **Local access**: `http://localhost:5000`
- **Network access**: `http://YOUR_COMPUTER_IP:5000`
- Dashboard auto-refreshes every 500ms using HTMX
- Shows relay status (ON/OFF) and individual device status

### API Endpoints
- **Status JSON**: `http://localhost:5000/api/status`
  - Returns: `output_status`, `timestamp`, `device_list`
- **Status HTML**: `http://localhost:5000/api/status-html`
  - Returns: HTML fragment with current status (used by HTMX)

## Configuration

### Device Configuration
Edit `devices.py` to monitor different devices:

```python
device_list = {
    "Router": {
        "ip": "10.5.32.1",
        "status": None,
        "last_online": None
    },
    "Google DNS": {
        "ip": "8.8.8.8",
        "status": None,
        "last_online": None
    },
    "Iphone": {
        "ip": "10.5.33.222",
        "status": None,
        "last_online": None
    }
}
```

### Application Settings
Edit `app.py` to customize monitoring and relay output:

```python
ping_interval = 0.5        # Seconds between ping cycles
Host = '127.0.0.1'        # Relay controller IP address
Port = 7000                # Relay controller port
```

### How It Works
1. **Device Monitoring**: Pings each device in `device_list` every `ping_interval` seconds
2. **Status Tracking**: Updates device status (True/False) and last online timestamp
3. **Relay Logic**: Sets `output_status` to True if ALL devices are online
4. **Socket Output**: Sends `output_status` to relay controller via TCP socket
5. **Web Dashboard**: Displays current relay status and device details via HTMX

## Platform-Specific Notes

### Windows
- Uses `-n` parameter for ping count
- Works with Windows Command Prompt or PowerShell
- No special permissions required for system ping

### Linux/WSL
- Uses `-c` parameter for ping count  
- May require elevated permissions for ICMP packets
- Fallback to system ping if library fails

### Cross-Platform Compatibility
The code automatically detects the operating system and uses appropriate ping parameters.

## Application Architecture

### Threading Model
The application uses three concurrent threads:
1. **Ping Thread** - Continuously monitors device connectivity
2. **Socket Thread** - Sends relay status to external controller
3. **Flask Thread** - Serves web dashboard and API endpoints

### Device Status Handling
- Device status is stored in a shared dictionary in `devices.py`
- Status is updated in real-time as pings complete
- Last online timestamp is recorded when device transitions to online state
- `output_status` reflects overall network health (True = all devices online)

### Web Communication
- **HTMX** handles dynamic updates without page refresh
- Dashboard pulls status every 500ms via `/api/status-html` endpoint
- Changes appear instantly without user interaction
- Responsive design works on desktop and mobile devices

## API Response Examples

### `/api/status` (JSON)
```json
{
  "output_status": true,
  "timestamp": 1729605938.123,
  "device_list": {
    "Router": {
      "ip": "10.5.32.1",
      "status": true,
      "last_online": "22 Oct 2025 16:05:30"
    },
    "Google DNS": {
      "ip": "8.8.8.8",
      "status": true,
      "last_online": "22 Oct 2025 16:05:28"
    },
    "Iphone": {
      "ip": "10.5.33.222",
      "status": false,
      "last_online": null
    }
  }
}
```

### `/api/status-html` (HTML Fragment)
```html
<div class="status online">Relay Status ON</div>
<div id="ip-list"><h3>Device Status:</h3>
    <div class="ip-item ip-online">
        <strong>Router</strong>
        <span class="status-indicator">Online</span>
    </div>
    <div class="ip-item ip-online">
        <strong>Google DNS</strong>
        <span class="status-indicator">Online</span>
    </div>
    <div class="ip-item ip-offline">
        <strong>Iphone</strong>
        <span class="status-indicator">Offline</span>
    </div>
</div>
```

## Troubleshooting

### Permission Errors (Linux/WSL)
```bash
# Grant ping capabilities
sudo setcap cap_net_raw+ep $(which python3)

# Or run with elevated privileges
sudo python3 app.py
```

### Module Not Found
```bash
# Install missing dependencies
pip install -r requirements.txt
# Or manually:
pip install flask ping3
```

### Web Dashboard Not Loading
- Verify Flask is running: Check console for "web server accessable on Localhost:5000"
- Verify HTMX is loading: Check browser console for JavaScript errors
- Check firewall settings if accessing from other devices
- Try `http://127.0.0.1:5000` instead of `localhost:5000`

### Devices Not Showing as Online
- Verify devices are reachable: `ping 10.5.32.1` (or your device IP)
- Check firewall settings blocking ICMP packets
- Verify device IPs are correct in `devices.py`
- Ensure network adapter is connected and devices are on the same network

### Socket Relay Not Connecting
- Verify relay controller is running and accessible at configured `Host` and `Port`
- Check firewall allows outbound connections to relay port
- Verify no other application is using the relay port
- Check console for socket connection errors

### Dashboard Shows "Checking" Status
- This is normal for devices that haven't responded yet
- Wait for the next ping cycle (every `ping_interval` seconds)
- Check device connectivity and ping response times

## Development

### Understanding the Code Structure

**app.py** - Main application entry point:
- Flask app setup and route handlers
- Ping monitoring thread
- Socket relay output thread
- API endpoints for status retrieval

**devices.py** - Device configuration:
- Central location for all monitored devices
- Device IP addresses and status tracking
- Last online timestamps

**templates/index.html** - Web interface:
- HTMX configuration for auto-refresh
- Loading state handling
- Responsive layout

**static/css/style.css** - Styling:
- Color-coded status indicators
- Responsive design for mobile/desktop
- Status card styling

### Adding New Devices
1. Open `devices.py`
2. Add new entry to `device_list`:
   ```python
   "Device Name": {
       "ip": "192.168.x.x",
       "status": None,
       "last_online": None
   }
   ```
3. Restart the application

### Modifying Monitoring Behavior
Edit `app.py` variables:
- `ping_interval` - How often to ping (in seconds)
- `Host` / `Port` - Relay controller address
- Modify `ping_device()` function for custom ping logic
- Modify `Send_output()` for custom relay messaging

### Contributing
- Follow Python PEP 8 style guidelines
- Add comments for complex logic
- Test on both Windows and Linux
- Update README documentation as needed

## Future Enhancements

- [ ] Email/SMS notifications when network status changes
- [ ] Historical data logging and charts
- [ ] Raspberry Pi GPIO integration (LED indicators)
- [ ] Configuration file support (YAML/JSON)
- [ ] Network latency tracking and graphs
- [ ] Custom alert thresholds per device
- [ ] Webhook notifications
- [ ] Database integration for historical data
- [ ] Device group management
- [ ] Performance metrics and uptime tracking

## License

MIT License - feel free to modify and distribute as needed.

## Author

**Joshua Huggard** - [joshuahuggard96](https://github.com/joshuahuggard96)

Project Link: [https://github.com/joshuahuggard96/network-monitor-pi](https://github.com/joshuahuggard96/network-monitor-pi)
