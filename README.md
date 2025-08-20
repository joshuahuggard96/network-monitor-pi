# Network Monitor

A Python-based network monitoring tool that continuously pings IP addresses and provides real-time status updates. Features both command-line interface, background monitoring, and a web dashboard for visual monitoring.

## Features

- **Web Dashboard**: Real-time HTML interface showing network status
- **Individual IP Monitoring**: Track each IP address separately with online/offline status
- **Continuous Background Monitoring**: Threaded monitoring without blocking main application
- **Multiple Ping Methods**: Support for both `ping3` library and system ping fallback
- **Cross-Platform Support**: Works on Windows, Linux, and WSL
- **Real-Time Updates**: Live monitoring with configurable intervals
- **Flexible IP Management**: Easy addition/removal of IP addresses to monitor
- **Clean Logging**: Optional request log suppression for cleaner console output
- **Thread-Safe Operations**: Safe concurrent access to monitoring results

## Project Structure

```
network-monitor-pi/
├── app.py              # Original subprocess-based implementation
├── app_v2.py           # Enhanced version with threading support
├── app_v0.3.py         # Latest version with Flask web interface
├── app_v0.4.py         # Current main application
├── templates/
│   └── index.html      # Web dashboard interface
├── legacy/             # Previous versions
├── README.md           # This file
└── requirements.txt    # Python dependencies
```

## Requirements

- Python 3.6+
- ping3 library for ICMP ping functionality
- Flask for web dashboard
- Network connectivity for testing

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/joshuahuggard96/network-monitor-pi.git
   cd network-monitor-pi
   ```

2. **Install Python dependencies**
   ```bash
   # For Windows
   pip install ping3 flask
   
   # For Linux/WSL
   pip3 install ping3 flask
   ```

3. **Linux/WSL Permission Setup** (if needed)
   ```bash
   # Grant ping capabilities to Python (optional)
   sudo setcap cap_net_raw+ep $(which python3)
   
   # Or run with sudo if permission errors occur
   sudo python3 app_v0.4.py
   ```

## Usage

### Web Dashboard (Recommended)
```bash
python3 app_v0.4.py
```
- Open your browser to `http://localhost:5000`
- Real-time web dashboard showing:
  - Overall network status
  - Individual IP address status (Online/Offline)
  - Last update timestamp
  - Auto-refreshing every 2 seconds

### Command Line Versions
```bash
# Basic version with subprocess
python3 app.py

# Threading version with background monitoring
python3 app_v2.py

# Flask version with API endpoints
python3 app_v0.3.py
```

### Web Access
- **Local access**: `http://localhost:5000`
- **Network access**: `http://YOUR_COMPUTER_IP:5000`
- **API endpoint**: `http://localhost:5000/api/status` (JSON response)

## Configuration

Edit the variables at the top of `app_v0.4.py` to customize monitoring:

```python
ping_interval = 5           # Seconds between ping cycles
times_to_check = 2         # Successful pings needed for "online" status
ip_address_list = [        # IPs to monitor
    "192.168.16.1",        # Router/Gateway  
    "8.8.8.8",             # Google DNS
    "1.1.1.1"              # Cloudflare DNS
]
```

### Web Dashboard Features
- **Real-time Updates**: Dashboard refreshes automatically every 2 seconds
- **Individual IP Status**: Each IP shows as Online ✅ or Offline ❌
- **Overall Status**: Shows "Network Online" when all IPs are reachable
- **Responsive Design**: Works on desktop and mobile devices
- **Clean Interface**: Simple, easy-to-read status indicators

### Disable Flask Request Logs
To reduce console output, the application disables HTTP request logging by default. You'll only see:
```
Network Monitoring started
web server accessible on Localhost:5000
pinging IP List:
Ping to 192.168.16.1 successful. ✅
```

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

## Features Comparison

| Feature | app.py | app_v2.py | app_v0.3.py | app_v0.4.py |
|---------|--------|-----------|-------------|-------------|
| Basic ping functionality | ✅ | ✅ | ✅ | ✅ |
| Background monitoring | ❌ | ✅ | ✅ | ✅ |
| Threading support | ❌ | ✅ | ✅ | ✅ |
| Web dashboard | ❌ | ❌ | ✅ | ✅ |
| Individual IP status | ❌ | ❌ | ❌ | ✅ |
| API endpoints | ❌ | ❌ | ✅ | ✅ |
| Real-time updates | ❌ | ✅ | ✅ | ✅ |
| Clean logging | ❌ | ❌ | ❌ | ✅ |
| Interactive menu | ✅ | ❌ | ❌ | ❌ |

## Screenshots

### Web Dashboard
The web interface provides:
- Overall network status indicator
- Individual IP address cards showing online/offline status
- Automatic refresh every 2 seconds
- Clean, responsive design that works on all devices
- Last updated timestamp

### API Response Example
```json
{
  "network_status": true,
  "timestamp": 1692014338.123,
  "ip_addresses": ["192.168.16.1", "8.8.8.8", "1.1.1.1"],
  "ip_status": {
    "192.168.16.1": true,
    "8.8.8.8": true, 
    "1.1.1.1": false
  }
}
```

## Troubleshooting

### Permission Errors
```bash
# Linux/WSL: Grant ping capabilities
sudo setcap cap_net_raw+ep $(which python3)

# Or run with elevated privileges
sudo python3 app_v0.4.py
```

### Module Not Found
```bash
# Install missing dependencies
pip3 install ping3 flask
```

### Web Dashboard Not Loading
- Verify Flask is running: Check console for "web server accessible on Localhost:5000"
- Check firewall settings if accessing from other devices
- Try `http://127.0.0.1:5000` instead of `localhost:5000`

### Network Issues
- Verify IP addresses are reachable with manual ping: `ping 8.8.8.8`
- Check firewall settings blocking ICMP packets
- Test with different IP addresses (try `1.1.1.1` or `8.8.8.8`)
- Ensure network adapter is connected

### Flask Request Logs
If you see HTTP request logs cluttering output, they should be disabled by default in the latest version. If not, add this before `app.run()`:
```python
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)
```

## Development

### Adding New Features
1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Test on multiple platforms
5. Submit a pull request

### Contributing
- Follow Python PEP 8 style guidelines
- Add comments for complex logic
- Test on both Windows and Linux
- Update documentation as needed

## License

MIT License - feel free to modify and distribute as needed.

## Future Enhancements

- [ ] Email/SMS notifications when network goes down
- [ ] Historical data logging and charts
- [ ] Raspberry Pi GPIO integration (LED indicators)
- [ ] Configuration file support (YAML/JSON config)
- [ ] Multiple monitoring profiles/groups
- [ ] Network latency tracking and graphs
- [ ] Export data to CSV/Excel
- [ ] Mobile app companion
- [ ] Docker containerization
- [ ] Prometheus/Grafana integration
- [ ] Custom alert thresholds per IP
- [ ] Webhook notifications

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test on multiple platforms (Windows/Linux)
5. Update documentation as needed
6. Submit a pull request

### Code Style
- Follow Python PEP 8 style guidelines
- Add comments for complex logic
- Include docstrings for functions
- Test thoroughly before submitting

## License

MIT License - feel free to modify and distribute as needed.

## Author

**Joshua Huggard** - [joshuahuggard96](https://github.com/joshuahuggard96)

Project Link: [https://github.com/joshuahuggard96/network-monitor-pi](https://github.com/joshuahuggard96/network-monitor-pi)
