document.addEventListener("DOMContentLoaded", () => {
    const trackerFill = document.getElementById("tracker-fill");
    const labels = document.querySelectorAll(".tracker-labels span");
    let currentStep = 0;

    // Time intervals for each stage in milliseconds
    const intervals = [1000, 5000, 10000, 15000];

    const updateTracker = () => {
        if (currentStep < labels.length) {
            const percentage = ((currentStep + 1) / labels.length) * 100;
            trackerFill.style.width = `${percentage}%`;
            labels[currentStep].style.color = "#ff437b"; // Highlight the current step
            currentStep++;
            if (currentStep < labels.length) {
                setTimeout(updateTracker, intervals[currentStep]);
            }
        }
    };

    // Start tracker animation
    setTimeout(updateTracker, intervals[0]);
});
