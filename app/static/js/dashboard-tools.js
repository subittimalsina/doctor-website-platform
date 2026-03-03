(function () {
  "use strict";

  function qs(selector, scope) {
    return (scope || document).querySelector(selector);
  }

  function qsa(selector, scope) {
    return Array.from((scope || document).querySelectorAll(selector));
  }

  function safeText(value) {
    if (value === null || value === undefined) {
      return "";
    }
    return String(value);
  }

  function normalize(value) {
    return safeText(value).trim().toLowerCase();
  }

  function create(tag, attrs, text) {
    const el = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach((key) => {
        if (key === "className") {
          el.className = attrs[key];
        } else {
          el.setAttribute(key, attrs[key]);
        }
      });
    }
    if (text) {
      el.textContent = text;
    }
    return el;
  }

  function addSearchToTables() {
    const tables = qsa("table.table");
    tables.forEach((table, index) => {
      const wrapper = table.closest(".card");
      if (!wrapper || wrapper.dataset.searchAttached === "yes") {
        return;
      }

      const searchWrap = create("div", { className: "table-search-wrap" });
      const searchInput = create("input", {
        type: "search",
        placeholder: "Filter rows...",
        className: "table-search",
        "aria-label": `Filter table ${index + 1}`,
      });
      searchWrap.appendChild(searchInput);

      wrapper.insertBefore(searchWrap, table);
      wrapper.dataset.searchAttached = "yes";

      const rows = qsa("tbody tr", table);
      searchInput.addEventListener("input", () => {
        const term = normalize(searchInput.value);
        rows.forEach((row) => {
          const text = normalize(row.textContent || "");
          row.style.display = text.includes(term) ? "" : "none";
        });
      });
    });
  }

  function enhanceStatusBadges() {
    const badges = qsa(".badge");
    badges.forEach((badge) => {
      const text = normalize(badge.textContent);
      if (text.includes("pending") || text.includes("open") || text.includes("unpaid")) {
        badge.classList.add("badge-pending");
      }
      if (text.includes("confirmed") || text.includes("resolved") || text.includes("paid")) {
        badge.classList.add("badge-good");
      }
      if (text.includes("cancelled") || text.includes("closed") || text.includes("overdue")) {
        badge.classList.add("badge-warn");
      }
    });
  }

  function setupAutoDismissAlerts() {
    const alerts = qsa(".alert");
    alerts.forEach((alert) => {
      setTimeout(() => {
        alert.classList.add("fade-out");
        setTimeout(() => {
          if (alert && alert.parentNode) {
            alert.parentNode.removeChild(alert);
          }
        }, 400);
      }, 5000);
    });
  }

  function setupFadingCards() {
    const cards = qsa(".card, .stat");
    cards.forEach((card, index) => {
      card.style.animationDelay = `${Math.min(index * 0.03, 0.4)}s`;
    });
  }

  function formatCurrencyFields() {
    const cells = qsa("td");
    cells.forEach((cell) => {
      const text = safeText(cell.textContent);
      if (/^\$\d+(\.\d{2})?$/.test(text.trim())) {
        cell.classList.add("currency");
      }
    });
  }

  function setupFormGuardrails() {
    const forms = qsa("form");
    forms.forEach((form) => {
      form.addEventListener("submit", () => {
        const submitButtons = qsa("button[type='submit']", form);
        submitButtons.forEach((button) => {
          const original = button.textContent;
          button.dataset.originalLabel = original || "Submit";
          button.textContent = "Processing...";
          button.disabled = true;
        });
      });
    });
  }

  function setupDetailsAccordion() {
    const detailsElements = qsa("details");
    detailsElements.forEach((details) => {
      details.addEventListener("toggle", () => {
        if (!details.open) {
          return;
        }
        detailsElements.forEach((other) => {
          if (other !== details) {
            other.open = false;
          }
        });
      });
    });
  }

  function setupStickyActions() {
    const actionRows = qsa(".dashboard-actions");
    actionRows.forEach((row) => {
      row.classList.add("actions-ready");
    });
  }

  function setupKeyboardShortcuts() {
    document.addEventListener("keydown", (event) => {
      if (!event.altKey) {
        return;
      }
      const key = event.key.toLowerCase();
      if (key === "a") {
        const firstAppointmentLink = qs("a[href='/appointments/book']");
        if (firstAppointmentLink) {
          firstAppointmentLink.click();
        }
      }
      if (key === "s") {
        const supportLink = qs("a[href='/support/new']");
        if (supportLink) {
          supportLink.click();
        }
      }
      if (key === "d") {
        const dashboardLink = qs("a[href='/dashboard'], a[href='/admin']");
        if (dashboardLink) {
          dashboardLink.click();
        }
      }
    });
  }

  function setupTableSorting() {
    const tables = qsa("table.table");
    tables.forEach((table) => {
      const headers = qsa("thead th", table);
      const tbody = qs("tbody", table);
      if (!tbody || headers.length === 0) {
        return;
      }

      headers.forEach((header, colIndex) => {
        header.style.cursor = "pointer";
        header.title = "Sort";
        let asc = true;

        header.addEventListener("click", () => {
          const rows = qsa("tr", tbody);
          rows.sort((a, b) => {
            const av = normalize((a.children[colIndex] || {}).textContent);
            const bv = normalize((b.children[colIndex] || {}).textContent);
            if (av < bv) {
              return asc ? -1 : 1;
            }
            if (av > bv) {
              return asc ? 1 : -1;
            }
            return 0;
          });
          rows.forEach((row) => tbody.appendChild(row));
          asc = !asc;
        });
      });
    });
  }

  function registerQuickSummary() {
    const statCards = qsa(".stat h3");
    if (statCards.length === 0) {
      return;
    }
    let total = 0;
    statCards.forEach((el) => {
      const num = parseInt(safeText(el.textContent).replace(/[^0-9]/g, ""), 10);
      if (!isNaN(num)) {
        total += num;
      }
    });

    const section = qs(".section-pad");
    if (!section) {
      return;
    }
    const hint = create("p", { className: "muted" }, `Snapshot total across visible counters: ${total}`);
    section.insertBefore(hint, section.children[2] || null);
  }

  function setupThemeSwitch() {
    const footer = qs(".site-footer .container");
    if (!footer) {
      return;
    }

    const row = create("div", { className: "theme-switch" });
    const button = create("button", { type: "button", className: "btn-ghost" }, "Toggle Contrast");
    row.appendChild(button);
    footer.appendChild(row);

    button.addEventListener("click", () => {
      document.body.classList.toggle("high-contrast");
    });
  }

  function setupLiveClock() {
    const nav = qs(".nav-wrap");
    if (!nav) {
      return;
    }

    const clock = create("span", { className: "nav-clock" });
    nav.appendChild(clock);

    function update() {
      const now = new Date();
      clock.textContent = now.toLocaleString();
    }

    update();
    setInterval(update, 1000);
  }

  function init() {
    addSearchToTables();
    enhanceStatusBadges();
    setupAutoDismissAlerts();
    setupFadingCards();
    formatCurrencyFields();
    setupFormGuardrails();
    setupDetailsAccordion();
    setupStickyActions();
    setupKeyboardShortcuts();
    setupTableSorting();
    registerQuickSummary();
    setupThemeSwitch();
    setupLiveClock();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
