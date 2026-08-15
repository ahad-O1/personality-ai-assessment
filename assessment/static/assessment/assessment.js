document.addEventListener("DOMContentLoaded", () => {

    const options = document.querySelectorAll(".answer-option");
    const continueBtn = document.getElementById("continueBtn");
    const form = document.getElementById("assessmentForm");

    if (!options.length || !continueBtn || !form) {
        return;
    }

    continueBtn.disabled = true;

    options.forEach(option => {

        const input = option.querySelector("input");

        option.addEventListener("click", () => {

            options.forEach(item => {
                item.classList.remove("selected");
            });

            option.classList.add("selected");
            input.checked = true;

            continueBtn.disabled = false;
        });

    });

    form.addEventListener("submit", () => {

        continueBtn.disabled = true;

        const text = continueBtn.querySelector("span");

        if (text) {
            text.textContent = "Analyzing response...";
        }

    });

});
