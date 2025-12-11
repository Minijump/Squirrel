export class Input {
    static createInput(type, options = {}) {
        const widgetConfig = Input._widgetConfig(type, options);
        if (widgetConfig) {
            return Input._createWidget(widgetConfig.widgetType, widgetConfig.widgetOptions, widgetConfig.defaultValue);
        }
        
        const element = Input._createElement(type, options);
        Input._applyAttributes(element, type, options);
        return element;
    }

    static _createElement(type, options) {
        if (type === 'textarea') return document.createElement('textarea');
        
        if (type === 'select') {
            const element = document.createElement('select');
            (options.selectOptions || []).forEach(([value, text]) => {
                const opt = document.createElement('option');
                opt.value = value;
                opt.text = text;
                element.appendChild(opt);
            });
            return element;
        }
        
        const element = document.createElement('input');
        element.type = type;
        return element;
    }

    static _applyAttributes(element, type, options) {
        if (options.placeholder && ['text', 'password', 'textarea', 'number'].includes(type)) {
            element.placeholder = options.placeholder;
        }
        if (options.value !== undefined) element.value = options.value;
        if (options.readonly) element.readOnly = true;
        if (options.className) element.className = options.className;
        if (type === 'number' && options.step) element.step = options.step;
        if (type === 'file' && options.accept) element.accept = options.accept;
        
        if (options.onchange) {
            element.setAttribute('onchange', options.onchange);
            element.classList.add('onchange-trigger');
        }
    }

    static _widgetConfig(type, options = {}) {
        const configs = {
            'dict': {
                widgetType: 'squirrel-dictionary',
                widgetOptions: JSON.stringify(options),
                defaultValue: JSON.stringify(options.dictDefault || {})
            },
            'list': {
                widgetType: 'squirrel-list',
                widgetOptions: JSON.stringify(options),
                defaultValue: JSON.stringify(options.listDefault || [])
            },
            'sq_action': {
                widgetType: 'squirrel-action',
                widgetOptions: false,
                defaultValue: false
            }
        };
        return configs[type] || null;
    }

    static _createWidget(widgetType, widgetOptions, defaultValue) {
        const element = document.createElement('textarea');
        element.setAttribute('widget', widgetType);
        if (widgetOptions) element.setAttribute('options', widgetOptions);
        if (defaultValue) element.value = defaultValue;
        return element;
    }
}
