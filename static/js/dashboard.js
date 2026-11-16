/**
 * Start-Up Sahay — Admin Dashboard Vanilla JavaScript
 * Clean, lightweight, accessible UI enhancements.
 */
document.addEventListener("DOMContentLoaded", function () {
  "use strict";

  // Auto-dismiss alert banners after 5 seconds if desired
  var alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach(function (alertElem) {
    setTimeout(function () {
      var closeBtn = alertElem.querySelector(".btn-close");
      if (closeBtn) {
        closeBtn.click();
      }
    }, 6000);
  });
});
