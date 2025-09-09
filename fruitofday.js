const slides = document.querySelectorAll('.mySlidesHome');
if (slides.length > 0) {
  // Get last shown index from localStorage, default to -1
  let lastIndex = Number(localStorage.getItem("lastSlideIndex"));
  if (isNaN(lastIndex)) lastIndex = -1;

  // Advance to the next slide, wrap around with modulo
  let current = (lastIndex + 1) % slides.length;
  let previous = (current - 1 + slides.length) % slides.length;

  // Save the new index for next reload
  localStorage.setItem("lastSlideIndex", current);

  // Apply classes
  slides[current].classList.add("active");
  slides[previous].classList.add("prev");
}

