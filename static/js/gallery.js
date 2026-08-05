/* ═══════════════════════════════════════════════════════
   HiddenYatra — Lightbox Gallery
   Full-screen image viewer with navigation
   ═══════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {
  const lightbox    = document.getElementById("lightbox");
  const lightboxImg = document.getElementById("lightbox-img");
  const lightboxCap = document.getElementById("lightbox-caption");
  const closeBtn    = document.getElementById("lightbox-close");
  const prevBtn     = document.getElementById("lightbox-prev");
  const nextBtn     = document.getElementById("lightbox-next");
  const gallery     = document.getElementById("gallery");

  if (!lightbox || !gallery) return;

  const items = gallery.querySelectorAll(".gallery-item");
  let currentIndex = 0;

  function openLightbox(index) {
    currentIndex = index;
    updateLightboxImage();
    lightbox.classList.add("active");
    document.body.style.overflow = "hidden";
  }

  function closeLightbox() {
    lightbox.classList.remove("active");
    document.body.style.overflow = "";
  }

  function updateLightboxImage() {
    const item = items[currentIndex];
    if (!item) return;
    const img = item.querySelector("img");
    const caption = item.querySelector(".gallery-caption");

    lightboxImg.src = img.src;
    lightboxImg.alt = img.alt;
    lightboxCap.textContent = caption ? caption.textContent : "";

    // Hide prev/next if single image
    if (prevBtn) prevBtn.style.display = items.length > 1 ? "" : "none";
    if (nextBtn) nextBtn.style.display = items.length > 1 ? "" : "none";
  }

  function nextImage() {
    currentIndex = (currentIndex + 1) % items.length;
    updateLightboxImage();
  }

  function prevImage() {
    currentIndex = (currentIndex - 1 + items.length) % items.length;
    updateLightboxImage();
  }

  // Bind gallery item clicks
  items.forEach((item, i) => {
    item.addEventListener("click", () => openLightbox(i));
  });

  // Lightbox controls
  if (closeBtn) closeBtn.addEventListener("click", closeLightbox);
  if (prevBtn)  prevBtn.addEventListener("click", prevImage);
  if (nextBtn)  nextBtn.addEventListener("click", nextImage);

  // Click outside image to close
  lightbox.addEventListener("click", (e) => {
    if (e.target === lightbox) closeLightbox();
  });

  // Keyboard navigation
  document.addEventListener("keydown", (e) => {
    if (!lightbox.classList.contains("active")) return;

    if (e.key === "Escape")     closeLightbox();
    if (e.key === "ArrowRight") nextImage();
    if (e.key === "ArrowLeft")  prevImage();
  });
});
