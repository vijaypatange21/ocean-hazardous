// Text Animation with Anime.js
class TextAnimation {
    constructor() {
        this.init();
    }

    init() {
        this.wrapTextElements();
        this.setupAnimations();
    }

    wrapTextElements() {
        const textElements = document.querySelectorAll('h1, h2, h3, p, .hero-subtitle, .card-heading, .hero-title-metallic');
        textElements.forEach(element => {
            if (!element.closest('.nav-container')) {
                this.wrapLetters(element);
            }
        });
    }

    wrapLetters(element) {
        const text = element.textContent;
        element.innerHTML = text.replace(/\S/g, "<span class='letter'>$&</span>");
        element.classList.add('text-animate');
    }

    setupAnimations() {
        // Hero title animation on load
        setTimeout(() => {
            anime({
                targets: '.hero-title-metallic .letter',
                translateY: [100, 0],
                opacity: [0, 1],
                easing: "easeOutExpo",
                duration: 1400,
                delay: (el, i) => 30 * i
            });
        }, 500);

        // Scroll animations for other elements
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.classList.contains('hero-title-metallic')) {
                    anime({
                        targets: entry.target.querySelectorAll('.letter'),
                        translateY: [50, 0],
                        opacity: [0, 1],
                        easing: "easeOutExpo",
                        duration: 800,
                        delay: (el, i) => 20 * i
                    });
                }
            });
        }, { threshold: 0.3 });

        document.querySelectorAll('.text-animate').forEach(el => {
            if (!el.classList.contains('hero-title-metallic')) {
                observer.observe(el);
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new TextAnimation();
});