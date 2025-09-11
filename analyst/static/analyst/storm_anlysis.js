// Indian Ocean Analytics Functions with Auto-Refresh
// Add these to your existing analytics.js file

// Add these variables to your existing global variables
let stormSurgeChart;
let seismicChart;
let riskAssessmentInterval;
let autoRefreshInterval;

// Auto-refresh function for all analytics data
function startAutoRefresh() {
    // Clear existing interval if any
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    // Auto-refresh every 7 seconds
    autoRefreshInterval = setInterval(() => {
        if (currentSection === 'analytics') {
            refreshAllAnalyticsData();
        }
    }, 7000); // 7 seconds
}

// Stop auto-refresh
function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Refresh all analytics data
async function refreshAllAnalyticsData() {
    try {
        // Show loading state if needed
        const refreshBtns = document.querySelectorAll('.refresh-btn');
        refreshBtns.forEach(btn => {
            btn.textContent = 'Refreshing...';
            btn.disabled = true;
        });

        // Refresh DART buoy data (call your existing function)
        if (typeof refreshBuoyData === 'function') {
            await refreshBuoyData();
        }
        
        // Refresh storm surge data
        await refreshStormSurgeData();
        
        // Refresh seismic data
        await refreshSeismicData();
        
        // Refresh risk assessment
        await refreshRiskAssessmentData();
        
        // Update UI with fresh data
        updateSurgeAlerts();
        updateRegionalRiskAssessment();
        
        // Reset button states
        refreshBtns.forEach(btn => {
            btn.textContent = 'Refresh Data';
            btn.disabled = false;
        });
        
    } catch (error) {
        console.error('Error refreshing analytics data:', error);
        
        // Reset button states on error
        const refreshBtns = document.querySelectorAll('.refresh-btn');
        refreshBtns.forEach(btn => {
            btn.textContent = 'Refresh Data';
            btn.disabled = false;
        });
    }
}

// Manual refresh function for buttons
async function manualRefreshAnalytics() {
    await refreshAllAnalyticsData();
}

// Fetch storm surge data from Django API
async function refreshStormSurgeData() {
    try {
        const response = await fetch('/ana/api/storm-surge-data/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        });
        
        if (response.ok) {
            const data = await response.json();
            updateStormSurgeChart(data);
        }
    } catch (error) {
        console.error('Error fetching storm surge data:', error);
        // Fallback to generated data
        createStormSurgeChart();
    }
}

// Fetch seismic data from Django API
async function refreshSeismicData() {
    try {
        const response = await fetch('/ana/api/seismic-data/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        });
        
        if (response.ok) {
            const data = await response.json();
            updateSeismicChart(data);
        }
    } catch (error) {
        console.error('Error fetching seismic data:', error);
        // Fallback to generated data
        createSeismicChart();
    }
}

// Fetch risk assessment data from Django API
async function refreshRiskAssessmentData() {
    try {
        const response = await fetch('/ana/api/risk-assessment/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        });
        
        if (response.ok) {
            const data = await response.json();
            updateRegionalRiskAssessment(data);
        }
    } catch (error) {
        console.error('Error fetching risk assessment data:', error);
        // Fallback to generated data
        updateRegionalRiskAssessment();
    }
}

// Update storm surge chart with API data
function updateStormSurgeChart(apiData) {
    if (!charts.stormSurge) {
        createStormSurgeChart();
        return;
    }
    
    if (apiData && apiData.regions) {
        // Update with API data
        const datasets = apiData.regions.map((region, index) => ({
            label: region.name,
            data: region.surge_data,
            borderColor: chartColors[index % chartColors.length],
            backgroundColor: chartColors[index % chartColors.length] + '20',
            borderWidth: 2,
            pointRadius: 4,
            fill: true,
            tension: 0.4
        }));
        
        charts.stormSurge.data.datasets = datasets;
        if (apiData.time_labels) {
            charts.stormSurge.data.labels = apiData.time_labels;
        }
        charts.stormSurge.update();
    } else {
        // Fallback to generated data
        createStormSurgeChart();
    }
}

// Update seismic chart with API data
function updateSeismicChart(apiData) {
    if (!charts.seismic) {
        createSeismicChart();
        return;
    }
    
    if (apiData && apiData.plates) {
        // Update with API data
        const datasets = apiData.plates.map((plate, index) => ({
            label: plate.name,
            data: plate.seismic_data,
            backgroundColor: chartColors[index % chartColors.length] + '99',
            borderColor: chartColors[index % chartColors.length],
            pointRadius: 6
        }));
        
        charts.seismic.data.datasets = datasets;
        charts.seismic.update();
    } else {
        // Fallback to generated data
        createSeismicChart();
    }
}

// Storm Surge Analysis for Indian Ocean regions
function createStormSurgeChart() {
    const ctx = document.getElementById('storm-surge-chart');
    if (!ctx) return;

    if (charts.stormSurge) {
        charts.stormSurge.destroy();
    }

    // Indian Ocean storm surge data
    const timeLabels = [];
    const now = new Date();
    for (let i = 11; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 2 * 60 * 60 * 1000); // 2-hour intervals
        timeLabels.push(time.toLocaleTimeString());
    }

    // Indian Ocean coastal regions surge predictions
    const surgeData = {
        'Arabian Sea Coast': generateSurgeData(2.1, 12),
        'Bay of Bengal': generateSurgeData(3.2, 12),
        'Maldives Region': generateSurgeData(1.8, 12),
        'Sri Lanka Coast': generateSurgeData(2.7, 12)
    };

    const datasets = Object.keys(surgeData).map((region, index) => ({
        label: region,
        data: surgeData[region],
        borderColor: chartColors[index],
        backgroundColor: chartColors[index] + '20',
        borderWidth: 2,
        pointRadius: 4,
        fill: true,
        tension: 0.4
    }));

    charts.stormSurge = new Chart(ctx, {
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
                        text: 'Time (12h forecast)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Surge Height (m)'
                    },
                    min: 0,
                    max: 5
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Indian Ocean Storm Surge Forecast'
                },
                legend: {
                    position: 'top'
                }
            }
        }
    });

    // Update surge alerts
    updateSurgeAlerts();
}

