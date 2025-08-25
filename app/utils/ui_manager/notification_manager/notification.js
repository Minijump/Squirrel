class NotificationManager {
    constructor() {
        this.notifications = [];
        this.maxNotifications = 5;
        this.defaultDuration = 3000;
        this.setupFetchInterceptor();
        this.checkStoredNotifications();
    }

    checkStoredNotifications() {
        const stored = sessionStorage.getItem('showNotification');
        if (stored) {
            sessionStorage.removeItem('showNotification');
            try {
                const {message, type} = JSON.parse(stored);
                setTimeout(() => this.show(message, type), 100);
            } catch (e) {}
        }
    }

    storeNotification(message, type = 'info') {
        sessionStorage.setItem('showNotification', JSON.stringify({message, type}));
    }

    async handleRedirectNotification(response, willRedirect = false) {
        const data = await this.extractMessage(response);
        if (data) {
            const type = response.status >= 400 ? 'error' : 'success';
            if (willRedirect) {
                this.storeNotification(data.message, type);
            } else {
                setTimeout(() => this.show(data.message, type), 10);
            }
        }
    }

    setupFetchInterceptor() {
        if (window.fetch.__intercepted) return;

        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const response = await originalFetch(...args);
            if (response?.status >= 200) {
                this.processNotification(response.clone()).catch(() => {});
            }
            return response;
        };
        window.fetch.__intercepted = true;
    }

    async processNotification(response) {
        const data = await this.extractMessage(response);
        if (data) {
            const type = response.status >= 400 ? 'error' : 'success';
            setTimeout(() => this.show(data.message, type), 10);
        }
    }

    async extractMessage(response) {
        try {
            const contentType = response.headers.get('content-type');
            if (contentType?.includes('application/json')) {
                const data = await response.json();
                if (data?.message?.trim()) return data;
            }
        } catch (e) {}
        return null;
    }

    getIcon(type) {
        const icons = {
            success: '<i class="fas fa-check-circle"></i>',
            error: '<i class="fas fa-exclamation-circle"></i>',
            warning: '<i class="fas fa-exclamation-triangle"></i>',
            info: '<i class="fas fa-info-circle"></i>'
        };
        return icons[type] || icons.info;
    }

    show(message, type = 'info', duration = this.defaultDuration) {
        while (this.notifications.length >= this.maxNotifications) {
            const oldest = this.notifications.shift();
            if (oldest?.element) this.remove(oldest.element);
        }

        const notification = this.create(message, type);
        this.notifications.push(notification);
        notification.element.style.top = `${20 + (this.notifications.length - 1) * 80}px`;

        document.body.appendChild(notification.element);
        setTimeout(() => notification.element.classList.add('show'), 100);

        if (duration > 0) {
            notification.timeoutId = setTimeout(() => this.remove(notification.element), duration);
        }

        return notification;
    }

    create(message, type) {
        const element = document.createElement('div');
        element.className = `notification ${type}`;
        element.innerHTML = `
            <span class="notification-icon">${this.getIcon(type)}</span>
            <span class="notification-message">${this.escapeHtml(message)}</span>
            <button class="close-btn" type="button">&times;</button>
        `;

        element.querySelector('.close-btn').addEventListener('click', () => this.remove(element));
        return {element, type, message, timeoutId: null};
    }

    remove(element) {
        if (!element?.parentNode) return;

        const index = this.notifications.findIndex(n => n.element === element);
        if (index > -1) {
            const notification = this.notifications[index];
            if (notification.timeoutId) clearTimeout(notification.timeoutId);
            this.notifications.splice(index, 1);
        }

        element.classList.remove('show');
        setTimeout(() => {
            if (element.parentNode) element.parentNode.removeChild(element);
            this.repositionNotifications();
        }, 300);
    }

    repositionNotifications() {
        this.notifications.forEach((notification, index) => {
            if (notification.element) {
                notification.element.style.top = `${20 + (index * 80)}px`;
            }
        });
    }

    clear() {
        this.notifications.forEach(notification => {
            if (notification.timeoutId) clearTimeout(notification.timeoutId);
            if (notification.element?.parentNode) this.remove(notification.element);
        });
        this.notifications = [];
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

let notificationManagerInstance = null;

function checkNotificationQueryParam() {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const notification = urlParams.get('notification');
        if (notification) {
            setTimeout(() => window.showNotification(decodeURIComponent(notification), 'error'), 0);
            urlParams.delete('notification');
            const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
            window.history.replaceState({}, document.title, newUrl);
        }
    } catch (e) {}
}

function getOrCreateInstance() {
    if (!notificationManagerInstance) {
        notificationManagerInstance = new NotificationManager();
    }
    return notificationManagerInstance;
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        notificationManagerInstance = new NotificationManager();
        checkNotificationQueryParam();
    });
} else {
    notificationManagerInstance = new NotificationManager();
    checkNotificationQueryParam();
}

window.NotificationManager = NotificationManager;

window.showNotification = function(message, type = 'info', duration = 4000) {
    return getOrCreateInstance().show(message, type, duration);
};

window.storeNotification = function(message, type = 'info') {
    const instance = getOrCreateInstance();
    if (instance) {
        return instance.storeNotification(message, type);
    } else {
        sessionStorage.setItem('showNotification', JSON.stringify({message, type}));
    }
};

window.handleRedirectNotification = function(response) {
    const instance = getOrCreateInstance();
    return instance ? instance.handleRedirectNotification(response, true) : Promise.resolve();
};
