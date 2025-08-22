function updateStatus() {
    fetch('/api/status') // calls API
        .then(response => response.json())
        .then(data => {
            // Update overall status
            const statusDiv = document.getElementById('status');
            if (data.output_status) {
                statusDiv.textContent = 'Relay Status ON';
                statusDiv.className = 'status online';
            } else {
                statusDiv.textContent = 'Relay Status OFF';
                statusDiv.className = 'status offline';
            }
            

            // Update individual devices
            const ipListDiv = document.getElementById('ip-list');
            ipListDiv.innerHTML = '<h3>Device Status:</h3>';
            
            // Handle device_list format
            for (const [deviceName, deviceInfo] of Object.entries(data.device_list)) {
                const deviceDiv = document.createElement('div');
                deviceDiv.className = 'ip-item';
                
                if (deviceInfo.status === true) {
                    deviceDiv.classList.add('ip-online');
                    deviceDiv.innerHTML = `
                        <strong>${deviceName}</strong> 
                        <span class="status-indicator">Online</span>
                    `;
                } else if (deviceInfo.status === false) {
                    deviceDiv.classList.add('ip-offline');
                    deviceDiv.innerHTML = `
                        <strong>${deviceName}</strong> 
                        <span class="status-indicator">Offline</span>
                    `;
                } else {
                    deviceDiv.classList.add('ip-checking');
                    deviceDiv.innerHTML = `
                        <strong>${deviceName}</strong> 
                        <span class="status-indicator">Checking</span>
                    `;
                }
                
                ipListDiv.appendChild(deviceDiv);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('status').textContent = 'Error checking status';
            document.getElementById('status').className = 'status offline';
        });
}

// Initialize the application
function initApp() {
    console.log('Network Monitor Dashboard loaded');
    updateStatus();
    setInterval(updateStatus, 500);
}

// Start the app when the page loads
document.addEventListener('DOMContentLoaded', initApp);