// Generate realistic storm surge data
function generateSurgeData(baseHeight, points) {
    const data = [];
    for (let i = 0; i < points; i++) {
        // Simulate tidal and storm effects
        const tidal = Math.sin(i * 0.5) * 0.3;
        const storm = Math.sin(i * 0.2) * 0.8;
        const random = (Math.random() - 0.5) * 0.4;
        const surge = Math.max(0, baseHeight + tidal + storm + random);
        data.push(parseFloat(surge.toFixed(2)));
    }
    return data;
}

// Update surge alert cards with Indian Ocean data
function updateSurgeAlerts(apiData = null) {
    const alertsContainer = document.querySelector('.surge-alerts');
    if (!alertsContainer) return;

    let indianOceanAlerts;
    
    if (apiData && apiData.alerts) {
        indianOceanAlerts = apiData.alerts;
    } else {
        // Fallback data
        indianOceanAlerts = [
            {
                location: 'Bay of Bengal',
                height: '3.4m surge expected',
                level: 'high'
            },
            {
                location: 'Arabian Sea Coast',
                height: '2.1m surge expected',
                level: 'medium'
            },
            {
                location: 'Maldives Region',
                height: '1.9m surge expected',
                level: 'low'
            }
        ];
    }

    alertsContainer.innerHTML = '';
    indianOceanAlerts.forEach(alert => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `surge-alert ${alert.level}`;
        alertDiv.innerHTML = `
            <div class="surge-location">${alert.location}</div>
            <div class="surge-height">${alert.height}</div>
        `;
        alertsContainer.appendChild(alertDiv);
    });
}

