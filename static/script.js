var animation = lottie.loadAnimation({
    container: document.getElementById('lottie-cart'),
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: '/static/Cart.json'
  });

document.addEventListener('DOMContentLoaded', function() {
  const title = document.querySelector('.title');
  const slideshow = document.querySelector('.slideshow-container');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate');
      }
    });
  });

  observer.observe(title);
  observer.observe(slideshow-container); 
});

let slideIndex = 0;
slideShow();

function slideShow() {
  let i;
  let slides = document.getElementsByClassName("slides");
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  slideIndex++;
  if (slideIndex > slides.length) {slideIndex = 1}
  slides[slideIndex-1].style.display = "block";
  setTimeout(slideShow, 6000);

}
