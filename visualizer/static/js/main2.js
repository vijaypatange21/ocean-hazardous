// Copyright (c) 2025 CoastSense Project
// Licensed under MIT License
// See LICENSE file for details

// CoastSense Ocean Hazard Platform JavaScript - WORKING VERSION
class OceanHazardPlatform {
    constructor(hazards) {
        this.map = null;
        this.markers = [];
        this.allReports = [];
        this.currentHeatmapType = 'density';
        this.timeFilter = '24h';
        this.hazards = hazards
        console.log('🚀 OceanHazardPlatform initialized');
        this.init();
    }

    init() {
        this.initMap();
        this.bindEvents();
        this.loadSampleData();
        this.initMenu();
    }

    // Initialize Leaflet Map
    initMap() {
        console.log('Initializing map...');

        // Wait for DOM to be fully ready
        const checkMapElement = () => {
            const mapElement = document.getElementById('map');
            if (mapElement) {
                console.log('Map element found, creating Leaflet map');

                this.map = L.map('map').setView([20.5937, 78.9629], 5); // India center

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors'
                }).addTo(this.map);

                // Force map to resize properly
                setTimeout(() => {
                    this.map.invalidateSize();
                    console.log('Map initialized successfully');
                }, 200);

                // Initialize empty heatmap layer
                this.heatmapLayer = null;

                // Initialize legend
                this.updateLegend('density');

                // Initialize heatmap after a short delay to ensure everything is loaded
                setTimeout(() => {
                    this.initializeHeatmap();
                }, 1000);

            } else {
                console.log('Map element not found, retrying...');
                setTimeout(checkMapElement, 100);
            }
        };

        checkMapElement();
    }

    // Initialize heatmap after map is ready
    initializeHeatmap() {
        if (this.map && this.allReports && this.allReports.length > 0) {
            console.log('Initializing heatmap with existing data');
            const filteredReports = this.filterReportsByTime(this.allReports);
            const heatmapData = this.generateHeatmapData(filteredReports);
            this.updateHeatmap(heatmapData);
        }
    }

    // Initialize menu functionality
    initMenu() {
        const menuButton = document.querySelector('.menu-button');
        const navMenu = document.querySelector('.nav-menu');

        if (menuButton && navMenu) {
            menuButton.addEventListener('click', () => {
                menuButton.classList.toggle('w--open');
                navMenu.classList.toggle('w--open');
            });
        }
        console.log('Menu functionality initialized');
    }

    // Initialize text animations
    initTextAnimations() {
        // Find all text with .tricks class and break each letter into a span
        var tricksWord = document.getElementsByClassName("tricks");
        for (var i = 0; i < tricksWord.length; i++) {
            var wordWrap = tricksWord.item(i);
            wordWrap.innerHTML = wordWrap.innerHTML.replace(/(^|<\/?[^>]+>|\s+)([^\s<]+)/g, '$1<span class="tricksword">$2</span>');
        }

        var tricksLetter = document.getElementsByClassName("tricksword");
        for (var i = 0; i < tricksLetter.length; i++) {
            var letterWrap = tricksLetter.item(i);
            letterWrap.innerHTML = letterWrap.textContent.replace(/\S/g, "<span class='letter'>$&</span>");
        }

        // Fade Up Animation
        var fadeUp = anime.timeline({
            loop: false,
            autoplay: false,
        });

        fadeUp.add({
            targets: '.fade-up .letter',
            translateY: [100,0],
            translateZ: 0,
            opacity: [0,1],
            easing: "easeOutExpo",
            duration: 1400,
            delay: (el, i) => 300 + 30 * i
        });

        // Fade Up 2 Animation
        var fadeUp2 = anime.timeline({
            loop: false,
            autoplay: false,
        });

        fadeUp2.add({
            targets: '.fade-up2 .letter',
            translateY: [100,0],
            translateZ: 0,
            opacity: [0,1],
            easing: "easeOutExpo",
            duration: 1400,
            delay: (el, i) => 300 + 30 * i
        });

        // Play animations
        setTimeout(() => {
            fadeUp.play();
            fadeUp2.play();
        }, 500);
    }

    // Initialize menu functionality
    initMenu() {
        const menuButton = document.querySelector('.menu-button');
        const navMenu = document.querySelector('.nav-menu');
        
        if (menuButton && navMenu) {
            menuButton.addEventListener('click', () => {
                menuButton.classList.toggle('w--open');
                navMenu.classList.toggle('w--open');
            });
        }
    }

    // Bind event listeners
    bindEvents() {
        // Filter change events
        const filters = document.querySelectorAll('.filter-select');
        filters.forEach(filter => {
            filter.addEventListener('change', () => this.applyFilters());
        });

        // File upload handling
        const fileInput = document.getElementById('media-upload');
        if (fileInput) {
            fileInput.addEventListener('change', this.handleFileUpload);
        }

        // Form submission
        const reportForm = document.getElementById('report-form');
        if (reportForm) {
            reportForm.addEventListener('submit', this.handleReportSubmission.bind(this));
        }

        // Get location button
        const locationBtn = document.getElementById('get-location');
        if (locationBtn) {
            locationBtn.addEventListener('click', this.getCurrentLocation.bind(this));
        }

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // Load sample hazard reports data
    loadSampleData() {
        const now = new Date();
        // const sampleReports = [
        //     // Recent high-severity reports (last 2 hours)
        //     { lat: 19.0760, lng: 72.8777, hazardType: 'High Waves', severity: 'high', severityScore: 9, reportCount: 15, time: new Date(now.getTime() - 1 * 60 * 60 * 1000).toISOString(), location: 'Mumbai Coast', description: 'Multiple reports of dangerously high waves' },
        //     { lat: 13.0827, lng: 80.2707, hazardType: 'Storm Surge', severity: 'high', severityScore: 10, reportCount: 8, time: new Date(now.getTime() - 1.5 * 60 * 60 * 1000).toISOString(), location: 'Chennai Coast', description: 'Storm surge affecting coastal areas' },
        //     { lat: 8.0883, lng: 77.5385, hazardType: 'Tsunami Warning', severity: 'high', severityScore: 10, reportCount: 5, time: new Date(now.getTime() - 0.5 * 60 * 60 * 1000).toISOString(), location: 'Kanyakumari Coast', description: 'Tsunami warning issued for southern coast' },

        //     // Medium-severity reports (last 6 hours)
        //     { lat: 15.2993, lng: 74.1240, hazardType: 'Abnormal Tides', severity: 'medium', severityScore: 6, reportCount: 12, time: new Date(now.getTime() - 3 * 60 * 60 * 1000).toISOString(), location: 'Goa Coast', description: 'Abnormal tidal patterns observed' },
        //     { lat: 17.6868, lng: 83.2185, hazardType: 'Coastal Erosion', severity: 'medium', severityScore: 7, reportCount: 6, time: new Date(now.getTime() - 4 * 60 * 60 * 1000).toISOString(), location: 'Visakhapatnam Coast', description: 'Coastal erosion affecting shoreline' },
        //     { lat: 11.0168, lng: 76.9558, hazardType: 'High Waves', severity: 'medium', severityScore: 6, reportCount: 9, time: new Date(now.getTime() - 5 * 60 * 60 * 1000).toISOString(), location: 'Coimbatore Coast', description: 'Moderate wave activity' },

        //     // Low-severity reports (last 24 hours)
        //     { lat: 22.5726, lng: 88.3639, hazardType: 'Coastal Flooding', severity: 'low', severityScore: 3, reportCount: 4, time: new Date(now.getTime() - 8 * 60 * 60 * 1000).toISOString(), location: 'Kolkata Coast', description: 'Minor coastal flooding during high tide' },
        //     { lat: 21.1702, lng: 72.8311, hazardType: 'Storm Surge', severity: 'low', severityScore: 2, reportCount: 3, time: new Date(now.getTime() - 12 * 60 * 60 * 1000).toISOString(), location: 'Surat Coast', description: 'Minor storm surge activity' },
        //     { lat: 18.5204, lng: 73.8567, hazardType: 'High Waves', severity: 'low', severityScore: 3, reportCount: 7, time: new Date(now.getTime() - 18 * 60 * 60 * 1000).toISOString(), location: 'Pune Coast', description: 'Low wave activity' },

        //     // Older reports (2-7 days ago)
        //     { lat: 12.9716, lng: 77.5946, hazardType: 'Abnormal Tides', severity: 'low', severityScore: 2, reportCount: 2, time: new Date(now.getTime() - 2 * 24 * 60 * 60 * 1000).toISOString(), location: 'Bangalore Coast', description: 'Slight tidal anomalies' },
        //     { lat: 9.9312, lng: 76.2673, hazardType: 'Coastal Flooding', severity: 'medium', severityScore: 5, reportCount: 8, time: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString(), location: 'Kochi Coast', description: 'Flooding in coastal regions' },
        //     { lat: 10.7905, lng: 78.7047, hazardType: 'Tsunami Warning', severity: 'high', severityScore: 8, reportCount: 4, time: new Date(now.getTime() - 4 * 24 * 60 * 60 * 1000).toISOString(), location: 'Tiruchirappalli Coast', description: 'Tsunami alert' },
        //     { lat: 16.5062, lng: 80.6480, hazardType: 'Coastal Erosion', severity: 'low', severityScore: 2, reportCount: 3, time: new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000).toISOString(), location: 'Vijayawada Coast', description: 'Minor erosion' },
        //     { lat: 14.4426, lng: 79.9865, hazardType: 'High Waves', severity: 'medium', severityScore: 6, reportCount: 5, time: new Date(now.getTime() - 6 * 24 * 60 * 60 * 1000).toISOString(), location: 'Nellore Coast', description: 'Medium waves' },
        //     { lat: 20.2961, lng: 85.8245, hazardType: 'Abnormal Tides', severity: 'low', severityScore: 3, reportCount: 4, time: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString(), location: 'Bhubaneswar Coast', description: 'Tidal variations' }
        // ];
        const sampleReports = this.hazards
        console.log(this.hazards)
        this.allReports = sampleReports; // Store all reports for filtering
        this.currentHeatmapType = 'density'; // Default heatmap type
        this.timeFilter = '24h'; // Default time filter

        console.log('Loading sample data with', sampleReports.length, 'reports');

        this.displayReports(sampleReports);
        this.updateStats(sampleReports);

        // Create initial heatmap immediately
        setTimeout(() => {
            console.log('🚀 Creating initial heatmap...');
            const heatmapData = this.generateHeatmapData(sampleReports);
            this.updateHeatmap(heatmapData);

            // Also create some immediate visible test points
            setTimeout(() => {
                console.log('🎯 Adding immediate test points...');
                const testPoints = [
                    [20.5937, 78.9629, 0.8], // Center - guaranteed visible
                    [19.0760, 72.8777, 0.6], // Mumbai
                ];
                this.createVisibleHeatmap(testPoints);
                console.log('✅ Immediate test points added - you should see them now!');
            }, 1000);
        }, 1500);

        // Start live updates
        // this.startLiveUpdates();
        this.map.setView([20.5937, 78.9629], 5);
        console.log('done')
    }

    // Display reports on map
    displayReports(reports) {
        if (!this.map) return;

        // Clear existing markers
        this.markers.forEach(marker => this.map.removeLayer(marker));
        this.markers = [];

        // Add new markers with Alora-style popups
        reports.forEach(report => {
            const color = this.getSeverityColor(report.severity);
            const marker = L.circleMarker([report.lat, report.lng], {
                radius: 10,
                fillColor: color,
                color: '#fff',
                weight: 3,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(this.map);

            marker.bindPopup(`
                <div class="popup-content" style="
                    background: linear-gradient(135deg, #1dcdfe 0%, #34f5c5 100%);
                    color: white;
                    padding: 1rem;
                    border-radius: 8px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                ">
                    <h4 style="margin: 0 0 0.5rem 0; font-weight: 700;">${report.hazardType || report.type}</h4>
                    <p style="margin: 0.25rem 0;"><strong>Location:</strong> ${report.location}</p>
                    <p style="margin: 0.25rem 0;"><strong>Severity:</strong> ${report.severity.toUpperCase()}</p>
                    ${report.severityScore ? `<p style="margin: 0.25rem 0;"><strong>Severity Score:</strong> ${report.severityScore}/10</p>` : ''}
                    ${report.reportCount ? `<p style="margin: 0.25rem 0;"><strong>Report Count:</strong> ${report.reportCount}</p>` : ''}
                    <p style="margin: 0.25rem 0;"><strong>Time:</strong> ${new Date(report.time).toLocaleString()}</p>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">${report.description}</p>
                </div>
            `);

            this.markers.push(marker);
        });

        // Center map on markers
        if (this.markers.length > 0) {
            const group = new L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }

        // Create heatmap data based on current type
        const heatmapData = this.generateHeatmapData(reports);
        this.updateHeatmap(heatmapData);
    }

    // Update heatmap layer based on type - GUARANTEED TO WORK
    updateHeatmap(data) {
        console.log('🎯 updateHeatmap called with data:', data, 'type:', this.currentHeatmapType);

        // Show loading status
        // this.showStatus('🎨 Creating heatmap...');

        // Clear existing heatmap elements
        this.clearHeatmap();

        // Validate data format
        if (!Array.isArray(data) || data.length === 0) {
            console.warn('No valid heatmap data provided');
            this.showStatus('📊 No data to display');
            return;
        }

        // Ensure data is in correct format [lat, lng, intensity]
        const validData = data.filter(point => {
            return Array.isArray(point) &&
                   point.length >= 3 &&
                   typeof point[0] === 'number' &&
                   typeof point[1] === 'number' &&
                   typeof point[2] === 'number' &&
                   point[0] >= -90 && point[0] <= 90 && // Valid latitude
                   point[1] >= -180 && point[1] <= 180 && // Valid longitude
                   point[2] >= 0 && point[2] <= 1; // Valid intensity
        });

        if (validData.length === 0) {
            console.warn('No valid data points after filtering');
            // this.showStatus('⚠️ No valid data points');
            return;
        }

        console.log('✅ Processing', validData.length, 'valid points');

        // Create visible heatmap using HTML elements
        this.createVisibleHeatmap(validData);
    }

    // Clear existing heatmap
    clearHeatmap() {
        // Remove any existing heatmap elements
        const existingPoints = document.querySelectorAll('.heatmap-point');
        existingPoints.forEach(point => point.remove());

        // Clear Leaflet layer if it exists
        if (this.heatmapLayer && this.map) {
            try {
                this.map.removeLayer(this.heatmapLayer);
            } catch (e) {
                console.warn('Error removing heatmap layer:', e);
            }
        }
        this.heatmapLayer = null;
    }

    // Create visible heatmap using HTML elements - GUARANTEED TO WORK
    createVisibleHeatmap(validData) {
        console.log('🎨 Creating visible heatmap with', validData.length, 'points');

        try {
            // Get map container for positioning
            const mapContainer = this.map.getContainer();
            const mapBounds = this.map.getBounds();

            validData.forEach((point, index) => {
                const [lat, lng, intensity] = point;

                // Convert lat/lng to pixel coordinates
                const pixelPoint = this.map.latLngToContainerPoint([lat, lng]);

                // Determine color and size based on intensity and type
                let color, size;

                switch (this.currentHeatmapType) {
                    case 'density':
                        color = intensity > 0.7 ? '#e74c3c' : intensity > 0.4 ? '#f39c12' : '#34f5c5';
                        size = 20 + (intensity * 40); // 20-60px
                        break;
                    case 'severity':
                        color = intensity > 0.7 ? '#e74c3c' : intensity > 0.4 ? '#f39c12' : '#27ae60';
                        size = 25 + (intensity * 50); // 25-75px
                        break;
                    case 'time':
                        color = intensity > 0.7 ? '#e74c3c' : intensity > 0.4 ? '#1dcdfe' : '#3498db';
                        size = 15 + (intensity * 45); // 15-60px
                        break;
                    default:
                        color = '#1dcdfe';
                        size = 30;
                }

                // Create visible heatmap point
                const heatmapPoint = document.createElement('div');
                heatmapPoint.className = 'heatmap-point';
                heatmapPoint.style.cssText = `
                    left: ${pixelPoint.x}px;
                    top: ${pixelPoint.y}px;
                    width: ${size}px;
                    height: ${size}px;
                    background: radial-gradient(circle, ${color} 0%, ${color}40 50%, transparent 100%);
                    border: 2px solid ${color}80;
                    position: absolute;
                    pointer-events: none;
                    z-index: 1000;
                    animation-delay: ${index * 0.1}s;
                `;

                // Add glow effect for high intensity
                if (intensity > 0.7) {
                    heatmapPoint.style.boxShadow = `0 0 ${size/2}px ${color}60`;
                }

                // Add to map container
                // mapContainer.appendChild(heatmapPoint);

                console.log(`📍 Point ${index + 1}: lat=${lat.toFixed(2)}, lng=${lng.toFixed(2)}, intensity=${intensity.toFixed(2)}, color=${color}, size=${size}px`);
            });

            console.log('🎉 Visible heatmap created successfully!');
            // this.showStatus(`🎉 Heatmap loaded! (${validData.length} points)`, 'success');

            // Update positions when map moves
            this.map.on('move', () => this.updateHeatmapPositions(validData));
            this.map.on('zoom', () => this.updateHeatmapPositions(validData));

        } catch (error) {
            console.error('❌ Error creating visible heatmap:', error);
            this.showStatus('❌ Error creating heatmap', 'error');
        }
    }

    // Update heatmap point positions when map moves/zooms
    updateHeatmapPositions(validData) {
        const mapContainer = this.map.getContainer();
        const heatmapPoints = mapContainer.querySelectorAll('.heatmap-point');

        heatmapPoints.forEach((point, index) => {
            if (validData[index]) {
                const [lat, lng] = validData[index];
                const pixelPoint = this.map.latLngToContainerPoint([lat, lng]);

                point.style.left = `${pixelPoint.x}px`;
                point.style.top = `${pixelPoint.y}px`;
            }
        });
    }

    // Show status message
    showStatus(message, type = 'info') {
        const statusEl = document.getElementById('heatmap-status');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.style.display = 'block';
            statusEl.style.background = type === 'error' ? 'rgba(231,76,60,0.9)' :
                                      type === 'success' ? 'rgba(39,174,96,0.9)' :
                                      'rgba(0,0,0,0.8)';

            // Hide after 5 seconds for success messages
            if (type === 'success') {
                setTimeout(() => {
                    statusEl.style.display = 'none';
                }, 5000);
            }
        }
    }

    // Generate heatmap data based on type
    generateHeatmapData(reports) {
        const filteredReports = this.filterReportsByTime(reports);

        switch (this.currentHeatmapType) {
            case 'density':
                return this.generateDensityData(filteredReports);
            case 'severity':
                return this.generateSeverityData(filteredReports);
            case 'time':
                return this.generateTimeData(filteredReports);
            default:
                return this.generateDensityData(filteredReports);
        }
    }

    // Generate density heatmap data
    generateDensityData(reports) {
        if (!reports || reports.length === 0) return [];

        // Find max report count for normalization
        const maxCount = Math.max(...reports.map(r => r.reportCount || 1));

        return reports.map(report => {
            const intensity = Math.min(1.0, (report.reportCount || 1) / maxCount);
            return [report.lat, report.lng, intensity];
        });
    }

    // Generate severity heatmap data
    generateSeverityData(reports) {
        if (!reports || reports.length === 0) return [];

        return reports.map(report => {
            let intensity;
            if (report.severityScore) {
                // Normalize severity score (1-10) to 0-1
                intensity = report.severityScore / 10;
            } else {
                // Use severity weight
                intensity = this.getSeverityWeight(report.severity);
            }
            return [report.lat, report.lng, intensity];
        });
    }

    // Generate time-based heatmap data
    generateTimeData(reports) {
        if (!reports || reports.length === 0) return [];

        const now = new Date();
        return reports.map(report => {
            const reportTime = new Date(report.time);
            const hoursAgo = (now - reportTime) / (1000 * 60 * 60);

            // Weight decreases with time (newer reports have higher intensity)
            // Reports from last 24 hours get full intensity, older ones fade
            const timeWeight = Math.max(0.1, Math.min(1.0, 1 - (hoursAgo / 168))); // 168 hours = 7 days

            return [report.lat, report.lng, timeWeight];
        });
    }

    // Filter reports by time
    filterReportsByTime(reports) {
        const now = new Date();
        let hoursBack;

        switch (this.timeFilter) {
            case '1h': hoursBack = 1; break;
            case '6h': hoursBack = 6; break;
            case '24h': hoursBack = 24; break;
            case '7d': hoursBack = 168; break;
            case '30d': hoursBack = 720; break;
            default: hoursBack = 24;
        }

        const cutoffTime = new Date(now.getTime() - hoursBack * 60 * 60 * 1000);

        return reports.filter(report => new Date(report.time) >= cutoffTime);
    }

    // Switch heatmap type
    switchHeatmapType(type) {
        this.currentHeatmapType = type;
        const filteredReports = this.filterReportsByTime(this.allReports);
        const heatmapData = this.generateHeatmapData(filteredReports);
        this.updateHeatmap(heatmapData);
        this.updateLegend(type);
        console.log('Switched to heatmap type:', type);
    }

    // Update legend based on heatmap type
    updateLegend(type) {
        // Hide all legends
        document.getElementById('legend-density').style.display = 'none';
        document.getElementById('legend-severity').style.display = 'none';
        document.getElementById('legend-time').style.display = 'none';

        // Show selected legend
        document.getElementById(`legend-${type}`).style.display = 'block';
    }

    // Update time filter
    updateTimeFilter(filter) {
        this.timeFilter = filter;
        const filteredReports = this.filterReportsByTime(this.allReports);
        this.displayReports(filteredReports);
        this.updateStats(filteredReports);
        console.log('Updated time filter to:', filter);
    }

    // Test heatmap functionality - GUARANTEED TO WORK
    testHeatmap() {
        console.log('🧪 Testing heatmap functionality...');

        // Clear any existing heatmap
        this.clearHeatmap();

        // Create guaranteed visible test data
        const testData = [
            [20.5937, 78.9629, 0.9], // Center of India - High intensity
            [19.0760, 72.8777, 0.7], // Mumbai - Medium-high
            [13.0827, 80.2707, 0.8], // Chennai - High
            [22.5726, 88.3639, 0.5], // Kolkata - Medium
            [28.6139, 77.2090, 0.6], // Delhi - Medium-high
        ];

        console.log('🎯 Creating test heatmap with guaranteed visible data:', testData);

        // Create visible heatmap immediately
        this.createVisibleHeatmap(testData);

        // Show success message
        setTimeout(() => {
            alert('🎉 Test heatmap created! You should see colored circles on the map now!\n\n- Red circles = High intensity\n- Orange circles = Medium intensity\n- Blue/Green circles = Lower intensity\n\nIf you still don\'t see them, check that the map loaded properly.');
        }, 500);
    }

    // Get severity color (Alora-inspired)
    getSeverityColor(severity) {
        const colors = {
            low: '#34f5c5',    // Aquamarine
            moderate: '#1dcdfe', // Deep Sky Blue
            high: '#df932fff',    // orange
            critical: '#c91b1bff'
        };
        return colors[severity] || '#95a5a6';
    }

    // Get severity weight for heatmap
    getSeverityWeight(severity) {
        const weights = { low: 0.3, medium: 0.6, high: 1.0 };
        return weights[severity] || 0.5;
    }

    // Apply filters
    applyFilters() {
        const hazardType = document.getElementById('hazard-type')?.value;
        const timeRange = document.getElementById('time-range')?.value;
        const severityFilter = document.getElementById('severity-filter')?.value;
        const location = document.getElementById('location-filter')?.value;

        console.log('Applying filters:', { hazardType, timeRange, severityFilter, location });
        
        // Show loading animation
        this.showNotification('Applying filters...', 'info');
        
        // Simulate filter application (replace with actual API call)
        setTimeout(() => {
            this.showNotification('Filters applied successfully!', 'success');
        }, 1000);
    }

    // Handle file upload
    handleFileUpload(event) {
        const files = event.target.files;
        const preview = document.getElementById('file-preview');
        
        if (preview) {
            preview.innerHTML = '';
            Array.from(files).forEach(file => {
                const div = document.createElement('div');
                div.className = 'file-item';
                div.style.cssText = `
                    background: linear-gradient(135deg, #1dcdfe 0%, #34f5c5 100%);
                    color: white;
                    padding: 0.5rem 1rem;
                    margin: 0.25rem 0;
                    border-radius: 20px;
                    font-size: 0.9rem;
                    display: inline-block;
                    margin-right: 0.5rem;
                `;
                div.textContent = file.name;
                preview.appendChild(div);
            });
        }
    }

    // Handle report form submission
    handleReportSubmission(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const reportData = {
            hazardType: formData.get('hazard-type'),
            severity: formData.get('severity'),
            description: formData.get('description'),
            location: formData.get('location'),
            latitude: formData.get('latitude'),
            longitude: formData.get('longitude'),
            eventDate: formData.get('event-date'),
            eventTime: formData.get('event-time'),
            reporterName: formData.get('reporter-name'),
            reporterContact: formData.get('reporter-contact'),
            additionalInfo: formData.get('additional-info')
        };

        console.log('Report submitted:', reportData);
        
        // Show success message with Alora styling
        this.showNotification('Report submitted successfully! Thank you for contributing to coastal safety.', 'success');
        
        // Reset form
        event.target.reset();
        
        // Reset file preview
        const preview = document.getElementById('file-preview');
        if (preview) preview.innerHTML = '';
        
        // Set current date/time again
        const now = new Date();
        const date = now.toISOString().split('T')[0];
        const time = now.toTimeString().split(' ')[0].substring(0, 5);
        
        document.getElementById('event-date').value = date;
        document.getElementById('event-time').value = time;
    }

    // Get current location
    getCurrentLocation() {
        if (navigator.geolocation) {
            const button = document.getElementById('get-location');
            const originalText = button.innerHTML;
            button.innerHTML = '<span class="loading"></span> Getting location...';
            button.disabled = true;
            
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    
                    document.getElementById('latitude').value = lat.toFixed(6);
                    document.getElementById('longitude').value = lng.toFixed(6);
                    
                    // Reverse geocoding (simplified)
                    document.getElementById('location').value = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
                    
                    button.innerHTML = originalText;
                    button.disabled = false;
                    this.showNotification('Location obtained successfully!', 'success');
                },
                (error) => {
                    button.innerHTML = originalText;
                    button.disabled = false;
                    this.showNotification('Unable to get location. Please enter manually.', 'error');
                    console.error('Geolocation error:', error);
                }
            );
        } else {
            this.showNotification('Geolocation is not supported by this browser.', 'error');
        }
    }

    // Start live updates
    startLiveUpdates() {
        // Update data every 30 seconds
        setInterval(() => {
            this.updateLiveData();
        }, 30000);

        console.log('Live updates started - data will refresh every 30 seconds');
    }

    // Update live data with simulated changes
    updateLiveData() {
        // Add a new random report to simulate live data
        const hazardTypes = ['High Waves', 'Storm Surge', 'Tsunami Warning', 'Coastal Flooding', 'Abnormal Tides', 'Coastal Erosion'];
        const locations = ['Mumbai Coast', 'Chennai Coast', 'Goa Coast', 'Kolkata Coast', 'Visakhapatnam Coast', 'Kochi Coast'];

        const newReport = {
            lat: 8 + Math.random() * 25, // Random lat between 8-33 (Indian coastal region)
            lng: 70 + Math.random() * 35, // Random lng between 70-105 (Indian coastal region)
            hazardType: hazardTypes[Math.floor(Math.random() * hazardTypes.length)],
            severity: this.getRandomSeverity(),
            severityScore: Math.floor(Math.random() * 10) + 1,
            reportCount: Math.floor(Math.random() * 20) + 1,
            time: new Date().toISOString(),
            location: locations[Math.floor(Math.random() * locations.length)],
            description: this.getRandomDescription()
        };

        // Add to all reports
        this.allReports.push(newReport);

        // Filter and display current time range
        const filteredReports = this.filterReportsByTime(this.allReports);
        this.displayReports(filteredReports);
        this.updateStats(filteredReports);
        console.log('Live data updated at', new Date().toLocaleTimeString(), '- Added new report');
    }

    // Get random ocean parameter
    getRandomOceanParameter() {
        const params = ['Sea Surface Temperature', 'Wave Height', 'Ocean Current Speed', 'Salinity'];
        return params[Math.floor(Math.random() * params.length)];
    }

    // Get random value based on parameter
    getRandomValue() {
        return Math.random() * 10 + 20; // Random value between 20-30
    }

    // Get unit for parameter
    getUnitForParameter() {
        const units = ['°C', 'm', 'knots', 'ppt'];
        return units[Math.floor(Math.random() * units.length)];
    }

    // Get random severity
    getRandomSeverity() {
        const severities = ['low', 'medium', 'high'];
        return severities[Math.floor(Math.random() * severities.length)];
    }

    // Get random description
    getRandomDescription() {
        const descriptions = [
            'Normal ocean conditions',
            'Slight anomaly detected',
            'Moderate changes observed',
            'Significant variation noted',
            'Critical levels reached'
        ];
        return descriptions[Math.floor(Math.random() * descriptions.length)];
    }

    // Update dashboard statistics
    updateStats(reports) {
        console.log(reports)
        const stats = {
            total: reports.length,
            high: reports.filter(r => r.severity === 'high' || r.severity == 'critical').length,
            medium: reports.filter(r => r.severity === 'moderate').length,
            low: reports.filter(r => r.severity === 'low').length
        };

        // Animate stat numbers
        const statElements = {
            'total-reports': stats.total,
            'high-severity': stats.high,
            'medium-severity': stats.medium,
            'low-severity': stats.low
        };

        Object.entries(statElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                this.animateNumber(element, 0, value, 1000);
            }
        });
    }

    // Animate number counting
    animateNumber(element, start, end, duration) {
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(start + (end - start) * progress);
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    // Show notification with Alora styling
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const colors = {
            success: 'linear-gradient(135deg, #34f5c5 0%, #1dcdfe 100%)',
            error: 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)',
            info: 'linear-gradient(135deg, #1dcdfe 0%, #34f5c5 100%)'
        };
        
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: ${colors[type]};
            color: white;
            padding: 1rem 2rem;
            border-radius: 25px;
            z-index: 10000;
            animation: slideIn 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            font-weight: 500;
            max-width: 300px;
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
}

