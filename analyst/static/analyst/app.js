// Global application state
let currentSection = 'dashboard';
let charts = {};
let realTimeInterval = null;

// Application data from provided JSON
const appData = {
    user_profile: {
        name: "iron",
        role: "Analyst",
        last_login: "2025-09-08T00:22:00Z"
    },
    dashboard_metrics: {
        active_datasets: 142,
        reports_this_month: 28,
        active_stations: 89,
        alert_rate: "97.3%"
    },
    dart_buoys: [
        {id: "21401", lat: 30.515, lon: -148.169, status: "active", last_reading: "2025-09-08T00:20:00Z", wave_height: 2.1, pressure: 1013.2},
        {id: "21413", lat: 42.632, lon: -130.217, status: "active", last_reading: "2025-09-08T00:19:00Z", wave_height: 1.8, pressure: 1014.8},
        {id: "32412", lat: 17.204, lon: -158.006, status: "maintenance", last_reading: "2025-09-07T23:45:00Z", wave_height: null, pressure: null},
        {id: "46407", lat: 38.242, lon: -123.317, status: "active", last_reading: "2025-09-08T00:21:00Z", wave_height: 3.2, pressure: 1012.1}
    ],
    tsunami_events: [
        {date: "2025-09-01", magnitude: 7.2, location: "Alaska Peninsula", max_wave_height: 1.8, alerts_issued: 45, response_time: "4.2 min"},
        {date: "2025-08-15", magnitude: 6.8, location: "Japan Trench", max_wave_height: 0.9, alerts_issued: 23, response_time: "3.8 min"},
        {date: "2025-07-22", magnitude: 7.5, location: "Chile Coast", max_wave_height: 2.3, alerts_issued: 67, response_time: "3.1 min"}
    ],
    performance_metrics: {
        detection_accuracy: 97.3,
        false_alarm_rate: 2.1,
        response_time_avg: 3.7,
        system_uptime: 99.8,
        data_quality_score: 96.5
    },
    regional_risks: [
        {region: "Pacific Northwest", tsunami_risk: "high", storm_surge_risk: "medium", overall_score: 8.2},
        {region: "Gulf Coast", tsunami_risk: "low", storm_surge_risk: "very_high", overall_score: 8.9},
        {region: "East Coast", tsunami_risk: "low", storm_surge_risk: "high", overall_score: 6.8},
        {region: "Caribbean", tsunami_risk: "medium", storm_surge_risk: "high", overall_score: 7.5}
    ]
};

// Chart colors matching design system
const chartColors = ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5', '#5D878F', '#DB4545', '#D2BA4C', '#964325', '#944454', '#13343B'];

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupNavigation();
    setupEventListeners();
    initializeDashboard();
    startRealTimeUpdates();
    updateCurrentTime();
}

function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            const sectionName = this.dataset.section;
            switchSection(sectionName);
        });
    });
}

function setupEventListeners() {
    // Alert banner close
    const alertClose = document.querySelector('.alert-close');
    if (alertClose) {
        alertClose.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    }

    // Report generation
    const generateReportBtn = document.getElementById('generate-report-btn');
    if (generateReportBtn) {
        generateReportBtn.addEventListener('click', generateNewReport);
    }

    // Template selection
    const templateBtns = document.querySelectorAll('[data-template]');
    templateBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            selectReportTemplate(this.dataset.template);
        });
    });

    // Export buttons
    document.querySelectorAll('.export-options .btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.textContent.toLowerCase();
            handleExportAction(action);
        });
    });

    // Update notification
    const notificationAction = document.querySelector('.notification-action');
    if (notificationAction) {
        notificationAction.addEventListener('click', function() {
            refreshData();
            hideNotification();
        });
    }
}

