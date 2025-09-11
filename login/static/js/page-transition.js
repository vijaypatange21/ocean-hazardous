// Page Transition Animation
class PageTransition {
    constructor() {
        this.overlay = null;
        this.video = null;
        this.init();
    }

    init() {
        this.createOverlay();
        this.bindEvents();
    }

    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'page-transition-overlay';
        this.overlay.innerHTML = `
            <video class="transition-video" muted playsinline>
                <source src="../static/media/PageChange.mp4" type="video/mp4">
            </video>
        `;
        document.body.appendChild(this.overlay);
        this.video = this.overlay.querySelector('.transition-video');
    }

    bindEvents() {
        // Bind to all navigation links
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href]');
            if (link && this.shouldTransition(link)) {
                e.preventDefault();
                this.startTransition(link.href);
            }
        });
    }

    shouldTransition(link) {
        const href = link.getAttribute('href');
        // Skip external links, anchors, and javascript links
        return href && 
               !href.startsWith('#') && 
               !href.startsWith('javascript:') && 
               !href.startsWith('mailto:') && 
               !href.startsWith('tel:') &&
               !link.target;
    }

    startTransition(url) {
        this.overlay.classList.add('active');
        this.video.currentTime = 0;
        this.video.playbackRate = 3.2;
        this.video.play();

        // Stop video after 2.5 seconds and navigate
        setTimeout(() => {
            this.video.pause();
            window.location.href = url;
        }, 2500);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PageTransition();
});