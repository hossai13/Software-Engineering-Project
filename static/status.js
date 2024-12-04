document.addEventListener("DOMContentLoaded", () => {

    const trackerSections = document.querySelectorAll(".tracker-bar div");
    let currentStep = 0;

    const intervals = [1000, 5000, 10000, 15000];

    const updateTracker = () => {
        if (currentStep < trackerSections.length) {
            trackerSections[currentStep].classList.add("active");
            currentStep++;
            if (currentStep < trackerSections.length) {
                setTimeout(updateTracker, intervals[currentStep - 1]); 
            }
        }
    };

    setTimeout(updateTracker, intervals[0]);
    var textWrapper = document.querySelector('.animation');
    textWrapper.innerHTML = textWrapper.textContent.replace(/\S/g, "<span class='letter'>$&</span>");

    anime.timeline({loop: true})
    .add({
        targets: '.animation .letter',
        translateY: [-100,0],
        easing: "easeOutExpo",
        duration: 2000,
        delay: (el, i) => 30 * i
    }).add({
        targets: '.animation',
        opacity: 0,
        duration: 1000,
        easing: "easeOutExpo",
        delay: 1000
    });
});
