export class SquirrelWidget {
    constructor(element, allowedTagNames = []) {
        if (!element) {
            throw new Error('Widget requires an element');
        }
        if (element.tagName && !allowedTagNames.includes(element.tagName)) {
            throw new Error('Widget can only be initialized on specific tag names: ' + allowedTagNames.join(', '));
        }
        this.element = element;
        this.defaultOptions = {};
    }

    parseOptions() {
        const userOptions = this.element.getAttribute('options');
        try {
            return userOptions ? { ...this.defaultOptions, ...JSON.parse(userOptions) } : this.defaultOptions;
        } catch (error) {
            console.warn('Invalid options JSON, using defaults:', error);
            return this.defaultOptions;
        }
    }
}
