
let countdownTime = new Date().getTime() + 5 * 60 * 1000;
let x = setInterval(function() {
    let now = new Date().getTime();
    let distance = countdownTime - now;
    let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    let seconds = Math.floor((distance % (1000 * 60)) / 1000);
    document.getElementById("timer").innerHTML = minutes + " : " + seconds;
    if (distance < 0) {
        clearInterval(x);
        document.getElementById("timer").innerHTML = "ORDER CANCEL UNAVAILABLE";
        }
    }, 1000);