// Seismic Activity Correlation for Indian Ocean
function createSeismicChart() {
    const ctx = document.getElementById('seismic-chart');
    if (!ctx) return;

    if (charts.seismic) {
        charts.seismic.destroy();
    }

    // Generate seismic data for Indian Ocean tectonic regions
    const seismicData = generateSeismicCorrelationData();

    charts.seismic = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Indo-Australian Plate',
                data: seismicData.indoAustralian,
                backgroundColor: 'rgba(255, 99, 132, 0.6)',
                borderColor: 'rgba(255, 99, 132, 1)',
                pointRadius: 6
            }, {
                label: 'Eurasian Plate',
                data: seismicData.eurasian,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                pointRadius: 6
            }, {
                label: 'Burma Plate',
                data: seismicData.burma,
                backgroundColor: 'rgba(255, 206, 86, 0.6)',
                borderColor: 'rgba(255, 206, 86, 1)',
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Magnitude (Richter Scale)'
                    },
                    min: 3,
                    max: 9
                },
                y: {
                    title: {
                        display: true,
                        text: 'Tsunami Risk Factor'
                    },
                    min: 0,
                    max: 10
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Indian Ocean Seismic Activity vs Tsunami Risk'
                },
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: Magnitude ${context.parsed.x}, Risk ${context.parsed.y}`;
                        }
                    }
                }
            }
        }
    });
}

// Generate seismic correlation data for Indian Ocean plates
function generateSeismicCorrelationData() {
    const data = {
        indoAustralian: [],
        eurasian: [],
        burma: []
    };

    // Indo-Australian Plate (higher tsunami risk due to subduction zones)
    for (let i = 0; i < 15; i++) {
        const magnitude = 4 + Math.random() * 4.5;
        const risk = magnitude > 7 ? 6 + Math.random() * 3 : 2 + Math.random() * 4;
        data.indoAustralian.push({x: parseFloat(magnitude.toFixed(1)), y: parseFloat(risk.toFixed(1))});
    }

    // Eurasian Plate (moderate tsunami risk)
    for (let i = 0; i < 12; i++) {
        const magnitude = 3.5 + Math.random() * 4;
        const risk = magnitude > 6.5 ? 4 + Math.random() * 3 : 1 + Math.random() * 3;
        data.eurasian.push({x: parseFloat(magnitude.toFixed(1)), y: parseFloat(risk.toFixed(1))});
    }

    // Burma Plate (variable tsunami risk)
    for (let i = 0; i < 10; i++) {
        const magnitude = 4.2 + Math.random() * 3.8;
        const risk = magnitude > 7.2 ? 7 + Math.random() * 2.5 : 2.5 + Math.random() * 3.5;
        data.burma.push({x: parseFloat(magnitude.toFixed(1)), y: parseFloat(risk.toFixed(1))});
    }

    return data;
}

// Update Regional Risk Assessment for Indian Ocean
function updateRegionalRiskAssessment(apiData = null) {
    const riskHeatmap = document.querySelector('.risk-heatmap');
    if (!riskHeatmap) return;

    let indianOceanRisks;
    
    if (apiData && apiData.regions) {
        indianOceanRisks = apiData.regions;
    } else {
        // Fallback data - Indian Ocean regional risk data
        indianOceanRisks = [
            {
                region: 'Sumatra Coast',
                score: 8.7,
                level: 'very-high'
            },
            {
                region: 'Andaman Islands',
                score: 8.2,
                level: 'high'
            },
            {
                region: 'Sri Lanka Coast',
                score: 7.4,
                level: 'high'
            },
            {
                region: 'Maldives',
                score: 6.9,
                level: 'medium'
            },
            {
                region: 'Indian West Coast',
                score: 6.2,
                level: 'medium'
            },
            {
                region: 'Bangladesh Coast',
                score: 7.8,
                level: 'high'
            }
        ];
    }

    riskHeatmap.innerHTML = '';
    indianOceanRisks.forEach(risk => {
        const riskDiv = document.createElement('div');
        riskDiv.className = `risk-region ${risk.level}`;
        riskDiv.innerHTML = `
            <span class="region-name">${risk.region}</span>
            <span class="risk-score">${risk.score}</span>
        `;
        riskHeatmap.appendChild(riskDiv);
    });
}

// Start risk assessment updates
function startRiskAssessmentUpdates() {
    // Update immediately
    updateRegionalRiskAssessment();
    
    // Update every 10 minutes
    riskAssessmentInterval = setInterval(() => {
        if (currentSection === 'analytics') {
            updateRegionalRiskAssessment();
            updateSurgeAlerts();
        }
    }, 600000); // 10 minutes
}

// Enhanced analytics initialization to include all Indian Ocean analytics
function initializeIndianOceanAnalytics() {
    createDartBuoyChart(); // Your existing function
    createStormSurgeChart(); // New storm surge analysis
    createSeismicChart(); // New seismic correlation
    
    // Start live updates
    startDartBuoyUpdates(); // Your existing function
    startRiskAssessmentUpdates(); // New risk assessment updates
    startAutoRefresh(); // Start auto-refresh every 7 seconds
}

// Add cleanup for new intervals
window.addEventListener('beforeunload', function() {
    if (realTimeInterval) {
        clearInterval(realTimeInterval);
    }
    
    if (dartBuoyUpdateInterval) {
        clearInterval(dartBuoyUpdateInterval);
    }
    
    if (riskAssessmentInterval) {
        clearInterval(riskAssessmentInterval);
    }
    
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    // Destroy all charts
    Object.values(charts).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });
});

// Replace your analytics section switch case with this enhanced version
function switchSectionIndianOcean(sectionName) {
    // Stop auto-refresh when leaving analytics section
    if (currentSection === 'analytics' && sectionName !== 'analytics') {
        stopAutoRefresh();
    }
    
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
            initializeIndianOceanAnalytics(); // Use enhanced version with all analytics
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

// Make functions globally accessible
window.createStormSurgeChart = createStormSurgeChart;
window.createSeismicChart = createSeismicChart;
window.updateRegionalRiskAssessment = updateRegionalRiskAssessment;
window.manualRefreshAnalytics = manualRefreshAnalytics;
window.refreshAllAnalyticsData = refreshAllAnalyticsData;