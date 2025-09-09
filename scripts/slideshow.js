// Change this to control speed between slides (ms)
const SLIDE_INTERVAL = 8000;

const slides = document.querySelectorAll('.mySlides');
if (slides.length > 0) {
  let current = 0;
  let previous = slides.length - 1;

  // initial state
  slides[current].classList.add('active');
  slides[previous].classList.add('prev'); // parked offscreen left

  setInterval(() => {
    // clear old classes
    slides[previous].classList.remove('prev');
    slides[current].classList.remove('active');

    // advance indices
    previous = current;
    current = (current + 1) % slides.length;

    // set new classes to trigger CSS slide
    slides[previous].classList.add('prev');  // current slides out left
    slides[current].classList.add('active'); // next slides in from right
  }, SLIDE_INTERVAL);
}
