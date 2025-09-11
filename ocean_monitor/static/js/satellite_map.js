// INCOIS Satellite Map Management System

class INCOISSatelliteMap {
    constructor() {
        this.autoRefreshInterval = null;
        this.isAutoRefreshActive = false;
        this.refreshIntervalMs = 300000; // 5 minutes default
        this.mapLoadingStates = new Map();
        this.apiEndpoints = {
            hazardReports: '/api/hazard-reports/',
            mapConfig: '/api/update-map-config/',
            dashboardStats: '/api/dashboard-stats/',
            endSession: '/api/end-session/'
        };
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.startHealthCheck();
    }

    setupEventListeners() {
        // Map iframe load events
        const iframes = document.querySelectorAll('iframe[id*="satellite"]');
        iframes.forEach(iframe => {
            iframe.addEventListener('load', () => {
                this.handleMapLoad(iframe.id);
            });
            
            iframe.addEventListener('error', () => {
                this.handleMapError(iframe.id);
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey) {
                switch(e.key) {
                    case 'r':
                        e.preventDefault();
                        this.refreshAllMaps();
                        break;
                    case 'a':
                        e.preventDefault();
                        this.toggleAutoRefresh();
                        break;
                }
            }
        });

        // Visibility change handling
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.isAutoRefreshActive) {
                this.pauseAutoRefresh();
            } else if (!document.hidden) {
                this.resumeAutoRefresh();
            }
        });
    }

    handleMapLoad(iframeId) {
        console.log(`✅ Map loaded successfully: ${iframeId}`);
        this.mapLoadingStates.set(iframeId, 'loaded');
        this.updateConnectionStatus('online');
        this.hideLoadingOverlay(iframeId);
    }

    handleMapError(iframeId) {
        console.error(`❌ Map failed to load: ${iframeId}`);
        this.mapLoadingStates.set(iframeId, 'error');
        this.updateConnectionStatus('offline');
        this.showErrorState(iframeId);
    }

    updateConnectionStatus(status) {
        const statusElements = document.querySelectorAll('[data-connection-status]');
        statusElements.forEach(element => {
            element.className = `badge ${status === 'online' ? 'bg-success' : 'bg-danger'}`;
            element.textContent = status === 'online' ? 'Connected' : 'Disconnected';
        });

        // Update navbar indicator if exists
        const navIndicator = document.querySelector('.navbar .status-indicator');
        if (navIndicator) {
            navIndicator.className = `status-indicator ${status === 'online' ? 'status-online' : 'status-offline'}`;
        }
    }

    refreshAllMaps() {
        const iframes = document.querySelectorAll('iframe[id*="satellite"]');
        iframes.forEach(iframe => {
            this.refreshMap(iframe.id);
        });
    }

    refreshMap(iframeId) {
        const iframe = document.getElementById(iframeId);
        if (!iframe) return;

        console.log(`🔄 Refreshing map: ${iframeId}`);
        
        // Show loading overlay
        this.showLoadingOverlay(iframeId);
        
        const currentSrc = iframe.src;
        const newSrc = this.addCacheBuster(currentSrc);
        
        // Clear and reload iframe
        iframe.src = '';
        setTimeout(() => {
            iframe.src = newSrc;
            this.updateLastUpdateTime();
        }, 100);
    }

    addCacheBuster(url) {
        const separator = url.includes('?') ? '&' : '?';
        const timestamp = new Date().getTime();
        const random = Math.random().toString(36).substring(7);
        return `${url}${separator}t=${timestamp}&refresh=${random}`;
    }

    showLoadingOverlay(iframeId) {
        const iframe = document.getElementById(iframeId);
        if (!iframe) return;

        const container = iframe.parentElement;
        let overlay = container.querySelector('.loading-overlay');
        
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="text-center">
                    <div class="loading-spinner mb-2"></div>
                    <div class="text-muted">Loading satellite data...</div>
                </div>
            `;
            container.style.position = 'relative';
            container.appendChild(overlay);
        }
        
        overlay.style.display = 'flex';
    }

    hideLoadingOverlay(iframeId) {
        const iframe = document.getElementById(iframeId);
        if (!iframe) return;

        const container = iframe.parentElement;
        const overlay = container.querySelector('.loading-overlay');
        
        if (overlay) {
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 1000);
        }
    }

    showErrorState(iframeId) {
        const iframe = document.getElementById(iframeId);
        if (!iframe) return;

        const container = iframe.parentElement;
        let errorOverlay = container.querySelector('.error-overlay');
        
        if (!errorOverlay) {
            errorOverlay = document.createElement('div');
            errorOverlay.className = 'loading-overlay error-overlay';
            errorOverlay.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-exclamation-triangle text-danger fa-3x mb-3"></i>
                    <h5>Connection Error</h5>
                    <p class="text-muted">Unable to load satellite data</p>
                    <button class="btn btn-primary btn-sm" onclick="mapManager.refreshMap('${iframeId}')">
                        <i class="fas fa-retry"></i> Retry
                    </button>
                </div>
            `;
            container.appendChild(errorOverlay);
        }
        
        errorOverlay.style.display = 'flex';
    }

    updateLastUpdateTime() {
        const timeElements = document.querySelectorAll('[id*="lastUpdate"]');
        const currentTime = new Date().toLocaleString();
        
        timeElements.forEach(element => {
            element.textContent = currentTime;
        });

        // Animate update indicator
        timeElements.forEach(element => {
            element.style.color = '#28a745';
            setTimeout(() => {
                element.style.color = '';
            }, 2000);
        });
    }

    startAutoRefresh(intervalMs = this.refreshIntervalMs) {
        if (this.autoRefreshInterval) {
            this.stopAutoRefresh();
        }

        this.autoRefreshInterval = setInterval(() => {
            this.refreshAllMaps();
            this.updateDashboardStats();
        }, intervalMs);

        this.isAutoRefreshActive = true;
        console.log(`🚀 Auto-refresh started: ${intervalMs}ms interval`);
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
        this.isAutoRefreshActive = false;
        console.log('⏹️ Auto-refresh stopped');
    }

    pauseAutoRefresh() {
        if (this.isAutoRefreshActive) {
            this.stopAutoRefresh();
            this.wasPausedByVisibility = true;
        }
    }

    resumeAutoRefresh() {
        if (this.wasPausedByVisibility) {
            this.startAutoRefresh();
            this.wasPausedByVisibility = false;
        }
    }

    toggleAutoRefresh() {
        if (this.isAutoRefreshActive) {
            this.stopAutoRefresh();
        } else {
            this.startAutoRefresh();
        }
        
        this.updateAutoRefreshUI();
        return this.isAutoRefreshActive;
    }

    updateAutoRefreshUI() {
        const icons = document.querySelectorAll('[id*="autoRefreshIcon"], [id*="autoIcon"]');
        const buttons = document.querySelectorAll('[id*="autoRefreshBtn"], [id*="autoBtn"]');
        const statuses = document.querySelectorAll('[id*="refreshStatus"], [id*="status"]');
        
        icons.forEach(icon => {
            icon.className = this.isAutoRefreshActive ? 'fas fa-pause' : 'fas fa-play';
        });
        
        buttons.forEach(button => {
            if (button.classList.contains('btn')) {
                button.className = this.isAutoRefreshActive ? 
                    'btn btn-warning btn-sm' : 'btn btn-success btn-sm';
            }
        });
        
        statuses.forEach(status => {
            if (status.classList.contains('badge')) {
                status.className = this.isAutoRefreshActive ? 
                    'badge bg-success' : 'badge bg-secondary';
                status.textContent = this.isAutoRefreshActive ? 'Auto' : 'Manual';
            } else {
                status.textContent = this.isAutoRefreshActive ? 'Auto' : 'Manual';
            }
        });
    }

    async loadInitialData() {
        try {
            // Load dashboard statistics
            await this.updateDashboardStats();
            
            // Load hazard reports for map overlay
            await this.loadHazardReports();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    async updateDashboardStats() {
        try {
            const response = await fetch(this.apiEndpoints.dashboardStats);
            const stats = await response.json();
            
            // Update stat cards if they exist
            this.updateStatCards(stats);
            
        } catch (error) {
            console.error('Error updating dashboard stats:', error);
        }
    }

    updateStatCards(stats) {
        const statElements = {
            'recent_reports': stats.today_reports,
            'critical_reports': stats.critical_reports,
            'unverified_reports': stats.pending_reports,
            'total_reports': stats.total_reports
        };

        Object.entries(statElements).forEach(([key, value]) => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element && value !== undefined) {
                element.textContent = value;
                // Add pulse animation for updates
                element.classList.add('stat-updated');
                setTimeout(() => {
                    element.classList.remove('stat-updated');
                }, 1000);
            }
        });
    }

    async loadHazardReports(filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            const response = await fetch(`${this.apiEndpoints.hazardReports}?${params}`);
            const data = await response.json();
            
            if (data.success) {
                console.log(`📊 Loaded ${data.reports.length} hazard reports`);
                return data.reports;
            }
            
        } catch (error) {
            console.error('Error loading hazard reports:', error);
        }
        
        return [];
    }

    startHealthCheck() {
        // Check satellite feed connectivity every 30 seconds
        setInterval(() => {
            this.checkMapConnectivity();
        }, 30000);
    }

    async checkMapConnectivity() {
        try {
            // Simple connectivity check to NOAA
            const response = await fetch('https://coralreefwatch.noaa.gov/product/vs/map_full.html', { 
                method: 'HEAD',
                mode: 'no-cors',
                cache: 'no-cache'
            });
            this.updateConnectionStatus('online');
        } catch (error) {
            this.updateConnectionStatus('offline');
            console.warn('Satellite feed connectivity issue detected');
        }
    }

    async endSession() {
        try {
            await fetch(this.apiEndpoints.endSession, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                    'Content-Type': 'application/json'
                }
            });
        } catch (error) {
            console.error('Error ending session:', error);
        }
    }
}

