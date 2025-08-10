class ThemeManager {
    constructor() {
        this.storageKey = 'squirrel-theme';
        this.themes = { dark: 'dark', light: 'light' };
        this.init();
    }

    init() {
        const savedTheme = this.getSavedTheme();
        this.applyTheme(savedTheme);
        this.updateThemeControls(savedTheme);
    }

    getSavedTheme() {
        const saved = localStorage.getItem(this.storageKey);
        if (saved && (saved === this.themes.dark || saved === this.themes.light)) return saved;
        return (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches)
            ? this.themes.light
            : this.themes.dark;
    }

    applyTheme(theme) {
        const html = document.documentElement;
        const isLight = theme === this.themes.light;
        const alreadyLight = html.hasAttribute('data-theme');
        if (isLight === alreadyLight) {
            localStorage.setItem(this.storageKey, theme);
            return;
        }
        if (isLight) html.setAttribute('data-theme', 'light');
        else html.removeAttribute('data-theme');
        localStorage.setItem(this.storageKey, theme);
    }

    setTheme(theme) {
        if (theme !== this.themes.dark && theme !== this.themes.light) {
            console.warn(`Invalid theme: ${theme}`);
            return;
        }
        this.applyTheme(theme);
        this.updateThemeControls(theme);
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
    }

    getCurrentTheme() {
        return document.documentElement.hasAttribute('data-theme') ? this.themes.light : this.themes.dark;
    }

    updateThemeControls(theme) {
        const themeSelects = document.querySelectorAll('[data-theme-select]');
        themeSelects.forEach(select => { if (select.value !== theme) select.value = theme; });
    }

    static getInstance() {
        if (!window.themeManager) window.themeManager = new ThemeManager();
        return window.themeManager;
    }
}

(function () { ThemeManager.getInstance(); })();
export { ThemeManager };
