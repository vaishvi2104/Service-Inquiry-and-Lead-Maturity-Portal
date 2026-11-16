/**
 * Start-Up Sahay — Public Portal Vanilla JavaScript
 * Zero external JS dependencies. Pure Vanilla DOM API.
 * Strict XSS prevention: textContent only, no raw innerHTML.
 */
document.addEventListener("DOMContentLoaded", function () {
  "use strict";

  // 1. Mobile number input helper: Restrict input to numbers only (up to 10 digits)
  var mobileInput = document.getElementById("id_mobile_number");
  if (mobileInput) {
    mobileInput.addEventListener("input", function (e) {
      var val = e.target.value.replace(/\D/g, "");
      if (val.length > 10) {
        val = val.substring(0, 10);
      }
      e.target.value = val;
    });
  }

  // 2. Navigation smooth-scrolling via data-scroll-target (no hash links used)
  var scrollButtons = document.querySelectorAll("[data-scroll-target]");
  scrollButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var targetId = btn.getAttribute("data-scroll-target");
      if (targetId) {
        var targetElem = document.getElementById(targetId);
        if (targetElem) {
          targetElem.scrollIntoView({ behavior: "smooth" });
        }
      }
    });
  });

  // 3. Service selection triggers: "Enquire Now" buttons on service cards
  var serviceButtons = document.querySelectorAll(".js-select-service");
  var serviceSelect = document.getElementById("id_service");
  var inquirySection = document.getElementById("inquiry-form-section");

  if (serviceButtons.length > 0 && serviceSelect) {
    serviceButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        var targetService = button.getAttribute("data-service-key");
        if (targetService) {
          serviceSelect.value = targetService;
          if (inquirySection) {
            inquirySection.scrollIntoView({ behavior: "smooth" });
          }
          serviceSelect.focus();
        }
      });
    });
  }

  // 4. Reference ID Copy to Clipboard on confirmation page
  var copyRefBtn = document.getElementById("js-copy-ref-btn");
  var refCodeElem = document.getElementById("js-ref-code");
  var copyFeedback = document.getElementById("js-copy-feedback");

  if (copyRefBtn && refCodeElem) {
    copyRefBtn.addEventListener("click", function () {
      var refText = refCodeElem.textContent.trim();
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(refText).then(function () {
          if (copyFeedback) {
            copyFeedback.textContent = "Copied to clipboard!";
            setTimeout(function () {
              copyFeedback.textContent = "";
            }, 3000);
          }
        });
      }
    });
  }
});
