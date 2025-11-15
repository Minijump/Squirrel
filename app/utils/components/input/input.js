export class Input {
    static createInput(type, options = {}) {
        if (type === 'dict') return Input._createWidget('squirrel-dictionary', options.dictOptions, options.dictDefault || {});
        if (type === 'list') return Input._createWidget('squirrel-list', options.listOptions, options.listDefault || []);
        
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

    static _createWidget(widgetType, widgetOptions, defaultValue) {
        const element = document.createElement('textarea');
        element.setAttribute('widget', widgetType);
        if (widgetOptions) element.setAttribute('options', JSON.stringify(widgetOptions));
        element.value = JSON.stringify(defaultValue);
        return element;
    }
}
