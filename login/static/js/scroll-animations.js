// Scroll Animation Observer
class ScrollAnimations {
    constructor() {
        this.init();
    }

    init() {
        this.createObserver();
        this.addAnimationClasses();
    }

    createObserver() {
        const options = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, options);

        this.observeElements();
    }

    addAnimationClasses() {
        const elements = document.querySelectorAll('.section, .card, .process-item, .heading, .paragraph, .hero-subtitle');
        elements.forEach((el, index) => {
            el.classList.add('scroll-animate');
            el.style.animationDelay = `${index * 0.1}s`;
        });
    }

    observeElements() {
        const animatedElements = document.querySelectorAll('.scroll-animate');
        animatedElements.forEach(el => this.observer.observe(el));
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ScrollAnimations();
});