// Initialize the satellite map manager
const mapManager = new INCOISSatelliteMap();

// Global functions for backward compatibility and template integration
window.refreshSatelliteMap = function() {
    mapManager.refreshAllMaps();
};

window.toggleAutoRefresh = function() {
    return mapManager.toggleAutoRefresh();
};

window.toggleFullscreen = function() {
    const iframe = document.querySelector('iframe[id*="satellite"]');
    if (!iframe) return;
    
    if (iframe.requestFullscreen) {
        iframe.requestFullscreen();
    } else if (iframe.webkitRequestFullscreen) {
        iframe.webkitRequestFullscreen();
    } else if (iframe.mozRequestFullScreen) {
        iframe.mozRequestFullScreen();
    } else if (iframe.msRequestFullscreen) {
        iframe.msRequestFullscreen();
    }
};

window.exportData = function() {
    // Placeholder for data export functionality
    alert('Data export functionality will be implemented in Phase 2 of the INCOIS project');
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    mapManager.init();
});

// Auto-start refresh after page load
window.addEventListener('load', function() {
    setTimeout(() => {
        if (document.querySelector('iframe[id*="satellite"]')) {
            mapManager.startAutoRefresh();
        }
    }, 5000); // Start after 5 seconds
});

// Handle page unload - end session
window.addEventListener('beforeunload', function() {
    mapManager.endSession();
});