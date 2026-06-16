'use strict';

/* ═══════════════════════════════════════════════
   MEDIRESPONSE — MAIN JAVASCRIPT
   Handles: sidebar toggle, auto-refresh, alerts
   ═══════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

    // ── Mobile Sidebar Toggle ──────────────────────────────
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('open');
        });

        // Close sidebar when clicking outside it
        document.addEventListener('click', function (e) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });
    }

    // ── Auto-dismiss alerts after 5 seconds ───────────────
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-8px)';
            alert.style.transition = 'all 0.3s ease';
            setTimeout(function () { alert.remove(); }, 300);
        }, 5000);
    });

    // ── Confirm dialogs for destructive actions ────────────
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    // ── Highlight active table rows on hover ───────────────
    document.querySelectorAll('.table tbody tr').forEach(function (row) {
        row.style.cursor = 'pointer';
    });

    // ── Bar chart height animation ─────────────────────────
    // Finds all bar elements and animates them upward on load
    const bars = document.querySelectorAll('.bar-chart__bar');
    bars.forEach(function (bar) {
        const targetHeight = bar.style.height;
        bar.style.height = '0';
        setTimeout(function () {
            bar.style.height = targetHeight;
        }, 100);
    });

});
