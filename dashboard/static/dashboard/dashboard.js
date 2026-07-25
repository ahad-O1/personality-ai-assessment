document.addEventListener("DOMContentLoaded", function () {
    const getJsonData = (elementId, fallback = []) => {
        const element = document.getElementById(elementId);

        if (!element) {
            return fallback;
        }

        try {
            return JSON.parse(element.textContent);
        } catch (error) {
            console.error(`Could not parse ${elementId}:`, error);
            return fallback;
        }
    };

    // Sidebar
    const sidebar = document.getElementById("sidebar");
    const menuButton = document.getElementById("menuButton");
    const sidebarOverlay = document.getElementById("sidebarOverlay");

    const closeSidebar = () => {
        sidebar?.classList.remove("open");
        sidebarOverlay?.classList.remove("active");
    };

    menuButton?.addEventListener("click", function () {
        sidebar?.classList.toggle("open");
        sidebarOverlay?.classList.toggle("active");
    });

    sidebarOverlay?.addEventListener("click", closeSidebar);

    // Scroll reveal
    const revealElements = document.querySelectorAll(".reveal");

    const revealObserver = new IntersectionObserver(
        function (entries) {
            entries.forEach(function (entry, index) {
                if (entry.isIntersecting) {
                    setTimeout(function () {
                        entry.target.classList.add("visible");
                    }, index * 70);

                    revealObserver.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.08,
        }
    );

    revealElements.forEach(function (element) {
        revealObserver.observe(element);
    });

    // Animated counters
    const counters = document.querySelectorAll(".animated-counter");

    counters.forEach(function (counter) {
        const target = Number(counter.dataset.target || 0);
        const duration = 1100;
        const startTime = performance.now();

        const updateCounter = function (currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const easedProgress = 1 - Math.pow(1 - progress, 4);
            const value = Math.floor(target * easedProgress);

            counter.textContent = value;

            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };

        requestAnimationFrame(updateCounter);
    });

    // Progress animations
    document.querySelectorAll(".progress-value").forEach(function (bar) {
        const progress = Math.min(
            Math.max(Number(bar.dataset.progress || 0), 0),
            100
        );

        setTimeout(function () {
            bar.style.width = `${progress}%`;
        }, 550);
    });
    document.querySelectorAll(".mini-progress-fill").forEach(function (bar) {
        const width = Math.min(
            Math.max(Number(bar.dataset.width || 0), 0),
            100
        );

        setTimeout(function () {
            bar.style.width = `${width}%`;
        }, 500);
    });
    // Chart data
    const labels = getJsonData("chart-labels");

    const openness = getJsonData("openness-history");
    const conscientiousness = getJsonData(
        "conscientiousness-history"
    );
    const extraversion = getJsonData("extraversion-history");
    const agreeableness = getJsonData("agreeableness-history");
    const neuroticism = getJsonData("neuroticism-history");

    const latestRadarScores = getJsonData(
        "latest-radar-scores",
        [0, 0, 0, 0, 0]
    );

    const careerLabels = getJsonData("career-labels");
    const careerValues = getJsonData("career-values");

    Chart.defaults.font.family = "Inter";
    Chart.defaults.color = "#64748b";

    // OCEAN History Chart
    const oceanCanvas = document.getElementById(
        "oceanHistoryChart"
    );

    if (oceanCanvas) {
        new Chart(oceanCanvas, {
            type: "line",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: "Openness",
                        data: openness,
                        borderColor: "#2563eb",
                        backgroundColor: "rgba(37, 99, 235, 0.08)",
                        tension: 0.4,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                    },
                    {
                        label: "Conscientiousness",
                        data: conscientiousness,
                        borderColor: "#7c3aed",
                        backgroundColor: "rgba(124, 58, 237, 0.08)",
                        tension: 0.4,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                    },
                    {
                        label: "Extraversion",
                        data: extraversion,
                        borderColor: "#059669",
                        backgroundColor: "rgba(5, 150, 105, 0.08)",
                        tension: 0.4,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                    },
                    {
                        label: "Agreeableness",
                        data: agreeableness,
                        borderColor: "#ea580c",
                        backgroundColor: "rgba(234, 88, 12, 0.08)",
                        tension: 0.4,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                    },
                    {
                        label: "Neuroticism",
                        data: neuroticism,
                        borderColor: "#dc2626",
                        backgroundColor: "rgba(220, 38, 38, 0.08)",
                        tension: 0.4,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                    },
                ],
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                animation: {
                    duration: 1500,
                    easing: "easeOutQuart",
                },

                interaction: {
                    mode: "index",
                    intersect: false,
                },

                plugins: {
                    legend: {
                        position: "bottom",

                        labels: {
                            usePointStyle: true,
                            boxWidth: 7,
                            padding: 18,
                            font: {
                                size: 10,
                                weight: "600",
                            },
                        },
                    },

                    tooltip: {
                        backgroundColor: "#0f172a",
                        titleColor: "#ffffff",
                        bodyColor: "#cbd5e1",
                        padding: 12,
                        cornerRadius: 10,
                    },
                },

                scales: {
                    x: {
                        grid: {
                            display: false,
                        },

                        ticks: {
                            font: {
                                size: 9,
                            },
                        },
                    },

                    y: {
                        min: 0,
                        max: 100,

                        ticks: {
                            stepSize: 20,
                            font: {
                                size: 9,
                            },
                        },

                        grid: {
                            color: "rgba(148, 163, 184, 0.13)",
                        },
                    },
                },
            },
        });
    }

    // Radar Chart
    const radarCanvas = document.getElementById(
        "latestRadarChart"
    );

    if (radarCanvas) {
        new Chart(radarCanvas, {
            type: "radar",

            data: {
                labels: [
                    "Openness",
                    "Conscientiousness",
                    "Extraversion",
                    "Agreeableness",
                    "Neuroticism",
                ],

                datasets: [
                    {
                        label: "Latest Profile",
                        data: latestRadarScores,
                        borderColor: "#2563eb",
                        backgroundColor: "rgba(37, 99, 235, 0.2)",
                        pointBackgroundColor: "#2563eb",
                        pointBorderColor: "#ffffff",
                        pointRadius: 4,
                        pointHoverRadius: 7,
                        borderWidth: 2,
                    },
                ],
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                animation: {
                    duration: 1600,
                    easing: "easeOutQuart",
                },

                plugins: {
                    legend: {
                        display: false,
                    },

                    tooltip: {
                        backgroundColor: "#0f172a",
                        padding: 11,
                        cornerRadius: 10,
                    },
                },

                scales: {
                    r: {
                        min: 0,
                        max: 100,

                        ticks: {
                            stepSize: 20,
                            display: false,
                        },

                        pointLabels: {
                            color: "#475569",
                            font: {
                                size: 9,
                                weight: "600",
                            },
                        },

                        grid: {
                            color: "rgba(148, 163, 184, 0.18)",
                        },

                        angleLines: {
                            color: "rgba(148, 163, 184, 0.18)",
                        },
                    },
                },
            },
        });
    }

    // Career Trend Chart
    const careerCanvas = document.getElementById(
        "careerTrendChart"
    );

    if (careerCanvas) {
        new Chart(careerCanvas, {
            type: "bar",

            data: {
                labels: careerLabels,

                datasets: [
                    {
                        label: "Times Recommended",
                        data: careerValues,
                        backgroundColor: [
                            "rgba(37, 99, 235, 0.86)",
                            "rgba(124, 58, 237, 0.82)",
                            "rgba(5, 150, 105, 0.82)",
                            "rgba(234, 88, 12, 0.82)",
                            "rgba(14, 165, 233, 0.82)",
                        ],
                        borderRadius: 9,
                        borderSkipped: false,
                        maxBarThickness: 42,
                    },
                ],
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: "y",

                animation: {
                    duration: 1500,
                    easing: "easeOutQuart",
                },

                plugins: {
                    legend: {
                        display: false,
                    },

                    tooltip: {
                        backgroundColor: "#0f172a",
                        padding: 11,
                        cornerRadius: 10,
                    },
                },

                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0,
                            font: {
                                size: 9,
                            },
                        },
                        grid: {
                            color: "rgba(148, 163, 184, 0.13)",
                        },
                    },

                    y: {
                        grid: {
                            display: false,
                        },

                        ticks: {
                            color: "#334155",
                            font: {
                                size: 10,
                                weight: "600",
                            },
                        },
                    },
                },
            },
        });
    }
});