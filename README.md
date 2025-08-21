# Network Monitor Pi

A professional Python-based network monitoring application that continuously pings network devices and provides real-time status updates through a modern web interface. Built with Flask and designed for reliability and ease of use.

## 🚀 Features

- **Real-Time Web Dashboard**: Modern responsive web interface with live status updates
- **Device Management**: Add/remove devices dynamically through the web interface
- **Individual Device Monitoring**: Track each device separately with online/offline/checking status
- **Persistent Configuration**: Device list automatically saved to file
- **Thread-Safe Operations**: Safe concurrent monitoring and web requests
- **Professional API**: RESTful endpoints for integration with other systems
- **Cross-Platform Support**: Works on Windows, Linux, macOS, and Raspberry Pi
- **Input Validation**: IP address format validation and duplicate prevention
- **Comprehensive Logging**: Professional logging with configurable levels
- **Auto-Refresh**: Dashboard updates every 500ms for real-time monitoring

## 🏗️ Project Structure

```
network-monitor-pi/
├── app.py                 # Main application (current version)
├── devices.py            # Device configuration file (auto-generated)
├── templates/
│   └── index.html        # Web dashboard template
├── static/
│   ├── css/
│   │   └── style.css     # Dashboard styling
│   └── js/
│       └── app.js        # Frontend JavaScript
├── legacy/               # Previous versions
├── .gitignore           # Git ignore rules
├── README.md            # This documentation
└── requirements.txt     # Python dependencies
```

## 📋 Requirements

- Python 3.7+
- ping3 library for ICMP ping functionality
- Flask for web framework
- Network connectivity for device monitoring

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/network-monitor-pi.git
   cd network-monitor-pi
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or manually install:
   ```bash
   pip install ping3 flask
   ```

3. **Linux/Raspberry Pi Setup** (if needed)
   ```bash
   # Grant ping capabilities to Python (recommended)
   sudo setcap cap_net_raw+ep $(which python3)
   
   # Alternative: run with sudo if permission errors occur
   sudo python3 app.py
   ```

## 🚀 Usage

### Starting the Application
```bash
python3 app.py
```

The application will:
- Start the monitoring thread
- Launch the web server on port 5000
- Begin pinging configured devices every 500ms
- Display status information in the console

### Web Dashboard Access
- **Local access**: `http://localhost:5000`
- **Network access**: `http://YOUR_COMPUTER_IP:5000`
- **Raspberry Pi**: `http://raspberrypi.local:5000`

### Web Interface Features

#### Main Dashboard
- **Overall Status**: Shows "Relay Status ON/OFF" based on all devices
- **Device List**: Individual cards for each monitored device
- **Status Indicators**: 
  - 🟢 Online - Device responding to pings
  - 🔴 Offline - Device not responding
  - 🟡 Checking - Status being determined
- **Real-time Updates**: Auto-refresh every 500ms

#### Device Management
- **Add Device Form**:
  - Device Name field (e.g., "Router", "Phone")
  - IP Address field with validation
  - Real-time validation feedback
- **Remove Devices**: Each device has a "Remove" button with confirmation
- **Persistent Storage**: Changes automatically saved to `devices.py`

## ⚙️ Configuration

### Default Configuration
The application starts with these default devices in `devices.py`:
```python
device_list = {
    "Router": {
        "ip": "192.168.0.1",
        "status": None,
        "last_online": None
    },
    "google dns": {
        "ip": "8.8.8.8",
        "status": None,
        "last_online": None
    },
    "Iphone": {
        "ip": "192.168.0.140",
        "status": None,
        "last_online": None
    }
}
```

### Application Settings
Edit the constants at the top of `app.py`:
```python
PING_INTERVAL = 0.5  # Seconds between ping cycles
HOST = '0.0.0.0'     # Listen on all interfaces
PORT = 5000          # Web server port
```

## 🔌 API Endpoints

### GET `/api/status`
Returns current network status and device information.

**Response:**
```json
{
  "output_status": true,
  "timestamp": 1692014338.123,
  "device_list": {
    "Router": {
      "ip": "192.168.0.1",
      "status": true,
      "last_online": "2025-08-21 14:30:15"
    },
    "google dns": {
      "ip": "8.8.8.8",
      "status": true,
      "last_online": "2025-08-21 14:30:15"
    }
  }
}
```

### POST `/api/add-device`
Add a new device to monitor.

