document.addEventListener("DOMContentLoaded", () => {
 const input = document.getElementById("id_mobile");
 const error = document.getElementById("mobileValidationError");
 if (!input || !error) return;
 let checked = false;
 const descriptions = input.getAttribute("aria-describedby") || "";
 function validate() {
  const number = input.value.replace(/[\s()-]/g, "").replace(/^\+91/, "");
  const valid = /^[6-9][0-9]{9}$/.test(number) && input.value.length <= 20;
  error.hidden = valid;
  input.setAttribute("aria-invalid", String(!valid));
  input.setAttribute("aria-describedby", [descriptions, valid ? "" : error.id].filter(Boolean).join(" "));
  return valid;
 }
 input.addEventListener("blur", () => { checked = true; validate(); });
 input.addEventListener("input", () => { if (checked) validate(); });
 input.form.addEventListener("submit", event => {
  checked = true;
  if (!validate()) { event.preventDefault(); input.focus(); }
 });
});
