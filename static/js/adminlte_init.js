/**
 * Sahay LeadFlow — AdminLTE 4 Initialization & CRM Helpers
 * Vanilla JavaScript (Bootstrap 5.3 + AdminLTE 4)
 */
document.addEventListener("DOMContentLoaded", function () {
  "use strict";

  // Initialize Bootstrap 5 Tooltips if available
  if (typeof bootstrap !== "undefined" && bootstrap.Tooltip) {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }

  // Sidebar toggle state preservation in localStorage
  var sidebarToggleBtn = document.querySelector('[data-lte-toggle="sidebar"]');
  if (sidebarToggleBtn) {
    var storedCollapse = localStorage.getItem("adminlte_sidebar_collapse");
    if (storedCollapse === "true") {
      document.body.classList.add("sidebar-collapse");
    }

    sidebarToggleBtn.addEventListener("click", function () {
      setTimeout(function () {
        var isCollapsed = document.body.classList.contains("sidebar-collapse");
        localStorage.setItem("adminlte_sidebar_collapse", isCollapsed ? "true" : "false");
      }, 100);
    });
  }

  // Initialize OverlayScrollbars on sidebar if available
  if (typeof OverlayScrollbarsGlobal !== "undefined" && OverlayScrollbarsGlobal.OverlayScrollbars) {
    var sidebarWrapper = document.querySelector(".sidebar-wrapper");
    if (sidebarWrapper) {
      OverlayScrollbarsGlobal.OverlayScrollbars(sidebarWrapper, {
        scrollbars: {
          theme: "os-theme-light",
          autoHide: "leave",
          clickScroll: true
        }
      });
    }
  }

  // Auto-dismiss alerts after 5 seconds
  var alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      if (typeof bootstrap !== "undefined" && bootstrap.Alert) {
        var bsAlert = bootstrap.Alert.getInstance(alert);
        if (bsAlert) {
          bsAlert.close();
        }
      }
    }, 6000);
  });
});
