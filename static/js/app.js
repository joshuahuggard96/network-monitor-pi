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
            
            // Handle device_list format with remove buttons
            for (const [deviceName, deviceInfo] of Object.entries(data.device_list)) {
                const deviceDiv = document.createElement('div');
                deviceDiv.className = 'ip-item';
                
                if (deviceInfo.status === true) {
                    deviceDiv.classList.add('ip-online');
                    deviceDiv.innerHTML = `
                        <div>
                            <strong>${deviceName}</strong> 
                            <span class="status-indicator">Online</span>
                        </div>
                        <button onclick="removeDevice('${deviceName}')" class="btn-danger">Remove</button>
                    `;
                } else if (deviceInfo.status === false) {
                    deviceDiv.classList.add('ip-offline');
                    deviceDiv.innerHTML = `
                        <div>
                            <strong>${deviceName}</strong> 
                            <span class="status-indicator">Offline</span>
                        </div>
                        <button onclick="removeDevice('${deviceName}')" class="btn-danger">Remove</button>
                    `;
                } else {
                    deviceDiv.classList.add('ip-checking');
                    deviceDiv.innerHTML = `
                        <div>
                            <strong>${deviceName}</strong> 
                            <span class="status-indicator">Checking</span>
                        </div>
                        <button onclick="removeDevice('${deviceName}')" class="btn-danger">Remove</button>
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

// Add device form handler
function setupAddDeviceForm() {
    const form = document.getElementById('add-device-form');
    const messageDiv = document.getElementById('message');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const deviceData = {
                name: formData.get('name'),
                ip: formData.get('ip')
            };
            
            fetch('/api/add-device', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(deviceData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    messageDiv.innerHTML = `<div class="success">${data.message}</div>`;
                    form.reset();
                    updateStatus(); // Refresh the device list
                } else {
                    messageDiv.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                messageDiv.innerHTML = `<div class="error">Error adding device</div>`;
            });
        });
    }
}

// Remove device function
function removeDevice(deviceName) {
    if (confirm(`Are you sure you want to remove "${deviceName}"?`)) {
        fetch('/api/remove-device', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({name: deviceName})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatus(); // Refresh the device list
                showMessage(`Device "${deviceName}" removed successfully`, 'success');
            } else {
                showMessage(`Error: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Error removing device', 'error');
        });
    }
}

// Helper function to show messages
function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.innerHTML = `<div class="${type}">${text}</div>`;
    setTimeout(() => {
        messageDiv.innerHTML = '';
    }, 3000);
}

// Initialize the application
function initApp() {
    console.log('Network Monitor Dashboard loaded');
    updateStatus();
    setupAddDeviceForm(); // Setup form handlers
    setInterval(updateStatus, 500);
}

// Start the app when the page loads
document.addEventListener('DOMContentLoaded', initApp);
