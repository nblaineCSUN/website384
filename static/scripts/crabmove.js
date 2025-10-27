document.addEventListener("DOMContentLoaded", () => {
  const crab = document.getElementById("crabmerchant");
  const container = document.getElementById("divider");
  const containerWidth = container.clientWidth;
  const crabWidth = crab.clientWidth;
  let direction = 1; // 1 = moving right, -1 = moving left
  let speed = 1;     // pixels per frame (you can tweak)
  
  function animate() {
    // get current left position
    const currentLeft = parseFloat(getComputedStyle(crab).left);
    let nextLeft = currentLeft + (direction * speed);
    
    // if reaching edges, flip direction
    if (nextLeft + crabWidth >= containerWidth) {
      direction = -1;
      nextLeft = containerWidth - crabWidth;
    } else if (nextLeft <= 0) {
      direction = 1;
      nextLeft = 0;
    }
    
    crab.style.left = nextLeft + "px";
    requestAnimationFrame(animate);
  }
  
  animate();  // start the loop
});
