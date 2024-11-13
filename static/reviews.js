document.addEventListener("DOMContentLoaded", () => {
    const reviewModal = document.getElementById("review-modal");
    const createReviewBtn = document.getElementById("create-review-btn");
    const closeModal = document.querySelector(".close");

    createReviewBtn.addEventListener("click", () => {
        reviewModal.style.display = "block";
    });

    closeModal.addEventListener("click", () => {
        reviewModal.style.display = "none";
    });

    window.addEventListener("click", (event) => {
        if (event.target === reviewModal) {
            reviewModal.style.display = "none";
        }
    });

    // Star rating logic
    const stars = document.querySelectorAll('.star-rating-container .star');
    stars.forEach(star => {
        star.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            document.getElementById('rating').value = value;
            stars.forEach(star => {
                if (star.getAttribute('data-value') <= value) {
                    star.src = '/static/Images_Videos/icons8-star-50-3.png';
                } else {
                    star.src = '/static/Images_Videos/icons8-star-50-2.png';
                }
            });
        });
    });
});
