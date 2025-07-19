class ThemeManager {
    constructor() {
        this.storageKey = 'squirrel-theme';
        this.themes = {
            dark: 'dark',
            light: 'light'
        };    
        this.init();
    }

    init() {
        const savedTheme = this.getSavedTheme();
        this.applyTheme(savedTheme);
        
        this.updateThemeControls(savedTheme);
    }

    getSavedTheme() {
        const saved = localStorage.getItem(this.storageKey);
        return saved && Object.values(this.themes).includes(saved) ? saved : this.themes.dark;
    }

    applyTheme(theme) {
        const html = document.documentElement;
        
        if (theme === this.themes.light) html.setAttribute('data-theme', 'light');
        else html.removeAttribute('data-theme');
        
        localStorage.setItem(this.storageKey, theme);
    }

    setTheme(theme) {
        if (!Object.values(this.themes).includes(theme)) {
            console.warn(`Invalid theme: ${theme}`);
            return;
        }
        
        this.applyTheme(theme);
        this.updateThemeControls(theme);
        
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme } 
        }));
    }

    getCurrentTheme() {
        return document.documentElement.hasAttribute('data-theme') 
            ? this.themes.light 
            : this.themes.dark;
    }

    updateThemeControls(theme) {
        const themeSelects = document.querySelectorAll('[data-theme-select]');        
        themeSelects.forEach(select => {
            if (select.value !== theme) {
                select.value = theme;
            }
        });
    }

    static getInstance() {
        if (!window.themeManager) {
            window.themeManager = new ThemeManager();
        }
        return window.themeManager;
    }
}

// Add theme before dom is loaded to avoid flash of default theme (still flash sometimes)
(function() {
    ThemeManager.getInstance()
})();
export { ThemeManager };
