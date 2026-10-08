document.addEventListener("DOMContentLoaded", () => {
  const userMenuBtn = document.getElementById("userMenuBtn");
  const userDropdown = document.getElementById("userDropdown");
  const mobileToggleBtn = document.getElementById("mobileToggleBtn");
  const mobileNavDrawer = document.getElementById("mobileNavDrawer");

  if (userMenuBtn && userDropdown) {
    userMenuBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      userDropdown.classList.toggle("show");
    });

    document.addEventListener("click", (e) => {
      if (!userDropdown.contains(e.target) && !userMenuBtn.contains(e.target)) {
        userDropdown.classList.remove("show");
      }
    });
  }

  if (mobileToggleBtn && mobileNavDrawer) {
    mobileToggleBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      mobileNavDrawer.classList.toggle("active");
    });

    document.addEventListener("click", (e) => {
      if (!mobileNavDrawer.contains(e.target) && !mobileToggleBtn.contains(e.target)) {
        mobileNavDrawer.classList.remove("active");
      }
    });
  }

  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.transition = "opacity 0.4s ease, transform 0.4s ease";
      alert.style.opacity = "0";
      alert.style.transform = "translateY(-8px)";
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });
});
