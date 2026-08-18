document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("assessmentForm");
    const continueBtn = document.getElementById("continueBtn");
    const options = document.querySelectorAll(".answer-option");

    if (!form || !continueBtn || !options.length) {
        return;
    }

    // Disable continue button until an answer option is selected
    continueBtn.disabled = true;

    options.forEach(option => {
        const input = option.querySelector("input[type='radio']");

        option.addEventListener("click", () => {
            options.forEach(item => {
                item.classList.remove("selected");
            });

            option.classList.add("selected");
            if (input) {
                input.checked = true;
            }

            continueBtn.disabled = false;
        });
    });

    // Show loading state on standard form submit
    form.addEventListener("submit", () => {
        continueBtn.disabled = true;
        const text = continueBtn.querySelector("span");
        if (text) {
            text.textContent = "Analyzing response...";
        }
    });

});