**Request:**
```json
{
  "name": "New Router",
  "ip": "192.168.1.1"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Device \"New Router\" added successfully"
}
```

### POST `/api/remove-device`
Remove a device from monitoring.

**Request:**
```json
{
  "name": "Old Device"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Device \"Old Device\" removed successfully"
}
```

## 🖥️ Platform Support

### Windows
- Uses standard ping functionality
- No special permissions required
- Works with Command Prompt or PowerShell

### Linux/Ubuntu/Debian
- Requires ICMP permissions for optimal performance
- Systemd service compatible
- Supports headless operation

### Raspberry Pi
- Perfect for always-on monitoring
- Low resource usage
- Can integrate with GPIO for physical indicators

### macOS
- Full compatibility with macOS ping utilities
- Works with both Intel and Apple Silicon Macs

## 🔧 Advanced Usage

### Running as a Service (Linux/Raspberry Pi)
Create a systemd service file:
```bash
sudo nano /etc/systemd/system/network-monitor.service
```

```ini
[Unit]
Description=Network Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/network-monitor-pi
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable network-monitor.service
sudo systemctl start network-monitor.service
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
```

## 🐛 Troubleshooting

### Common Issues

**Permission Errors (Linux/macOS)**
```bash
# Solution 1: Grant capabilities
sudo setcap cap_net_raw+ep $(which python3)

# Solution 2: Run with sudo
sudo python3 app.py
```

**Module Not Found**
```bash
pip install ping3 flask
# or for Python 3 specifically
pip3 install ping3 flask
```

**Web Dashboard Not Loading**
- Verify the server is running: Look for "Web interface available at http://localhost:5000"
- Check firewall settings
- Try `http://127.0.0.1:5000` instead of `localhost`
- Ensure port 5000 is not in use by another application

**Devices Not Responding**
- Verify IP addresses are correct and reachable
- Test manual ping: `ping 8.8.8.8`
- Check network connectivity
- Verify firewall allows ICMP packets

**File Permission Errors**
```bash
# Ensure write permissions for device configuration
chmod 664 devices.py
```

### Debug Mode
Enable debug logging by changing the logging level in `app.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Monitoring Best Practices

### Device Selection
- **Gateway/Router**: Always monitor your network gateway
- **Critical Services**: Include essential servers and services
- **External Connectivity**: Add public DNS servers (8.8.8.8, 1.1.1.1)
- **Local Devices**: Monitor important local devices

### Ping Interval Considerations
- **Fast Response**: 0.5s interval for real-time monitoring
- **Reduced Load**: 5-10s interval for less network traffic
- **Battery Devices**: Longer intervals for mobile devices

### Network Design
- Place monitor on reliable network segment
- Consider multiple monitoring points for redundancy
- Monitor both internal and external connectivity

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-amazing-feature`
3. Install development dependencies: `pip install -r requirements.txt`
4. Make your changes
5. Test on multiple platforms
6. Update documentation
7. Submit a pull request

### Code Style
- Follow Python PEP 8 style guidelines
- Add comprehensive docstrings
- Include error handling
- Write unit tests for new features
- Update README for significant changes

### Testing
```bash
# Run basic functionality test
python3 -c "from app import ping_device; print('Import successful')"

# Test web interface
curl http://localhost:5000/api/status
```

## 📈 Future Enhancements

- [ ] Historical data logging and visualization
- [ ] Email/SMS/Webhook notifications
- [ ] Network latency tracking and graphs
- [ ] Multiple monitoring profiles
- [ ] Configuration file import/export
- [ ] Raspberry Pi GPIO integration
- [ ] Mobile-responsive design improvements
- [ ] Docker Compose deployment
- [ ] Prometheus metrics export
- [ ] Custom alert thresholds per device
- [ ] Network topology discovery
- [ ] Performance metrics dashboard

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Joshua Huggard** - [joshuahuggard96](https://github.com/joshuahuggard96)

## 🔗 Links

- **GitHub Repository**: [https://github.com/joshuahuggard96/network-monitor-pi](https://github.com/joshuahuggard96/network-monitor-pi)
- **Issues**: [Report bugs or request features](https://github.com/joshuahuggard96/network-monitor-pi/issues)
- **Wiki**: [Additional documentation and examples](https://github.com/joshuahuggard96/network-monitor-pi/wiki)

## ⭐ Show Your Support

Give a ⭐️ if this project helped you monitor your network effectively!

---

**Built with ❤️ for reliable network monitoring**
