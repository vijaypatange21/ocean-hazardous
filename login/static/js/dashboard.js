// Dashboard JavaScript - static/js/dashboard.js

let locationMap, mainMap;
let currentLocation = { lat: 20.5937, lng: 78.9629 }; // Default: India center
let selectedLocation = null;
let mapMarkers = [];

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize maps when submit report is shown
    initializeGeolocation();
});

// Navigation Functions
function showDashboard() {
    hideAllContent();
    document.getElementById('dashboard-content').classList.remove('d-none');
    document.getElementById('dashboard-content').classList.add('fade-in');
    updateActiveNav('dashboard');
}

function showSubmitReport() {
    hideAllContent();
    document.getElementById('submit-report-content').classList.remove('d-none');
    document.getElementById('submit-report-content').classList.add('fade-in');
    updateActiveNav('reports');
    
    // Initialize location map after a brief delay
    setTimeout(initializeLocationMap, 100);
}

function showMap() {
    hideAllContent();
    document.getElementById('map-content').classList.remove('d-none');
    document.getElementById('map-content').classList.add('fade-in');
    updateActiveNav('map');
    
    // Initialize main map after a brief delay
    setTimeout(initializeMainMap, 100);
}

function showGuidelines() {
    hideAllContent();
    document.getElementById('guidelines-content').classList.remove('d-none');
    document.getElementById('guidelines-content').classList.add('fade-in');
    updateActiveNav('guidelines');
}

function hideAllContent() {
    const contents = [
        'dashboard-content',
        'submit-report-content', 
        'map-content',
        'guidelines-content'
    ];
    
    contents.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.classList.add('d-none');
            element.classList.remove('fade-in');
        }
    });
}

function updateActiveNav(activeSection) {
    // Remove active class from all nav links
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Add active class to current section
    const navMap = {
        'dashboard': 0,
        'reports': 1,
        'map': 2,
        'guidelines': 1 // Guidelines is under reports dropdown
    };
    
    if (navMap[activeSection] !== undefined) {
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        if (navLinks[navMap[activeSection]]) {
            navLinks[navMap[activeSection]].classList.add('active');
        }
    }
}

// Geolocation Functions
function initializeGeolocation() {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                currentLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
            },
            function(error) {
                console.log("Geolocation error:", error);
                // Keep default location (India center)
            }
        );
    }
}

function getCurrentLocation() {
    if ("geolocation" in navigator) {
        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Getting Location...';
        button.disabled = true;

        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                selectedLocation = { lat, lng };
                updateLocationInputs(lat, lng);
                
                if (locationMap) {
                    locationMap.setView([lat, lng], 15);
                    updateLocationMarker(lat, lng);
                }
                
                button.innerHTML = originalText;
                button.disabled = false;
            },
            function(error) {
                alert("Unable to get your location. Please select manually on the map.");
                button.innerHTML = originalText;
                button.disabled = false;
            }
        );
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

// Map Initialization Functions
function initializeLocationMap() {
    if (locationMap) {
        locationMap.remove();
    }
    
    locationMap = L.map('location-map').setView([currentLocation.lat, currentLocation.lng], 10);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(locationMap);
    
    // Add click event to select location
    locationMap.on('click', function(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        
        selectedLocation = { lat, lng };
        updateLocationInputs(lat, lng);
        updateLocationMarker(lat, lng);
    });
}

function initializeMainMap() {
    if (mainMap) {
        mainMap.remove();
    }
    
    mainMap = L.map('main-map').setView([currentLocation.lat, currentLocation.lng], 6);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(mainMap);
    
    // Load hazard reports
    loadHazardReports();
}

function updateLocationInputs(lat, lng) {
    // Round coordinates to 8 decimal places to match model precision
    const roundedLat = Math.round(lat * 100000000) / 100000000; // 8 decimal places
    const roundedLng = Math.round(lng * 100000000) / 100000000; // 8 decimal places
    
    document.getElementById('latitude').value = roundedLat;
    document.getElementById('longitude').value = roundedLng;
    document.getElementById('location-display').value = `Lat: ${roundedLat.toFixed(6)}, Lng: ${roundedLng.toFixed(6)}`;
    
    // Optional: Reverse geocode to get address
    reverseGeocode(roundedLat, roundedLng);
}

function updateLocationMarker(lat, lng) {
    // Remove existing marker
    locationMap.eachLayer(function(layer) {
        if (layer instanceof L.Marker) {
            locationMap.removeLayer(layer);
        }
    });
    
    // Add new marker
    L.marker([lat, lng])
        .addTo(locationMap)
        .bindPopup('Selected Location')
        .openPopup();
}

function reverseGeocode(lat, lng) {
    // Using OpenStreetMap Nominatim API for reverse geocoding (free)
    fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
        .then(response => response.json())
        .then(data => {
            if (data && data.display_name) {
                document.getElementById('location-display').value = data.display_name;
            }
        })
        .catch(error => {
            console.log('Reverse geocoding failed:', error);
        });
}

// Load and display hazard reports on main map
function loadHazardReports() {
    fetch('/api/map-data/')
        .then(response => response.json())
        .then(data => {
            displayHazardReports(data.reports);
        })
        .catch(error => {
            console.error('Error loading hazard reports:', error);
        });
}

function displayHazardReports(reports) {
    // Clear existing markers
    mapMarkers.forEach(marker => mainMap.removeLayer(marker));
    mapMarkers = [];
    
    reports.forEach(report => {
        const marker = createHazardMarker(report);
        marker.addTo(mainMap);
        mapMarkers.push(marker);
    });
}

