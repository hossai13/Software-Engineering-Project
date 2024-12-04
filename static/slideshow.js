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

  const adminToolsButton = document.getElementById('admin-tools-btn');
  const adminToolsModal = document.getElementById('admin-tools-modal');
  const closeAdminToolsModal = adminToolsModal?.querySelector('.close');

  if (adminToolsButton) {
      adminToolsButton.addEventListener('click', () => {
          adminToolsModal.style.display = 'block';
      });
  }

  if (closeAdminToolsModal) {
      closeAdminToolsModal.addEventListener('click', () => {
          adminToolsModal.style.display = 'none';
      });

      window.addEventListener('click', (event) => {
          if (event.target === adminToolsModal) {
              adminToolsModal.style.display = 'none';
          }
      });
  }