import { Field } from './field.js';


export class Form {
    constructor(options = {}) {
        this.id = options.id || 'form-' + Math.random().toString(36).substring(2, 11);
        this.inputs = options.inputs || {};
        this.submitRoute = options.submitRoute || '';
        this.data = options.data || {};
        this.formHTML = null;
        this.create();
    }

    create() {
        const form = this.createForm();
        Object.keys(this.inputs).forEach(key => {
            const input = new Field(key, this.inputs[key]);
            form.appendChild(input.inputDivHTML);
        });
        form.appendChild(this.createSubmitButton());
        this.completeInputs(form, this.data);

        this.formHTML = form;
    }

    createForm() {
        const form = document.createElement('form');
        form.id = this.id;
        form.className = 'std-form';
        form.method = 'post';
        form.action = this.submitRoute;
        form.enctype = 'multipart/form-data';
        return form;
    }

    createSubmitButton() {
        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.className = 'btn-primary';
        submitButton.textContent = 'Confirm';
        return submitButton;
    }

    completeInputs(form, data={}) {
        Object.keys(data).forEach(key => {
            const inputElement = form.querySelector(`#${key}`);
            if (inputElement) inputElement.value = data[key];
            else console.warn(`Element with id ${key} not found in the form.`);
        });
    }

    // TODO: add an easy way to bind events to inputs? (or in Field class) + fill data in input?
}
