import { Field } from '/static/utils/components/field/field.js';


export class Form {
    constructor(options = {}) {
        this.id = options.id || 'form-' + Math.random().toString(36).substring(2, 11);
        this.submitRoute = options.submitRoute || '';
        this.submitText = options.submitText || 'Confirm';
        this.formHTML = this._build(options.inputs || {}, options.data || {});
    }

    _build(inputs, data) {
        const form = this._createFormElement();
        
        Object.keys(inputs).forEach(key => {
            const field = new Field(key, inputs[key], data[key]);
            form.appendChild(field.inputDivHTML);
        });
        
        form.appendChild(this._createSubmitButton());
        
        return form;
    }

    _createFormElement() {
        const form = document.createElement('form');
        form.id = this.id;
        form.className = 'std-form';
        form.method = 'post';
        form.action = this.submitRoute;
        form.enctype = 'multipart/form-data';
        return form;
    }

    _createSubmitButton() {
        const button = document.createElement('button');
        button.type = 'submit';
        button.className = 'btn-primary';
        button.textContent = this.submitText;
        return button;
    }
}
