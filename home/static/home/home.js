document.addEventListener("DOMContentLoaded", () => {

    /*
    =========================================================
    NAVBAR SCROLL EFFECT
    =========================================================
    */

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


    /*
    =========================================================
    REVEAL ANIMATIONS
    =========================================================
    */

    const revealElements =
        document.querySelectorAll(".reveal");

    const revealObserver =
        new IntersectionObserver(
            (entries) => {

                entries.forEach((entry) => {

                    if (entry.isIntersecting) {

                        entry.target.classList.add("visible");

                        revealObserver.unobserve(
                            entry.target
                        );

                    }

                });

            },
            {
                threshold: 0.12
            }
        );


    revealElements.forEach((element) => {
        revealObserver.observe(element);
    });


    /*
    =========================================================
    COUNTER ANIMATION
    =========================================================
    */

    const counters =
        document.querySelectorAll("[data-count]");


    const animateCounter = (element) => {

        const target =
            Number(element.dataset.count);

        const suffix =
            element.dataset.suffix || "";

        const duration = 1200;

        const startTime =
            performance.now();


        const update = (currentTime) => {

            const elapsed =
                currentTime - startTime;

            const progress =
                Math.min(elapsed / duration, 1);

            const eased =
                1 - Math.pow(1 - progress, 3);

            const value =
                Math.floor(target * eased);

            element.textContent =
                value + suffix;


            if (progress < 1) {
                requestAnimationFrame(update);
            }

        };


        requestAnimationFrame(update);

    };


    const counterObserver =
        new IntersectionObserver(
            (entries) => {

                entries.forEach((entry) => {

                    if (entry.isIntersecting) {

                        animateCounter(
                            entry.target
                        );

                        counterObserver.unobserve(
                            entry.target
                        );

                    }

                });

            },
            {
                threshold: 0.5
            }
        );


    counters.forEach((counter) => {
        counterObserver.observe(counter);
    });


    /*
    =========================================================
    MOBILE MENU
    =========================================================
    */

    const mobileMenu =
        document.getElementById("mobileMenu");

    const navLinks =
        document.querySelector(".nav-links");

    if (mobileMenu && navLinks) {

        mobileMenu.addEventListener(
            "click",
            () => {

                navLinks.classList.toggle(
                    "mobile-open"
                );

            }
        );

    }


    /*
    =========================================================
    SMOOTH INTERNAL LINKS
    =========================================================
    */

    document
        .querySelectorAll('a[href^="#"]')
        .forEach((link) => {

            link.addEventListener(
                "click",
                (event) => {

                    const targetId =
                        link.getAttribute("href");

                    if (
                        targetId === "#" ||
                        !targetId
                    ) {
                        return;
                    }

                    const target =
                        document.querySelector(
                            targetId
                        );

                    if (!target) {
                        return;
                    }

                    event.preventDefault();

                    target.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });

                }
            );

        });

});
