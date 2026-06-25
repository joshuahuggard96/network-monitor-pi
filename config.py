"""
Configuration file for network-monitor-pi
Edit these values to customize your setup
"""

# Network monitoring settings
PING_INTERVAL = 0.5  # seconds between ping checks
PING_TIMEOUT = 2     # seconds to wait for ping response

# Socket/Relay settings
RELAY_HOST = '127.0.0.1'  # IP address of relay controller
RELAY_PORT = 7000          # Port number for relay controller

# Web server settings
WEB_HOST = '0.0.0.0'  # 0.0.0.0 means accessible from any network interface
WEB_PORT = 5000       # Port for web dashboard
WEB_DEBUG = False     # Set to True for development

# Logging settings
LOG_LEVEL = 'INFO'   # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
