document.addEventListener("DOMContentLoaded", function () {
    let slideIndex = 0; 
    const slides = document.querySelectorAll(".slide");
    const totalSlides = slides.length;

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.remove("active");
            slide.style.opacity = "0";
        });
        slides[index].classList.add("active"); 
        slides[index].style.opacity = "1";
    }

    function changeSlide(direction) {
        slideIndex = (slideIndex + direction + totalSlides) % totalSlides; 
        showSlide(slideIndex);
        resetInterval();
    }

    function autoSlide() {
        changeSlide(1);
    }
    let slideInterval = setInterval(autoSlide, 3000);

    function resetInterval() {
        clearInterval(slideInterval);
        slideInterval = setInterval(autoSlide, 3000);
    }

    
    document.querySelector(".prev").addEventListener("click", () => changeSlide(-1));
    document.querySelector(".next").addEventListener("click", () => changeSlide(1));

    showSlide(slideIndex);
});


function searchWorkers() {
    const searchInput = document.getElementById('location').value.toLowerCase(); 
    const cards = document.querySelectorAll('.business-card'); 

    cards.forEach(card => {
        const workerTitle = card.querySelector('h3').textContent.toLowerCase(); 

        if (workerTitle.includes(searchInput)) {
            card.style.display = 'block'; 
        } else {
            card.style.display = 'none';
        }
    });
}