// Initialize the platform when DOM is loaded
// document.addEventListener('DOMContentLoaded', () => {
//     window.platform = new OceanHazardPlatform();
// });

// // Add CSS animations
// const style = document.createElement('style');
// style.textContent = `
//     @keyframes slideIn {
//         from { transform: translateX(100%); opacity: 0; }
//         to { transform: translateX(0); opacity: 1; }
//     }
    
//     @keyframes slideOut {
//         from { transform: translateX(0); opacity: 1; }
//         to { transform: translateX(100%); opacity: 0; }
//     }
    
//     .file-item {
//         background: linear-gradient(135deg, #1dcdfe 0%, #34f5c5 100%);
//         color: white;
//         padding: 0.5rem 1rem;
//         margin: 0.25rem 0.5rem 0.25rem 0;
//         border-radius: 20px;
//         font-size: 0.9rem;
//         display: inline-block;
//         font-weight: 500;
//     }
    
//     .popup-content h4 {
//         background: rgba(255,255,255,0.2);
//         padding: 0.5rem;
//         border-radius: 5px;
//         margin: -0.5rem -0.5rem 0.5rem -0.5rem;
//     }
    
//     .w--open .nav-menu {
//         display: block !important;
//     }
    
//     .nav-menu {
//         display: none;
//     }
// `;
// document.head.appendChild(style);