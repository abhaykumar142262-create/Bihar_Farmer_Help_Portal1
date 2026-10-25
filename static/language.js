(() => {
  const languages = ["en", "hi", "bho"];
  const languageButtons = document.querySelectorAll("[data-language]");
  const toggle = document.getElementById("language-toggle");
  const menu = document.getElementById("language-menu");
  const storedLanguage = localStorage.getItem("farmer-help-language");
  let language = languages.includes(storedLanguage) ? storedLanguage : "en";

  function applyLanguage(nextLanguage) {
    language = languages.includes(nextLanguage) ? nextLanguage : "en";
    localStorage.setItem("farmer-help-language", language);
    document.documentElement.lang = language;

    document.querySelectorAll("[data-en]").forEach((element) => {
      const translation = element.getAttribute(`data-${language}`);
      if (translation !== null) element.textContent = translation;
    });
    document.querySelectorAll("[data-placeholder-en]").forEach((element) => {
      const placeholder = element.getAttribute(`data-placeholder-${language}`);
      if (placeholder !== null) element.placeholder = placeholder;
    });
    document.querySelectorAll("[data-label-en]").forEach((element) => {
      const label = element.getAttribute(`data-label-${language}`);
      if (label !== null) element.setAttribute("aria-label", label);
    });
    languageButtons.forEach((button) => {
      button.setAttribute("aria-checked", String(button.dataset.language === language));
    });
  }

  applyLanguage(language);
  languageButtons.forEach((button) => {
    button.addEventListener("click", () => {
      applyLanguage(button.dataset.language);
      if (menu && toggle) {
        menu.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  });

  if (toggle && menu) {
    toggle.addEventListener("click", () => {
      const isExpanded = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!isExpanded));
      menu.hidden = isExpanded;
    });

    document.addEventListener("click", (event) => {
      if (!toggle.contains(event.target) && !menu.contains(event.target)) {
        toggle.setAttribute("aria-expanded", "false");
        menu.hidden = true;
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !menu.hidden) {
        toggle.setAttribute("aria-expanded", "false");
        menu.hidden = true;
        toggle.focus();
      }
    });
  }
})();
