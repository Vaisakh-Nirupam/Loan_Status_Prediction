setTimeout(() => {
  const flashes = document.querySelectorAll(".flash");
  flashes.forEach((flash) => {
    flash.style.opacity = 0;
    setTimeout(() => flash.remove(), 500);
  });
}, 3000);
