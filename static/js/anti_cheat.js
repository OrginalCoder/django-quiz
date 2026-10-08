(function () {
  document.body.classList.add("anti-cheat-active");

  const watermark = document.createElement("div");
  watermark.id = "antiCheatWatermark";
  watermark.style.position = "fixed";
  watermark.style.inset = "0";
  watermark.style.pointerEvents = "none";
  watermark.style.zIndex = "999";
  watermark.style.opacity = "0.04";
  watermark.style.display = "flex";
  watermark.style.flexWrap = "wrap";
  watermark.style.alignContent = "space-around";
  watermark.style.justifyContent = "space-around";
  watermark.style.overflow = "hidden";
  watermark.style.userSelect = "none";
  watermark.style.transform = "rotate(-20deg) scale(1.2)";

  for (let i = 0; i < 24; i++) {
    const item = document.createElement("div");
    item.textContent = "DJANGO QUIZ • HIMOYALANGAN TEST • NUSXA OLISH TAQIQLANADI";
    item.style.fontSize = "14px";
    item.style.fontWeight = "bold";
    item.style.color = "#ffffff";
    item.style.padding = "25px 40px";
    watermark.appendChild(item);
  }
  document.body.appendChild(watermark);

  const toast = document.createElement("div");
  toast.id = "antiCheatToast";
  toast.className = "anti-cheat-toast";
  toast.innerHTML = `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
    <span id="antiCheatToastText">Taqiqlangan amal!</span>
  `;
  document.body.appendChild(toast);

  const overlay = document.createElement("div");
  overlay.id = "antiCheatOverlay";
  overlay.className = "anti-cheat-overlay";
  overlay.style.display = "none";
  overlay.innerHTML = `
    <div class="glass-panel" style="max-width: 500px; padding: 2.5rem 2rem; border-color: rgba(239, 68, 68, 0.5); box-shadow: 0 0 45px rgba(239, 68, 68, 0.25);">
      <div style="width: 56px; height: 56px; border-radius: 50%; background: rgba(239, 68, 68, 0.2); color: #f87171; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.25rem;">
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
      </div>
      <h3 style="font-size: 1.25rem; color: #ffffff; margin-bottom: 0.75rem;">Himoyalangan test rejimi!</h3>
      <p style="color: var(--text-dim); font-size: 0.95rem; line-height: 1.5; margin-bottom: 1.75rem;" id="antiCheatOverlayMessage">
        Test vaqtida nusxa olish, skrinshot qilish yoki boshqa ilovalarga o'tish taqiqlanadi.
      </p>
      <button type="button" class="btn btn-primary" id="resumeTestBtn" style="background: linear-gradient(135deg, #ef4444, #dc2626);">
        Testga qaytish
      </button>
    </div>
  `;
  document.body.appendChild(overlay);

  let toastTimeout = null;
  function showToast(message) {
    const textEl = document.getElementById("antiCheatToastText");
    if (textEl) textEl.textContent = message;
    toast.classList.add("show");
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
      toast.classList.remove("show");
    }, 2400);
  }

  function clearClipboard() {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText("");
      }
    } catch (_) {}
  }

  const appContainer = document.querySelector(".quiz-container, #tournamentApp, #battleRoomApp, main");

  function triggerBlurOverlay(msg) {
    if (appContainer) appContainer.classList.add("anti-cheat-blur");
    const msgEl = document.getElementById("antiCheatOverlayMessage");
    if (msgEl && msg) msgEl.textContent = msg;
    overlay.style.display = "flex";
  }

  function removeBlurOverlay() {
    if (appContainer) appContainer.classList.remove("anti-cheat-blur");
    overlay.style.display = "none";
  }

  document.getElementById("resumeTestBtn").addEventListener("click", () => {
    removeBlurOverlay();
  });

  window.addEventListener("blur", () => {
    clearClipboard();
    triggerBlurOverlay("Test oynasidan chiqish yoki skrinshot vositalaridan foydalanish taqiqlanadi!");
  });

  window.addEventListener("pagehide", () => {
    clearClipboard();
    triggerBlurOverlay("Sahifadan chiqish taqiqlanadi!");
  });

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      clearClipboard();
      triggerBlurOverlay("Boshqa oynaga o'tish yoki skrinshot olish aniqlandi!");
    }
  });

  window.addEventListener("focus", () => {
    setTimeout(removeBlurOverlay, 300);
  });

  document.addEventListener("touchstart", (e) => {
    if (e.touches && e.touches.length >= 3) {
      e.preventDefault();
      clearClipboard();
      triggerBlurOverlay("Mobil skrinshot imo-ishoralari taqiqlanadi!");
      showToast("Ko'p barmoqli skrinshot bloklandi!");
      return false;
    }
  }, { passive: false });

  document.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    showToast("Sichqonchaning o'ng tugmasi bloklangan!");
    return false;
  });

  document.addEventListener("copy", (e) => {
    e.preventDefault();
    clearClipboard();
    showToast("Matndan nusxa olish taqiqlanadi!");
    return false;
  });

  document.addEventListener("cut", (e) => {
    e.preventDefault();
    clearClipboard();
    showToast("Kesib olish taqiqlanadi!");
    return false;
  });

  document.addEventListener("paste", (e) => {
    e.preventDefault();
    return false;
  });

  document.addEventListener("selectstart", (e) => {
    e.preventDefault();
    return false;
  });

  document.addEventListener("dragstart", (e) => {
    e.preventDefault();
    return false;
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "F12") {
      e.preventDefault();
      e.stopPropagation();
      showToast("Dasturchi vositalari (F12) taqiqlangan!");
      return false;
    }

    if (e.ctrlKey && e.shiftKey && ["I", "J", "C", "i", "j", "c"].includes(e.key)) {
      e.preventDefault();
      e.stopPropagation();
      showToast("Inspektor vositalari taqiqlangan!");
      return false;
    }

    if (e.ctrlKey && ["u", "U"].includes(e.key)) {
      e.preventDefault();
      e.stopPropagation();
      showToast("Sahifa kodini ko'rish taqiqlangan!");
      return false;
    }

    if (e.ctrlKey && ["s", "S", "p", "P"].includes(e.key)) {
      e.preventDefault();
      e.stopPropagation();
      showToast("Sahifani saqlash yoki chop etish taqiqlangan!");
      return false;
    }

    if (e.key === "PrintScreen" || (e.shiftKey && (e.metaKey || e.ctrlKey) && ["s", "S"].includes(e.key))) {
      e.preventDefault();
      clearClipboard();
      triggerBlurOverlay("Skrinshot olish qat'iyan taqiqlanadi!");
      showToast("Skrinshot olish bloklandi!");
      return false;
    }
  });

  document.addEventListener("keyup", (e) => {
    if (e.key === "PrintScreen") {
      clearClipboard();
      triggerBlurOverlay("Skrinshot olish qat'iyan taqiqlanadi!");
      showToast("Skrinshot olish bloklandi!");
    }
  });
})();
