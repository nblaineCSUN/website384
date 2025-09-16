const slides = document.querySelectorAll('.mySlidesHome');
if (slides.length > 0) {
  // Pick a random slide
  const current = Math.floor(Math.random() * slides.length);
  
  // Show it
  slides[current].classList.add("active");
}


