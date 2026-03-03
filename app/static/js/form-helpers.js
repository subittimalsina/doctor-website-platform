(function () {
  "use strict";

  const patterns = {
    email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    phone: /^[0-9+\-()\s]{7,25}$/,
    strongPassword: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d\W_]{8,}$/,
    slug: /^[a-z0-9-]{3,120}$/,
    numeric: /^\d+$/,
    amount: /^\d+(\.\d{1,2})?$/,
  };

  function toArray(nodeList) {
    return Array.prototype.slice.call(nodeList || []);
  }

  function trim(value) {
    return (value || "").trim();
  }

  function text(el) {
    return trim(el ? el.value : "");
  }

  function addError(el, message) {
    if (!el) {
      return;
    }

    el.classList.add("field-error");
    const existing = el.parentElement.querySelector(".field-error-message");
    if (existing) {
      existing.textContent = message;
      return;
    }

    const error = document.createElement("small");
    error.className = "field-error-message";
    error.textContent = message;
    el.parentElement.appendChild(error);
  }

  function clearError(el) {
    if (!el) {
      return;
    }

    el.classList.remove("field-error");
    const existing = el.parentElement.querySelector(".field-error-message");
    if (existing) {
      existing.parentElement.removeChild(existing);
    }
  }

  function validateRequired(el) {
    const value = text(el);
    if (!value) {
      addError(el, "This field is required.");
      return false;
    }
    clearError(el);
    return true;
  }

  function validateEmail(el) {
    const value = text(el);
    if (!value) {
      return true;
    }
    if (!patterns.email.test(value)) {
      addError(el, "Invalid email address.");
      return false;
    }
    clearError(el);
    return true;
  }

  function validatePhone(el) {
    const value = text(el);
    if (!value) {
      return true;
    }
    if (!patterns.phone.test(value)) {
      addError(el, "Phone must contain only digits and common symbols.");
      return false;
    }
    clearError(el);
    return true;
  }

  function validatePasswordStrength(el) {
    const value = text(el);
    if (!value) {
      return true;
    }
    if (!patterns.strongPassword.test(value)) {
      addError(el, "Use 8+ chars with letters and numbers.");
      return false;
    }
    clearError(el);
    return true;
  }

  function validateMinLength(el) {
    const value = text(el);
    const min = parseInt(el.getAttribute("minlength") || "0", 10);
    if (!min || !value) {
      return true;
    }
    if (value.length < min) {
      addError(el, `Minimum length is ${min} characters.`);
      return false;
    }
    clearError(el);
    return true;
  }

  function validateSlug(el) {
    const value = text(el);
    if (!value) {
      return true;
    }
    if (!patterns.slug.test(value)) {
      addError(el, "Use lowercase letters, numbers, and hyphens only.");
      return false;
    }
    clearError(el);
    return true;
  }

  function validateAmount(el) {
    const value = text(el);
    if (!value) {
      return true;
    }
    if (!patterns.amount.test(value)) {
      addError(el, "Enter a valid number (up to 2 decimals).");
      return false;
    }
    clearError(el);
    return true;
  }

  function validateDateTime(el) {
    const value = text(el);
    if (!value) {
      return true;
    }

    const dt = new Date(value);
    if (Number.isNaN(dt.getTime())) {
      addError(el, "Invalid date/time format.");
      return false;
    }

    const minToday = el.dataset.futureOnly === "yes";
    if (minToday) {
      const now = new Date();
      if (dt < now) {
        addError(el, "Choose a future date and time.");
        return false;
      }
    }

    clearError(el);
    return true;
  }

  function validateTextareaLength(el) {
    const value = text(el);
    const min = parseInt(el.dataset.minchars || "0", 10);
    if (!min || !value) {
      return true;
    }
    if (value.length < min) {
      addError(el, `Please provide at least ${min} characters.`);
      return false;
    }
    clearError(el);
    return true;
  }

  function runFieldValidators(el) {
    const validators = [];
    if (el.hasAttribute("required")) {
      validators.push(validateRequired);
    }
    if (el.type === "email") {
      validators.push(validateEmail);
    }
    if (el.type === "tel") {
      validators.push(validatePhone);
    }
    if (el.type === "password") {
      validators.push(validatePasswordStrength);
    }
    if (el.hasAttribute("minlength")) {
      validators.push(validateMinLength);
    }
    if (el.name && (el.name.includes("slug") || el.dataset.validate === "slug")) {
      validators.push(validateSlug);
    }
    if (el.type === "number" || el.dataset.validate === "amount") {
      validators.push(validateAmount);
    }
    if (el.type === "datetime-local") {
      validators.push(validateDateTime);
    }
    if (el.tagName === "TEXTAREA") {
      validators.push(validateTextareaLength);
    }

    return validators.every((validator) => validator(el));
  }

  function linkPasswordConfirm(form) {
    const password = form.querySelector("input[name='password']");
    const confirm = form.querySelector("input[name='confirm_password']");
    if (!password || !confirm) {
      return;
    }

    function compare() {
      const p = text(password);
      const c = text(confirm);
      if (!c) {
        clearError(confirm);
        return true;
      }
      if (p !== c) {
        addError(confirm, "Passwords do not match.");
        return false;
      }
      clearError(confirm);
      return true;
    }

    password.addEventListener("input", compare);
    confirm.addEventListener("input", compare);

    form.__passwordCompare = compare;
  }

  function setupLiveValidation(form) {
    const fields = toArray(form.querySelectorAll("input, textarea, select"));
    fields.forEach((field) => {
      field.addEventListener("blur", () => runFieldValidators(field));
      field.addEventListener("input", () => clearError(field));
    });
  }

  function normalizeSlugField(form) {
    const slug = form.querySelector("input[name='slug']");
    if (!slug) {
      return;
    }

    slug.addEventListener("blur", () => {
      slug.value = trim(slug.value)
        .toLowerCase()
        .replace(/\s+/g, "-")
        .replace(/[^a-z0-9-]/g, "")
        .replace(/-+/g, "-")
        .replace(/^-|-$/g, "");
    });
  }

  function addCharacterCounters(form) {
    const fields = toArray(form.querySelectorAll("textarea[data-counter='yes']"));
    fields.forEach((field) => {
      const max = parseInt(field.getAttribute("maxlength") || "0", 10);
      const counter = document.createElement("small");
      counter.className = "field-counter";
      field.parentElement.appendChild(counter);

      function update() {
        const length = field.value.length;
        if (max > 0) {
          counter.textContent = `${length}/${max}`;
        } else {
          counter.textContent = `${length} characters`;
        }
      }

      field.addEventListener("input", update);
      update();
    });
  }

  function addFormSummary(form) {
    const summary = document.createElement("div");
    summary.className = "form-summary";
    summary.hidden = true;
    form.insertBefore(summary, form.firstChild);

    form.__showSummary = function (messages) {
      summary.hidden = messages.length === 0;
      summary.innerHTML = "";
      if (messages.length === 0) {
        return;
      }
      const ul = document.createElement("ul");
      messages.forEach((message) => {
        const li = document.createElement("li");
        li.textContent = message;
        ul.appendChild(li);
      });
      summary.appendChild(ul);
    };
  }

  function validateForm(form) {
    const fields = toArray(form.querySelectorAll("input, textarea, select"));
    const errors = [];

    fields.forEach((field) => {
      const ok = runFieldValidators(field);
      if (!ok) {
        const label = field.name || field.id || "field";
        errors.push(`Invalid value in ${label}`);
      }
    });

    if (typeof form.__passwordCompare === "function" && !form.__passwordCompare()) {
      errors.push("Password and confirm password do not match.");
    }

    if (typeof form.__showSummary === "function") {
      form.__showSummary(errors.slice(0, 6));
    }

    return errors.length === 0;
  }

  function setupForm(form) {
    if (form.dataset.skipValidation === "yes" || form.id === "aiForm") {
      return;
    }

    linkPasswordConfirm(form);
    setupLiveValidation(form);
    normalizeSlugField(form);
    addCharacterCounters(form);
    addFormSummary(form);

    form.addEventListener("submit", (event) => {
      // Some live/AJAX forms (like AI chat) call preventDefault in their own
      // submit handler and manage validation/request flow separately.
      if (event.defaultPrevented) {
        return;
      }

      const valid = validateForm(form);
      if (!valid) {
        event.preventDefault();
      }
    });
  }

  function setupAllForms() {
    const forms = toArray(document.querySelectorAll("form"));
    forms.forEach(setupForm);
  }

  function setupInputHints() {
    const appointmentInput = document.querySelector("input[name='appointment_time']");
    if (appointmentInput) {
      appointmentInput.dataset.futureOnly = "yes";
    }

    const amountInputs = toArray(document.querySelectorAll("input[name='amount']"));
    amountInputs.forEach((el) => {
      el.dataset.validate = "amount";
    });

    const messageAreas = toArray(
      document.querySelectorAll("textarea[name='message'], textarea[name='notes'], textarea[name='body']")
    );
    messageAreas.forEach((el) => {
      if (!el.dataset.minchars) {
        el.dataset.minchars = "5";
      }
      if (!el.dataset.counter) {
        el.dataset.counter = "yes";
      }
    });

    const slugFields = toArray(document.querySelectorAll("input[name='slug']"));
    slugFields.forEach((el) => {
      el.dataset.validate = "slug";
    });
  }

  function setup() {
    setupInputHints();
    setupAllForms();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup);
  } else {
    setup();
  }
})();
