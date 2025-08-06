# Network Monitor

A Python-based network monitoring tool that continuously pings IP addresses and provides real-time status updates. Features both command-line interface and background monitoring capabilities.

## Features

- **Continuous Network Monitoring**: Background thread monitors network connectivity
- **Multiple Ping Methods**: Support for both `pythonping` library and system ping fallback
- **Cross-Platform Support**: Works on Windows, Linux, and WSL
- **Real-Time Status Updates**: Live monitoring with configurable intervals
- **Flexible IP Management**: Easy addition/removal of IP addresses to monitor
- **Debug Mode**: Detailed logging for troubleshooting
- **Thread-Safe Operations**: Safe concurrent access to monitoring results

## Project Structure

```
network-monitor-pi/
├── app.py          # Original subprocess-based implementation
├── app_v2.py       # Enhanced version with pythonping and threading
├── README.md       # This file
└── requirements.txt # Python dependencies
```

## Requirements

- Python 3.6+
- ping3 or pythonping library
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
   pip install ping3
   pip install pythonping
   
   # For Linux/WSL
   pip3 install ping3
   pip3 install pythonping
   ```

3. **Linux/WSL Permission Setup** (if using pythonping)
   ```bash
   # Grant ping capabilities to Python
   sudo setcap cap_net_raw+ep $(which python3)
   
   # Or run with sudo
   sudo python3 app_v2.py
   ```

## Usage

### Basic Version (app.py)
```bash
python3 app.py
```
- Simple subprocess-based ping implementation
- Interactive menu for IP management
- Manual ping operations

### Enhanced Version (app_v2.py)
```bash
python3 app_v2.py
```
- Background monitoring with threading
- Real-time status updates
- Configurable success thresholds

### Interactive Commands
- **Enter**: Check current monitoring status
- **"stop"**: Stop monitoring and exit
- **"debug"**: Enable debug mode for detailed output

## Configuration

Edit the variables at the top of `app_v2.py`:

```python
ping_interval = 1           # Seconds between ping cycles
times_to_check = 2         # Successful pings needed for "online" status
ip_address_list = [        # IPs to monitor
    "192.168.0.1",         # Router/Gateway
    "8.8.8.8",             # Google DNS
    "1.1.1.1"              # Cloudflare DNS
]
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

| Feature | app.py | app_v2.py |
|---------|--------|-----------|
| Basic ping functionality | ✅ | ✅ |
| Background monitoring | ❌ | ✅ |
| Threading support | ❌ | ✅ |
| Real-time status | ❌ | ✅ |
| Success threshold | ❌ | ✅ |
| Interactive menu | ✅ | ❌ |
| Debug mode | ❌ | ✅ |

## Troubleshooting

### Permission Errors
```bash
# Linux/WSL: Grant ping capabilities
sudo setcap cap_net_raw+ep $(which python3)

# Or run with elevated privileges
sudo python3 app_v2.py
```

### Module Not Found
```bash
# Install missing dependencies
pip3 install ping3 pythonping
```

### Network Issues
- Verify IP addresses are reachable
- Check firewall settings
- Test with basic system ping first

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

- [ ] Web dashboard interface
- [ ] Email/SMS notifications
- [ ] Raspberry Pi GPIO integration
- [ ] Configuration file support
- [ ] Logging to file
- [ ] Network latency tracking
- [ ] Multiple monitoring profiles
