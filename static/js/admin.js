/* ═══════════════════════════════════════════════════════
   HiddenYatra — Admin Page JavaScript
   Photo preview, specialty rows, admin map helpers
   ═══════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {

  /* ── Photo Upload Preview ───────────────────────── */
  const photoInput   = document.getElementById("photo-input");
  const photoPreview = document.getElementById("photo-preview");

  if (photoInput && photoPreview) {
    photoInput.addEventListener("change", () => {
      photoPreview.innerHTML = "";
      const files = photoInput.files;

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (!file.type.startsWith("image/")) continue;

        const reader = new FileReader();
        reader.onload = (e) => {
          const img = document.createElement("img");
          img.src = e.target.result;
          img.alt = file.name;
          photoPreview.appendChild(img);
        };
        reader.readAsDataURL(file);
      }
    });
  }


  /* ── Add / Remove Specialty Rows ────────────────── */
  const addSpecBtn = document.getElementById("add-specialty-btn");
  const specContainer = document.getElementById("specialties-container");

  if (addSpecBtn && specContainer) {
    // Get the specialty category options from existing select (if any)
    const existingSelect = specContainer.querySelector("select[name='spec_category[]']");
    let optionsHtml = '<option value="food">🍛 Food</option>';
    if (existingSelect) {
      optionsHtml = existingSelect.innerHTML;
    }

    addSpecBtn.addEventListener("click", () => {
      const row = document.createElement("div");
      row.className = "specialty-form-row";
      row.innerHTML = `
        <input type="text" name="spec_name[]" class="form-input" placeholder="Specialty name">
        <input type="text" name="spec_description[]" class="form-input" placeholder="Description">
        <select name="spec_category[]" class="form-select form-select-sm">
          ${optionsHtml}
        </select>
        <input type="text" name="spec_where[]" class="form-input" placeholder="Where to find">
        <button type="button" class="btn btn-danger btn-sm remove-spec-btn">✕</button>
      `;
      specContainer.appendChild(row);
    });

    // Remove specialty row (event delegation)
    specContainer.addEventListener("click", (e) => {
      if (e.target.classList.contains("remove-spec-btn")) {
        e.target.closest(".specialty-form-row").remove();
      }
    });
  }

});
