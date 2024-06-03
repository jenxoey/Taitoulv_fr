document.addEventListener("DOMContentLoaded", function() {
    const images = document.querySelectorAll('.background-container img');
    let currentIndex = 0;

    function changeBackground() {
        images.forEach((img, index) => {
            img.style.opacity = index === currentIndex ? '1' : '0';
        });
        currentIndex = (currentIndex + 1) % images.length;
    }

    setInterval(changeBackground, 5000);  // Change every 5 seconds
    changeBackground();  // Initialize
});
