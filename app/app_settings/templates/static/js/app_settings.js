import { ThemeManager } from '/static/utils/ui_manager/theme_manager/theme.js';

document.addEventListener('DOMContentLoaded', () => {
    const themeManager = ThemeManager.getInstance();

    const themeSelect = document.getElementById('themeSelect');
    if (themeSelect) {
        themeSelect.value = themeManager.getCurrentTheme();

        themeSelect.addEventListener('change', (e) => {
            themeManager.setTheme(e.target.value);
        });
    }
});
