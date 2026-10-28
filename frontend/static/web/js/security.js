/**
 * Ignite 2K27 - Website Security Module
 * Protects against unauthorized right-click, image scraping, and devtool inspection shortcuts.
 */
(function() {
    'use strict';

    let toastTimeout = null;
    function showSecurityToast(message) {
        if (!document.body) return;
        let toast = document.getElementById('security-toast-notice');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'security-toast-notice';
            toast.style.cssText = `
                position: fixed;
                bottom: 24px;
                left: 50%;
                transform: translateX(-50%) translateY(10px);
                background: rgba(15, 23, 42, 0.95);
                color: #ffffff;
                font-family: system-ui, -apple-system, sans-serif;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 18px;
                border-radius: 9999px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.15);
                display: flex;
                align-items: center;
                gap: 8px;
                z-index: 999999;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.25s ease, transform 0.25s ease;
            `;
            toast.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ff3b5c" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
                <span id="security-toast-text">${message || 'Right-click is disabled on this website'}</span>
            `;
            document.body.appendChild(toast);
        } else {
            const textEl = document.getElementById('security-toast-text');
            if (textEl && message) textEl.textContent = message;
        }

        requestAnimationFrame(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(-50%) translateY(0)';
        });

        clearTimeout(toastTimeout);
        toastTimeout = setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(-50%) translateY(10px)';
        }, 2000);
    }

    // 1. Disable Right Click (Context Menu)
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        showSecurityToast('Right-click is disabled on this website');
        return false;
    }, { capture: true });

    // 2. Disable Image and Link Dragging
    document.addEventListener('dragstart', function(e) {
        if (e.target && (e.target.nodeName === 'IMG' || e.target.nodeName === 'A')) {
            e.preventDefault();
            return false;
        }
    }, { capture: true });

    // 3. Disable DevTools and View Source keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
        const ctrlOrCmd = isMac ? e.metaKey : e.ctrlKey;
        const key = e.key ? e.key.toLowerCase() : '';
        const keyCode = e.keyCode || e.which;

        // F12 key
        if (key === 'f12' || keyCode === 123) {
            e.preventDefault();
            showSecurityToast('Developer tools are disabled');
            return false;
        }

        // Ctrl/Cmd + Shift + I/J/C (DevTools)
        if (ctrlOrCmd && e.shiftKey && (key === 'i' || key === 'j' || key === 'c' || keyCode === 73 || keyCode === 74 || keyCode === 67)) {
            e.preventDefault();
            showSecurityToast('Developer tools are disabled');
            return false;
        }

        // Ctrl/Cmd + U (View Source)
        if (ctrlOrCmd && (key === 'u' || keyCode === 85)) {
            e.preventDefault();
            showSecurityToast('Viewing page source is disabled');
            return false;
        }

        // Ctrl/Cmd + S (Save Page)
        if (ctrlOrCmd && (key === 's' || keyCode === 83)) {
            e.preventDefault();
            return false;
        }
    }, { capture: true });
})();