function switchSection(sectionName) {
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
            initializeAnalytics();
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

function initializeDashboard() {
    createTsunamiActivityChart();
    createPerformanceChart();
    updateMetrics();
}

function createTsunamiActivityChart() {
    const ctx = document.getElementById('tsunami-activity-chart');
    if (!ctx) return;

    // Destroy existing chart
    if (charts.tsunamiActivity) {
        charts.tsunamiActivity.destroy();
    }

    const data = appData.tsunami_events.map(event => ({
        x: event.date,
        y: event.magnitude
    }));

    charts.tsunamiActivity = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Magnitude',
                data: data,
                borderColor: chartColors[0],
                backgroundColor: chartColors[0] + '20',
                borderWidth: 3,
                pointRadius: 6,
                pointHoverRadius: 8,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        parser: 'YYYY-MM-DD',
                        displayFormats: {
                            day: 'MMM DD'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Magnitude'
                    },
                    min: 6,
                    max: 8
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function createPerformanceChart() {
    const ctx = document.getElementById('performance-chart');
    if (!ctx) return;

    if (charts.performance) {
        charts.performance.destroy();
    }

    const metrics = appData.performance_metrics;
    
    charts.performance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Detection Accuracy', 'System Uptime', 'Data Quality', 'Response Performance'],
            datasets: [{
                data: [
                    metrics.detection_accuracy,
                    metrics.system_uptime,
                    metrics.data_quality_score,
                    100 - metrics.false_alarm_rate
                ],
                backgroundColor: [chartColors[0], chartColors[1], chartColors[2], chartColors[4]],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function initializeAnalytics() {
    createDartBuoyChart();
    createStormSurgeChart();
    createSeismicChart();
}

function createDartBuoyChart() {
    const ctx = document.getElementById('dart-buoy-chart');
    if (!ctx) return;

    if (charts.dartBuoy) {
        charts.dartBuoy.destroy();
    }

    // Generate time series data for active buoys
    const timeLabels = [];
    const now = new Date();
    for (let i = 23; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60 * 60 * 1000);
        timeLabels.push(time.toISOString().substr(11, 5));
    }

    const datasets = appData.dart_buoys
        .filter(buoy => buoy.status === 'active')
        .map((buoy, index) => ({
            label: `Buoy ${buoy.id}`,
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
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

function createStormSurgeChart() {
    const ctx = document.getElementById('storm-surge-chart');
    if (!ctx) return;

    if (charts.stormSurge) {
        charts.stormSurge.destroy();
    }

    // Simulate storm surge forecast data
    const forecastHours = [];
    const gulfCoastData = [];
    const eastCoastData = [];
    
    for (let i = 0; i < 48; i++) {
        forecastHours.push(`${i}h`);
        gulfCoastData.push(Math.max(0, 4.2 * Math.sin((i - 12) * Math.PI / 24) + Math.random() * 0.5));
        eastCoastData.push(Math.max(0, 2.8 * Math.sin((i - 18) * Math.PI / 30) + Math.random() * 0.3));
    }

    charts.stormSurge = new Chart(ctx, {
        type: 'line',
        data: {
            labels: forecastHours,
            datasets: [{
                label: 'Gulf Coast',
                data: gulfCoastData,
                borderColor: chartColors[2],
                backgroundColor: chartColors[2] + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }, {
                label: 'East Coast',
                data: eastCoastData,
                borderColor: chartColors[1],
                backgroundColor: chartColors[1] + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Forecast Hours'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Surge Height (m)'
                    },
                    min: 0
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

function createSeismicChart() {
    const ctx = document.getElementById('seismic-chart');
    if (!ctx) return;

    if (charts.seismic) {
        charts.seismic.destroy();
    }

    // Generate seismic activity correlation data
    const seismicData = [];
    const tsunamiData = [];
    
    for (let i = 0; i < 30; i++) {
        const magnitude = 5.5 + Math.random() * 2.5;
        const tsunamiRisk = Math.max(0, (magnitude - 6.5) * 2 + Math.random() * 0.5);
        seismicData.push({x: i, y: magnitude});
        tsunamiData.push({x: i, y: tsunamiRisk});
    }

    charts.seismic = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Seismic Magnitude',
                data: seismicData,
                backgroundColor: chartColors[0],
                borderColor: chartColors[0],
                pointRadius: 6,
                yAxisID: 'y'
            }, {
                label: 'Tsunami Risk',
                data: tsunamiData,
                backgroundColor: chartColors[2],
                borderColor: chartColors[2],
                pointRadius: 6,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Days'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Magnitude'
                    },
                    min: 5,
                    max: 8
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Tsunami Risk Score'
                    },
                    min: 0,
                    max: 5,
                    grid: {
                        drawOnChartArea: false,
                    }
                }
            }
        }
    });
}

function initializeStatistics() {
    createAlertDistributionChart();
    createMethodComparisonChart();
    createSeasonalPatternsChart();
    createStationPerformanceChart();
}

function createAlertDistributionChart() {
    const ctx = document.getElementById('alert-distribution-chart');
    if (!ctx) return;

    if (charts.alertDistribution) {
        charts.alertDistribution.destroy();
    }

    charts.alertDistribution = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Tsunami Watch', 'Storm Surge', 'Seismic Alert', 'Maintenance', 'Weather Warning'],
            datasets: [{
                label: 'Alerts This Month',
                data: [12, 18, 35, 8, 22],
                backgroundColor: [chartColors[0], chartColors[1], chartColors[2], chartColors[3], chartColors[4]],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Alerts'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function createMethodComparisonChart() {
    const ctx = document.getElementById('method-comparison-chart');
    if (!ctx) return;

    if (charts.methodComparison) {
        charts.methodComparison.destroy();
    }

    charts.methodComparison = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Accuracy', 'Speed', 'Reliability', 'Coverage', 'Cost Efficiency'],
            datasets: [{
                label: 'DART Buoys',
                data: [95, 85, 92, 78, 70],
                borderColor: chartColors[0],
                backgroundColor: chartColors[0] + '20',
                borderWidth: 2
            }, {
                label: 'Seismic Network',
                data: [88, 98, 85, 95, 85],
                borderColor: chartColors[1],
                backgroundColor: chartColors[1] + '20',
                borderWidth: 2
            }, {
                label: 'Coastal Gauges',
                data: [92, 75, 88, 82, 90],
                borderColor: chartColors[2],
                backgroundColor: chartColors[2] + '20',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function createSeasonalPatternsChart() {
    const ctx = document.getElementById('seasonal-patterns-chart');
    if (!ctx) return;

    if (charts.seasonalPatterns) {
        charts.seasonalPatterns.destroy();
    }

    charts.seasonalPatterns = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'Tsunami Events',
                data: [2, 1, 3, 2, 4, 3, 5, 8, 6, 4, 2, 3],
                borderColor: chartColors[0],
                backgroundColor: chartColors[0] + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }, {
                label: 'Storm Surge Events',
                data: [8, 6, 4, 5, 7, 12, 15, 18, 16, 12, 9, 7],
                borderColor: chartColors[1],
                backgroundColor: chartColors[1] + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Events'
                    }
                }
            }
        }
    });
}

function createStationPerformanceChart() {
    const ctx = document.getElementById('station-performance-chart');
    if (!ctx) return;

    if (charts.stationPerformance) {
        charts.stationPerformance.destroy();
    }

    charts.stationPerformance = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Station Performance',
                data: [
                    {x: 95, y: 98, r: 15},
                    {x: 88, y: 92, r: 12},
                    {x: 92, y: 95, r: 18},
                    {x: 85, y: 88, r: 10},
                    {x: 96, y: 97, r: 20},
                    {x: 89, y: 91, r: 14},
                    {x: 94, y: 96, r: 16}
                ],
                backgroundColor: chartColors[0] + '60',
                borderColor: chartColors[0],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Data Quality (%)'
                    },
                    min: 80,
                    max: 100
                },
                y: {
                    title: {
                        display: true,
                        text: 'Uptime (%)'
                    },
                    min: 85,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Quality: ${context.parsed.x}%, Uptime: ${context.parsed.y}%`;
                        }
                    }
                }
            }
        }
    });
}

function initializeReports() {
    // Report initialization logic here
    console.log('Reports section initialized');
}

function initializeDataManagement() {
    // Data management initialization logic here
    console.log('Data management section initialized');
}

function generateWaveData(baseHeight, points) {
    const data = [];
    for (let i = 0; i < points; i++) {
        // Generate realistic wave data with some variation
        const variation = (Math.random() - 0.5) * 0.5;
        const periodicVariation = Math.sin(i * Math.PI / 6) * 0.3;
        data.push(Math.max(0, baseHeight + variation + periodicVariation));
    }
    return data;
}

function updateMetrics() {
    // Simulate small changes in metrics
    const metrics = appData.dashboard_metrics;
    
    // Update with slight variations
    document.querySelector('.metric-value').textContent = metrics.active_datasets + Math.floor(Math.random() * 3);
}

function startRealTimeUpdates() {
    // Update every 30 seconds
    realTimeInterval = setInterval(() => {
        updateRealTimeData();
        showUpdateNotification();
    }, 30000);
}

function updateRealTimeData() {
    // Simulate real-time data updates
    appData.dart_buoys.forEach(buoy => {
        if (buoy.status === 'active' && buoy.wave_height) {
            // Add small random variation to wave height
            const variation = (Math.random() - 0.5) * 0.2;
            buoy.wave_height = Math.max(0, buoy.wave_height + variation);
        }
    });

    // Update charts if in analytics section
    if (currentSection === 'analytics') {
        createDartBuoyChart();
    }
}

function showUpdateNotification() {
    const notification = document.getElementById('update-notification');
    if (notification) {
        notification.classList.remove('hidden');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            hideNotification();
        }, 5000);
    }
}

function hideNotification() {
    const notification = document.getElementById('update-notification');
    if (notification) {
        notification.classList.add('hidden');
    }
}

function refreshData() {
    // Refresh current section data
    switch(currentSection) {
        case 'dashboard':
            initializeDashboard();
            break;
        case 'analytics':
            initializeAnalytics();
            break;
        case 'statistics':
            initializeStatistics();
            break;
    }
}

function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: '2-digit'
    }) + ' ' + now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
    });
    
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        timeElement.textContent = timeString;
    }

    // Update every minute
    setTimeout(updateCurrentTime, 60000);
}

function generateNewReport() {
    alert('Report generation initiated. This would open a report creation wizard in a full implementation.');
}

function selectReportTemplate(templateType) {
    alert(`Selected ${templateType} template. This would open the template editor in a full implementation.`);
}

function handleExportAction(action) {
    if (action.includes('pdf')) {
        alert('Exporting as PDF... This would generate a PDF report in a full implementation.');
    } else if (action.includes('data')) {
        alert('Exporting data... This would download CSV/JSON data in a full implementation.');
    } else if (action.includes('schedule')) {
        alert('Opening schedule dialog... This would show scheduling options in a full implementation.');
    } else if (action.includes('share')) {
        alert('Opening share dialog... This would show team sharing options in a full implementation.');
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (realTimeInterval) {
        clearInterval(realTimeInterval);
    }
    
    // Destroy all charts
    Object.values(charts).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });
});

// Handle responsive sidebar toggle (for mobile)
function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('open');
}

// Global error handler for charts
window.addEventListener('error', function(e) {
    console.error('Chart error:', e.error);
});

// Initialize charts after Chart.js loads
if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = 'FKGroteskNeue, Inter, sans-serif';
    Chart.defaults.color = '#626C71';
}

function toggleReportForm() {
    const form = document.getElementById('create-report-form');
    const isVisible = form.style.display !== 'none';
    form.style.display = isVisible ? 'none' : 'block';
    
    if (!isVisible) {
        form.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function showSubmitForm(reportId) {
    document.getElementById('submit-form-' + reportId).style.display = 'block';
}

function hideSubmitForm(reportId) {
    document.getElementById('submit-form-' + reportId).style.display = 'none';
}

// Auto-refresh report status
function refreshReportStatus() {
    document.querySelectorAll('.report-card[data-report-id]').forEach(function(card) {
        const reportId = card.dataset.reportId;
        fetch(`/analyst/api/report-status/${reportId}/`)
            .then(response => response.json())
            .then(data => {
                const badge = card.querySelector('.status-badge');
                badge.textContent = data.status_display;
                badge.className = `status-badge status-${data.status}`;
            })
            .catch(error => console.error('Error:', error));
    });
}

// Refresh status every 30 seconds
setInterval(refreshReportStatus, 30000);
// Chart.js: Recent Tsunami Activity Chart
document.addEventListener('DOMContentLoaded', function() {
    var ctx = document.getElementById('tsunami-activity32-chart').getContext('2d');
    var seismicChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Sep 01', 'Sep 03', 'Sep 05', 'Sep 07', 'Sep 09', 'Sep 11', 'Sep 13'],
            datasets: [{
                label: 'Tsunami Events',
                data: [0, 1, 0, 2, 1, 0, 1],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(255, 205, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(201, 203, 207, 0.7)'
                ],
                borderColor: 'rgba(255,99,132,1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Recent Tsunami Activity (Events per Day)'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Events'
                    },
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
});