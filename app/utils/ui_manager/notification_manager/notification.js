/**
 * Auto Notification System for JSONResponse
 * Automatically shows popups for JSONResponse messages from the server
 */

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
                // Small delay to ensure DOM is ready
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
            
            // Check if it's a JSON response
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                try {
                    const data = await clonedResponse.json();
                    
                    // Check if it has a message property
                    if (data && typeof data.message === 'string' && data.message.trim()) {
                        const type = this.getTypeFromStatusCode(response.status);
                        
                        if (willRedirect) {
                            // Store for after redirect
                            this.storeNotification(data.message, type);
                        } else {
                            // Show immediately
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
            return; // Already intercepted
        }

        const originalFetch = window.fetch;
        const self = this; // Capture the correct context
        
        window.fetch = async function(...args) {
            try {
                console.log('Fetch intercepted:', args[0]); // Debug log
                const response = await originalFetch.apply(this, args);
                
                // Process notification IMMEDIATELY when response is received
                if (response && response.status >= 200) {
                    console.log('Processing response for notifications:', response.status, response.headers.get('content-type')); // Debug log
                    // Clone the response IMMEDIATELY to avoid conflicts with user code
                    const clonedResponse = response.clone();
                    
                    // Process notification asynchronously without blocking the original response
                    self.processNotification(clonedResponse).catch(err => {
                        // Silently ignore notification processing errors
                        console.debug('Notification processing error:', err);
                    });
                }
                
                return response;
            } catch (error) {
                // Network error or other fetch error
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
            // Check if it's a JSON response
            const contentType = response.headers.get('content-type');
            console.log('Content-Type:', contentType); // Debug log
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                console.log('JSON data received:', data); // Debug log
                
                // Check if it has a message property (typical for JSONResponse)
                if (data && typeof data.message === 'string' && data.message.trim()) {
                    const type = this.getTypeFromStatusCode(response.status);
                    console.log('Showing notification:', data.message, 'Type:', type); // Debug log
                    // Use setTimeout to ensure DOM is ready and avoid blocking
                    setTimeout(() => {
                        this.show(data.message, type);
                    }, 10);
                } else {
                    console.log('No valid message found in data:', data); // Debug log
                }
            } else {
                console.log('Not a JSON response'); // Debug log
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
        // Remove oldest notifications if we have too many
        while (this.notifications.length >= this.maxNotifications) {
            const oldest = this.notifications.shift();
            if (oldest && oldest.element) {
                this.remove(oldest.element);
            }
        }

        const notification = this.create(message, type);
        this.notifications.push(notification);

        // Position notification based on existing notifications
        const index = this.notifications.length - 1;
        notification.element.style.top = `${20 + (index * 80)}px`;

        // Add to DOM
        document.body.appendChild(notification.element);

        // Trigger animation
        setTimeout(() => {
            notification.element.classList.add('show');
        }, 100);

        // Auto remove after duration
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

        // Add close button functionality
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

        // Find and remove from notifications array
        const index = this.notifications.findIndex(n => n.element === element);
        if (index > -1) {
            const notification = this.notifications[index];
            if (notification.timeoutId) {
                clearTimeout(notification.timeoutId);
            }
            this.notifications.splice(index, 1);
        }

        // Animate out
        element.classList.remove('show');
        
        // Remove from DOM after animation
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
            // Reposition remaining notifications
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

// Initialize immediately when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        notificationManagerInstance = new NotificationManager();
    });
} else {
    // DOM is already ready
    notificationManagerInstance = new NotificationManager();
}

// Export for manual use if needed
window.NotificationManager = NotificationManager;

// Also provide a simple global function for manual notifications
window.showNotification = function(message, type = 'info', duration = 4000) {
    if (notificationManagerInstance) {
        return notificationManagerInstance.show(message, type, duration);
    } else {
        // If not initialized yet, try to initialize and show
        notificationManagerInstance = new NotificationManager();
        return notificationManagerInstance.show(message, type, duration);
    }
};

// Function to store notification for after redirect
window.storeNotification = function(message, type = 'info') {
    if (notificationManagerInstance) {
        return notificationManagerInstance.storeNotification(message, type);
    } else {
        // Fallback - store directly in sessionStorage
        sessionStorage.setItem('showNotification', JSON.stringify({
            message: message,
            type: type
        }));
    }
};

// Function to handle redirect notifications with automatic message extraction
window.handleRedirectNotification = function(response) {
    if (notificationManagerInstance) {
        return notificationManagerInstance.handleRedirectNotification(response, true);
    }
    return Promise.resolve();
};
