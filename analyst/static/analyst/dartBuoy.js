// Add these variables to your existing global variables at the top
let dartBuoyLiveChart;
let dartBuoyUpdateInterval;

// Replace the existing createDartBuoyChart function with this enhanced version
function createDartBuoyChart() {
    const ctx = document.getElementById('dart-buoy-chart');
    if (!ctx) return;

    if (charts.dartBuoy) {
        charts.dartBuoy.destroy();
    }

    // Initialize empty chart first
    charts.dartBuoy = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Wave Height (m)'
                    },
                    min: 0,
                    max: 5
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Real-time Indian Ocean DART Buoy Data'
                },
                legend: {
                    position: 'top'
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });

    // Load live data
    updateDartBuoyLiveData();
}

// Add this new function to fetch live buoy data
function updateDartBuoyLiveData() {
    fetch('/ana/api/buoy-data/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                updateDartBuoyChartData(data.buoys);
                updateBuoyStatusGrid(data.buoys);
                console.log('DART buoy data updated successfully');
            } else {
                console.error('Failed to fetch buoy data:', data.error);
                // Fall back to simulated data
                createSimulatedDartBuoyChart();
            }
        })
        .catch(error => {
            console.error('Error fetching buoy data:', error);
            // Fall back to simulated data
            createSimulatedDartBuoyChart();
        });
}

// Add this function to update chart with live data
function updateDartBuoyChartData(buoys) {
    if (!charts.dartBuoy) return;

    // Clear existing datasets
    charts.dartBuoy.data.datasets = [];
    
    buoys.forEach((buoy, index) => {
        if (buoy.chart_data && buoy.chart_data.length > 0) {
            const color = chartColors[index % chartColors.length];
            
            charts.dartBuoy.data.datasets.push({
                label: `${buoy.buoy_id} - ${buoy.name}`,
                data: buoy.chart_data.map(reading => ({
                    x: new Date(reading.timestamp).toLocaleTimeString(),
                    y: reading.wave_height || 0
                })),
                borderColor: color,
                backgroundColor: color + '20',
                borderWidth: 2,
                pointRadius: 3,
                fill: false,
                tension: 0.4
            });
        }
    });
    
    // Update time labels from the most recent buoy data
    if (buoys.length > 0 && buoys[0].chart_data) {
        charts.dartBuoy.data.labels = buoys[0].chart_data.map(reading => 
            new Date(reading.timestamp).toLocaleTimeString()
        );
    }
    
    charts.dartBuoy.update();
}

// Add this function to update buoy status grid
function updateBuoyStatusGrid(buoys) {
    const statusGrid = document.querySelector('.buoy-status-grid');
    if (!statusGrid) return;
    
    statusGrid.innerHTML = '';
    
    buoys.forEach(buoy => {
        const statusDiv = document.createElement('div');
        statusDiv.className = `buoy-status ${buoy.status}`;
        
        statusDiv.innerHTML = `
            <span class="buoy-id">${buoy.buoy_id}</span>
            <span class="buoy-reading">${buoy.current_wave_height ? buoy.current_wave_height.toFixed(1) + 'm' : '--'}</span>
        `;
        
        statusGrid.appendChild(statusDiv);
    });
}

// Add this fallback function for when API is not available
function createSimulatedDartBuoyChart() {
    const ctx = document.getElementById('dart-buoy-chart');
    if (!ctx) return;

    if (charts.dartBuoy) {
        charts.dartBuoy.destroy();
    }

    // Generate time series data for Indian Ocean buoys
    const timeLabels = [];
    const now = new Date();
    for (let i = 23; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60 * 60 * 1000);
        timeLabels.push(time.toISOString().substr(11, 5));
    }

    // Simulated Indian Ocean buoys data
    const indianOceanBuoys = [
        {id: "23001", name: "Arabian Sea", wave_height: 2.1},
        {id: "23101", name: "Arabian Sea North", wave_height: 1.8},
        {id: "23007", name: "Lakshadweep Sea", wave_height: 2.5},
        {id: "46002", name: "Indian Ocean", wave_height: 3.2}
    ];

    const datasets = indianOceanBuoys.map((buoy, index) => ({
        label: `${buoy.id} - ${buoy.name}`,
        data: generateWaveData(buoy.wave_height, 24),
        borderColor: chartColors[index],
        backgroundColor: chartColors[index] + '20',
        borderWidth: 2,
        pointRadius: 3,
        fill: false,
        tension: 0.4
    }));

    charts.dartBuoy = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeLabels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time (24h)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Wave Height (m)'
                    },
                    min: 0,
                    max: 5
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Indian Ocean DART Buoy Data (Simulated)'
                },
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

// Add this function to manually refresh buoy data
// Replace your existing refreshDartBuoyData function with this:
function refreshDartBuoyData() {
    const refreshBtn = document.querySelector('.refresh-btn');
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.textContent = 'Refreshing...';
    }
    
    // Get CSRF token properly
    let csrfToken = '';
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        csrfToken = csrfInput.value;
    }
    
    const headers = {
        'Content-Type': 'application/json'
    };
    
    // Only add CSRF token if it exists and has proper length
    if (csrfToken && csrfToken.length > 10) {
        headers['X-CSRFToken'] = csrfToken;
    }
    
    fetch('/ana/api/refresh-data/', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({}) // Send empty JSON body
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            updateDartBuoyLiveData();
            console.log('Data refreshed successfully');
        } else {
            console.error('Failed to refresh:', data.error);
        }
    })
    .catch(error => {
        console.error('Error refreshing data:', error);
    })
    .finally(() => {
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.textContent = 'Refresh Data';
        }
    });
}

// Add this function to start DART buoy auto-updates
function startDartBuoyUpdates() {
    // Update immediately
    if (currentSection === 'analytics') {
        updateDartBuoyLiveData();
    }
    
    // Then update every 5 minutes
    dartBuoyUpdateInterval = setInterval(() => {
        if (currentSection === 'analytics') {
            updateDartBuoyLiveData();
        }
    }, 300000); // 5 minutes
}

// Modify the existing initializeAnalytics function to include DART buoy updates
function initializeAnalyticsEnhanced() {
    createDartBuoyChart(); // This will now use live data
    createStormSurgeChart();
    createSeismicChart();
    
    // Start live updates for DART buoys
    startDartBuoyUpdates();
}

// Replace the initializeAnalytics call in switchSection
function switchSectionEnhanced(sectionName) {
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

    // Update content sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`${sectionName}-section`).classList.add('active');

    currentSection = sectionName;

    // Initialize section-specific content
    switch(sectionName) {
        case 'dashboard':
            initializeDashboard();
            break;
        case 'analytics':
            initializeAnalyticsEnhanced(); // Use enhanced version
            break;
        case 'statistics':
            initializeStatistics();
            break;
        case 'reports':
            initializeReports();
            break;
        case 'data-management':
            initializeDataManagement();
            break;
    }
}

// Add cleanup for DART buoy intervals
window.addEventListener('beforeunload', function() {
    if (realTimeInterval) {
        clearInterval(realTimeInterval);
    }
    
    if (dartBuoyUpdateInterval) {
        clearInterval(dartBuoyUpdateInterval);
    }
    
    // Destroy all charts
    Object.values(charts).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });
});

// Make refreshDartBuoyData globally accessible for refresh button
window.refreshBuoyData = refreshDartBuoyData;