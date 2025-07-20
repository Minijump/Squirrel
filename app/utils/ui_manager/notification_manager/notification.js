class NotificationManager {
    constructor() {
        this.notifications = [];
        this.maxNotifications = 5;
        this.defaultDuration = 3000; // 3 seconds
        this.setupFetchInterceptor();
        this.checkStoredNotifications();
    }

    /**
     * Check for stored notifications from previous page loads
     */
    checkStoredNotifications() {
        const storedNotification = sessionStorage.getItem('showNotification');
        if (storedNotification) {
            sessionStorage.removeItem('showNotification');
            try {
                const notification = JSON.parse(storedNotification);
                setTimeout(() => {
                    this.show(notification.message, notification.type);
                }, 100);
            } catch (error) {
                console.warn('Failed to parse stored notification:', error);
            }
        }
    }

    /**
     * Store a notification to be shown after page redirect
     */
    storeNotification(message, type = 'info') {
        sessionStorage.setItem('showNotification', JSON.stringify({
            message: message,
            type: type
        }));
    }

    /**
     * Handle notifications for requests that will redirect
     */
    async handleRedirectNotification(response, willRedirect = false) {
        if (response && response.status >= 200) {
            const clonedResponse = response.clone();
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                try {
                    const data = await clonedResponse.json();
                    
                    if (data && typeof data.message === 'string' && data.message.trim()) {
                        const type = this.getTypeFromStatusCode(response.status);
                        
                        if (willRedirect) {
                            this.storeNotification(data.message, type);
                        } else {
                            setTimeout(() => {
                                this.show(data.message, type);
                            }, 10);
                        }
                    }
                } catch (error) {
                    // Silently ignore - not a JSON response or no message property
                }
            }
        }
    }

    /**
     * Intercept all fetch requests to automatically handle JSONResponse notifications
     */
    setupFetchInterceptor() {
        if (window.fetch.__intercepted) {
            return;
        }

        const originalFetch = window.fetch;
        const self = this;
        
        window.fetch = async function(...args) {
            try {
                const response = await originalFetch.apply(this, args);
                
                if (response && response.status >= 200) {
                    const clonedResponse = response.clone();
                    self.processNotification(clonedResponse).catch(err => {
                        console.debug('Notification processing error:', err);
                    });
                }
                
                return response;
            } catch (error) {
                throw error;
            }
        };
        
        window.fetch.__intercepted = true;
    }

    /**
     * Process notification from response (async to avoid blocking)
     */
    async processNotification(response) {
        try {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                
                if (data && typeof data.message === 'string' && data.message.trim()) {
                    const type = this.getTypeFromStatusCode(response.status);
                    setTimeout(() => {
                        this.show(data.message, type);
                    }, 10);
                }
            }
        } catch (error) {
            // Silently ignore - not a JSON response or no message property
        }
    }

    /**
     * Determine notification type based on HTTP status code
     */
    getTypeFromStatusCode(statusCode) {
        if (statusCode >= 200 && statusCode < 300) {
            return 'success';
        } else if (statusCode >= 400 && statusCode < 500) {
            return 'error';
        } else if (statusCode >= 500) {
            return 'error';
        } else {
            return 'info';
        }
    }

    /**
     * Get icon for notification type
     */
    getIcon(type) {
        const icons = {
            success: '<i class="fas fa-check-circle"></i>',
            error: '<i class="fas fa-exclamation-circle"></i>',
            warning: '<i class="fas fa-exclamation-triangle"></i>',
            info: '<i class="fas fa-info-circle"></i>'
        };
        return icons[type] || icons.info;
    }

    /**
     * Show a notification
     * @param {string} message - The message to display
     * @param {string} type - The notification type ('success', 'error', 'warning', 'info')
     * @param {number} duration - How long to show the notification (ms)
     */
    show(message, type = 'info', duration = this.defaultDuration) {
        while (this.notifications.length >= this.maxNotifications) {
            const oldest = this.notifications.shift();
            if (oldest && oldest.element) {
                this.remove(oldest.element);
            }
        }

        const notification = this.create(message, type);
        this.notifications.push(notification);

        const index = this.notifications.length - 1;
        notification.element.style.top = `${20 + (index * 80)}px`;

        document.body.appendChild(notification.element);

        setTimeout(() => {
            notification.element.classList.add('show');
        }, 100);

        if (duration > 0) {
            notification.timeoutId = setTimeout(() => {
                this.remove(notification.element);
            }, duration);
        }

        return notification;
    }

    /**
     * Create notification element
     * @param {string} message 
     * @param {string} type 
     * @returns {object} notification object with element and metadata
     */
    create(message, type) {
        const element = document.createElement('div');
        element.className = `notification ${type}`;
        
        const icon = this.getIcon(type);
        
        element.innerHTML = `
            <span class="notification-icon">${icon}</span>
            <span class="notification-message">${this.escapeHtml(message)}</span>
            <button class="close-btn" type="button">&times;</button>
        `;

        const closeBtn = element.querySelector('.close-btn');
        closeBtn.addEventListener('click', () => {
            this.remove(element);
        });

        const notification = {
            element: element,
            type: type,
            message: message,
            timeoutId: null
        };

        return notification;
    }

    /**
     * Remove a notification
     * @param {HTMLElement} element 
     */
    remove(element) {
        if (!element || !element.parentNode) return;

        const index = this.notifications.findIndex(n => n.element === element);
        if (index > -1) {
            const notification = this.notifications[index];
            if (notification.timeoutId) {
                clearTimeout(notification.timeoutId);
            }
            this.notifications.splice(index, 1);
        }

        element.classList.remove('show');
        
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
            this.repositionNotifications();
        }, 300);
    }

    /**
     * Reposition all notifications after one is removed
     */
    repositionNotifications() {
        this.notifications.forEach((notification, index) => {
            if (notification.element) {
                notification.element.style.top = `${20 + (index * 80)}px`;
            }
        });
    }

    /**
     * Clear all notifications
     */
    clear() {
        this.notifications.forEach(notification => {
            if (notification.timeoutId) {
                clearTimeout(notification.timeoutId);
            }
            if (notification.element && notification.element.parentNode) {
                this.remove(notification.element);
            }
        });
        this.notifications = [];
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text 
     * @returns {string}
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the notification manager as early as possible
let notificationManagerInstance = null;

function checkNotificationQueryParam() {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const notification = urlParams.get('notification');
        if (notification) {
            setTimeout(() => {
                window.showNotification(decodeURIComponent(notification), 'error');
            }, 0);
            urlParams.delete('notification');
            const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
            window.history.replaceState({}, document.title, newUrl);
        }
    } catch (e) {
        // Ignore errors
    }
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
    if (notificationManagerInstance) {
        return notificationManagerInstance.show(message, type, duration);
    } else {
        notificationManagerInstance = new NotificationManager();
        return notificationManagerInstance.show(message, type, duration);
    }
};

window.storeNotification = function(message, type = 'info') {
    if (notificationManagerInstance) {
        return notificationManagerInstance.storeNotification(message, type);
    } else {
        sessionStorage.setItem('showNotification', JSON.stringify({
            message: message,
            type: type
        }));
    }
};

window.handleRedirectNotification = function(response) {
    if (notificationManagerInstance) {
        return notificationManagerInstance.handleRedirectNotification(response, true);
    }
    return Promise.resolve();
};