function createHazardMarker(report) {
    // Choose icon based on severity and status
    let iconColor = getMarkerColor(report.status, report.severity);
    
    const marker = L.marker([report.lat, report.lng]);
    
    // Create popup content
    const popupContent = `
        <div class="p-2">
            <h6><strong>Report #${report.id}</strong></h6>
            <p><strong>Type:</strong> ${report.hazard_type}</p>
            <p><strong>Severity:</strong> <span class="badge bg-${getSeverityColor(report.severity)}">${report.severity}</span></p>
            <p><strong>Status:</strong> <span class="badge bg-${getStatusColor(report.status)}">${report.status}</span></p>
            <p><strong>Reporter:</strong> ${report.reporter}</p>
            <p><strong>Time:</strong> ${report.created_at}</p>
            <p><strong>Description:</strong> ${report.description}</p>
            ${report.urgent ? '<span class="badge bg-danger">URGENT</span>' : ''}
        </div>
    `;
    
    marker.bindPopup(popupContent);
    
    return marker;
}

function getMarkerColor(status, severity) {
    if (severity === 'critical') return 'red';
    if (status === 'verified') return 'green';
    if (status === 'pending') return 'orange';
    if (status === 'investigating') return 'blue';
    return 'gray';
}

function getSeverityColor(severity) {
    const colors = {
        'low': 'success',
        'moderate': 'warning',
        'high': 'danger',
        'critical': 'dark'
    };
    return colors[severity] || 'secondary';
}

function getStatusColor(status) {
    const colors = {
        'pending': 'warning',
        'verified': 'success',
        'rejected': 'danger',
        'investigating': 'info'
    };
    return colors[status] || 'secondary';
}

// Map utility functions
function refreshMapData() {
    if (mainMap) {
        loadHazardReports();
    }
}

function toggleMapView() {
    // Toggle between street view and satellite view (if available)
    // This is a placeholder - you can implement different tile layers
    console.log('Toggle map view - implement different tile layers if needed');
}

// Form submission handling with AJAX
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('hazard-report-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent normal form submission
            
            // Validate location is selected
            const lat = document.getElementById('latitude').value;
            const lng = document.getElementById('longitude').value;
            
            if (!lat || !lng) {
                showAlert('Please select a location on the map or use "Use My Location" button.', 'warning');
                return false;
            }
            
            // Add loading state
            const submitButton = form.querySelector('button[type="submit"]');
            const originalText = submitButton.innerHTML;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Submitting...';
            submitButton.disabled = true;
            
            // Create FormData object
            const formData = new FormData(form);
            
            // Submit form via AJAX
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    showAlert(data.message, 'success');
                    
                    // Reset form
                    form.reset();
                    document.getElementById('location-display').value = '';
                    
                    // Reset map marker
                    if (locationMap) {
                        locationMap.eachLayer(function(layer) {
                            if (layer instanceof L.Marker) {
                                locationMap.removeLayer(layer);
                            }
                        });
                    }
                    
                    // Reset selected location
                    selectedLocation = null;
                    
                    // Update dashboard stats
                    updateDashboardStats();
                    
                    // Switch back to dashboard after 3 seconds
                    setTimeout(() => {
                        showDashboard();
                    }, 3000);
                    
                } else {
                    // Show error message
                    showAlert(data.error || 'An error occurred while submitting the report.', 'danger');
                }
            })
            .catch(error => {
                console.error('Form submission error:', error);
                showAlert('Network error. Please check your connection and try again.', 'danger');
            })
            .finally(() => {
                // Restore button state
                submitButton.innerHTML = originalText;
                submitButton.disabled = false;
            });
        });
    }
});

// Add file input event listener
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('input[name="media_files"]');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelection);
    }
});

// File upload handling
function handleFileSelection() {
    const fileInput = document.querySelector('input[name="media_files"]');
    const files = fileInput.files;
    
    if (files.length > 0) {
        let totalSize = 0;
        for (let file of files) {
            totalSize += file.size;
        }
        
        // Check total size (50MB limit)
        const maxSize = 50 * 1024 * 1024; // 50MB
        if (totalSize > maxSize) {
            alert('Total file size exceeds 50MB limit. Please select smaller files.');
            fileInput.value = '';
            return;
        }
        
        // Show selected files count
        const helpText = fileInput.nextElementSibling;
        if (helpText) {
            helpText.textContent = `${files.length} file(s) selected (${formatFileSize(totalSize)})`;
        }
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Dashboard statistics update (optional - for real-time updates)
function updateDashboardStats() {
    fetch('/api/dashboard-stats/')
        .then(response => response.json())
        .then(data => {
            // Update stats numbers if elements exist
            const statsElements = document.querySelectorAll('.stats-number');
            if (statsElements.length >= 3 && data) {
                if (data.this_month !== undefined) statsElements[0].textContent = data.this_month;
                if (data.total_reports !== undefined) statsElements[1].textContent = data.total_reports;
                if (data.approval_rate !== undefined) statsElements[2].textContent = data.approval_rate + '%';
            }
        })
        .catch(error => {
            console.log('Stats update failed:', error);
        });
}

// Initialize stats update on page load
document.addEventListener('DOMContentLoaded', function() {
    updateDashboardStats();
    // Update stats every 5 minutes
    setInterval(updateDashboardStats, 300000);
});

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Handle responsive behavior
function handleResize() {
    if (locationMap) {
        setTimeout(() => locationMap.invalidateSize(), 100);
    }
    if (mainMap) {
        setTimeout(() => mainMap.invalidateSize(), 100);
    }
}

window.addEventListener('resize', handleResize);

// Handle bootstrap modal/collapse events for map resize
document.addEventListener('shown.bs.collapse', handleResize);
document.addEventListener('shown.bs.modal', handleResize);