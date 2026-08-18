document.addEventListener("DOMContentLoaded", () => {

    /* =========================================================
       COMPACT SVG THEME TOGGLE BUTTON (DARK & LIGHT)
    ========================================================= */
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    const themeNavIcon = document.getElementById("themeNavIcon");

    // Load saved theme or default to light theme
    const savedTheme = localStorage.getItem("app_theme") || "light";
    applyTheme(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", (e) => {
            e.preventDefault();
            const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            applyTheme(newTheme);
        });
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("app_theme", theme);

        if (themeNavIcon) {
            if (theme === "dark") {
                themeNavIcon.className = "bi bi-moon-stars-fill";
            } else {
                themeNavIcon.className = "bi bi-sun-fill";
            }
        }
    }


    /* =========================================================
       NAVBAR SCROLL EFFECT
    ========================================================= */
    const navbar = document.getElementById("navbar");
    const updateNavbar = () => {
        if (window.scrollY > 30) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }
    };
    window.addEventListener("scroll", updateNavbar);
    updateNavbar();


    /* =========================================================
       COUNTER ANIMATION
    ========================================================= */
    const counters = document.querySelectorAll("[data-count]");

    const animateCounter = (element) => {
        const target = Number(element.dataset.count);
        const suffix = element.dataset.suffix || "";
        const duration = 1200;
        const startTime = performance.now();

        const update = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const value = Math.floor(target * eased);

            element.textContent = value + suffix;

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        };

        requestAnimationFrame(update);
    };

    const counterObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.5 }
    );

    counters.forEach((counter) => {
        counterObserver.observe(counter);
    });

});
