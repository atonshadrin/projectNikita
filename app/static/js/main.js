// ===== SLIDER =====
(function() {
    const slider = document.getElementById('heroSlider');
    if (!slider) return;
    const slides = slider.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.slider-dots .dot');
    let current = 0;
    let timer = null;

    function goTo(idx) {
        slides[current].classList.remove('active');
        if (dots[current]) dots[current].classList.remove('active');
        current = (idx + slides.length) % slides.length;
        slides[current].classList.add('active');
        if (dots[current]) dots[current].classList.add('active');
    }

    function startTimer() {
        clearInterval(timer);
        timer = setInterval(() => goTo(current + 1), 5000);
    }

    const prevBtn = document.getElementById('sliderPrev');
    const nextBtn = document.getElementById('sliderNext');
    if (prevBtn) prevBtn.addEventListener('click', () => { goTo(current - 1); startTimer(); });
    if (nextBtn) nextBtn.addEventListener('click', () => { goTo(current + 1); startTimer(); });
    dots.forEach((dot, i) => {
        dot.addEventListener('click', () => { goTo(i); startTimer(); });
    });

    // Touch support
    let touchStartX = 0;
    slider.addEventListener('touchstart', e => { touchStartX = e.changedTouches[0].clientX; }, { passive: true });
    slider.addEventListener('touchend', e => {
        const diff = touchStartX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 50) { goTo(diff > 0 ? current + 1 : current - 1); startTimer(); }
    });

    startTimer();
})();

// ===== MOBILE NAV =====
const hamburger = document.getElementById('hamburger');
const mainNav = document.querySelector('.main-nav');
if (hamburger && mainNav) {
    hamburger.addEventListener('click', function() {
        mainNav.classList.toggle('open');
        const spans = this.querySelectorAll('span');
        this.classList.toggle('active');
        if (this.classList.contains('active')) {
            spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
        } else {
            spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
        }
    });
    mainNav.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => {
            mainNav.classList.remove('open');
            hamburger.classList.remove('active');
            hamburger.querySelectorAll('span').forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
        });
    });
}

// ===== FLASH CLOSE =====
document.querySelectorAll('.flash-close').forEach(btn => {
    btn.addEventListener('click', () => {
        btn.closest('.flash').style.animation = 'slideOut .3s ease forwards';
        setTimeout(() => btn.closest('.flash').remove(), 300);
    });
});
// Auto-close flashes after 5s
setTimeout(() => {
    document.querySelectorAll('.flash').forEach(f => {
        f.style.animation = 'slideOut .3s ease forwards';
        setTimeout(() => f.remove(), 300);
    });
}, 5000);

// ===== TOGGLE PASSWORD =====
document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', function() {
        const input = this.previousElementSibling;
        if (input.type === 'password') {
            input.type = 'text';
            this.innerHTML = '<i class="fas fa-eye-slash"></i>';
        } else {
            input.type = 'password';
            this.innerHTML = '<i class="fas fa-eye"></i>';
        }
    });
});

// ===== CURRENT DATE =====
const dateEl = document.getElementById('current-date');
if (dateEl) {
    const now = new Date();
    const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    dateEl.textContent = now.toLocaleDateString('ru-RU', opts);
}

// ===== SLIDE OUT ANIMATION =====
const style = document.createElement('style');
style.textContent = '@keyframes slideOut { to { transform: translateX(120%); opacity: 0; } }';
document.head.appendChild(style);
