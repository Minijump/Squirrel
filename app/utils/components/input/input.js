export class Input {
    constructor(type, options = {}) {
        this.type = type;
        this.options = {
            placeholder: '',
            value: '',
            readonly: false,
            className: '',
            step: 'any',
            accept: '',
            onchange: '',
            selectOptions: [],
            widget: '',
            ...options
        };
    }

    create() {
        let element;
        
        if (this.type === 'textarea') {
            element = document.createElement('textarea');
        } else if (this.type === 'select') {
            element = document.createElement('select');
            this.options.selectOptions.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option[0];
                optionElement.text = option[1];
                element.appendChild(optionElement);
            });
        } else {
            element = document.createElement('input');
            element.type = this.type;
        }

        if (this.options.placeholder && ['text', 'password', 'textarea', 'number'].includes(this.type)) {
            element.placeholder = this.options.placeholder;
        }

        if (this.options.value !== undefined && this.type !== 'select') {
            // For select, default value is the first one in options
            element.value = this.options.value;
        }

        if (this.options.readonly) {
            element.readOnly = true;
        }

        if (this.options.className) {
            element.className = this.options.className;
        }

        if (this.type === 'number' && this.options.step) {
            element.step = this.options.step;
        }

        if (this.type === 'file' && this.options.accept) {
            element.accept = this.options.accept;
        }

        if (this.options.widget) {
            element.setAttribute('widget', this.options.widget);
        }

        if (this.options.onchange) {
            element.setAttribute('onchange', this.options.onchange);
            element.classList.add('onchange-trigger');
        }

        return element;
    }

    static createInput(type, options = {}) {
        if (type === 'dict') {
            return  new Input(type, options).createDict(options);
        }
        if (type === 'list') {
            return  new Input(type, options).createList(options);
        }
        return new Input(type, options).create();
    }

    createDict(options = {}) {
        const element = document.createElement('textarea');
        element.setAttribute('widget', 'squirrel-dictionary');
        if (options.dictOptions) {
            element.setAttribute('options', JSON.stringify(options.dictOptions));
        }
        element.value = JSON.stringify(options.dictDefault || {});
        return element;
    }

    createList(options = {}) {
        const element = document.createElement('textarea');
        element.setAttribute('widget', 'squirrel-list');
        if (options.listOptions) {
            element.setAttribute('options', JSON.stringify(options.listOptions));
        }
        element.value = JSON.stringify(options.listDefault || []);
        return element;
    }
}
