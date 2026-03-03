(function () {
  const navToggle = document.getElementById("navToggle");
  const navMenu = document.getElementById("navMenu");

  if (navToggle && navMenu) {
    navToggle.addEventListener("click", () => {
      navMenu.classList.toggle("show");
    });

    document.addEventListener("click", (event) => {
      if (!navMenu.contains(event.target) && !navToggle.contains(event.target)) {
        navMenu.classList.remove("show");
      }
    });
  }

  const tableRows = document.querySelectorAll("table tbody tr");
  tableRows.forEach((row, idx) => {
    row.style.animation = `fadeSlide 0.3s ease ${idx * 0.04}s both`;
  });
})();
