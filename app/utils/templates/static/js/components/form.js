export class AutocompleteForm {
    // TODO doc on diff inputs info
    constructor(options = {}) {
        this.id = options.id || 'form-' + Math.random().toString(36).substring(2, 11);
        this.inputs = options.inputs || {};
        this.submitRoute = options.submitRoute || '';
        this.data = options.data || {};
        this.formCode = null;
        this.create();
    }

    create() {
        const form = this.createForm();
        Object.keys(this.inputs).forEach(key => {
            let input
            let label = null;
            let infoNote
            if (this.inputs[key].invisible) {
                input = this.createInput(this.inputs[key]);
                input.type = 'hidden';
            }
            else{
                label = this.createLabel(this.inputs[key]);
                infoNote = this.createInfoNote(this.inputs[key]);
                input = this.createInput(this.inputs[key]);
                input.required = (this.inputs[key].required !== undefined) ? this.inputs[key].required : true;
            }
            input.name = key;
            input.id = key;
            if (label) {
                form.appendChild(label);
            }
            if (infoNote) {
                form.appendChild(infoNote);
            }
            form.appendChild(input);
            if (this.inputs[key].type === 'dict') {
                new SquirrelDictionary(input);
            }
        });
        
        this.completeInputs(form, this.data);

        const submitButton = this.createSubmitButton();
        form.appendChild(submitButton);

        this.formCode = form.outerHTML;
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

    createInput(input) {
        let formInput = document.createElement('input');
        if (input.type === 'txt') {
            formInput = document.createElement('textarea');
        }
        if (input.type === 'dict') {
            formInput = document.createElement('textarea');
            formInput.setAttribute('widget', 'squirrel-dictionary');
            if (input.options) {
                const options = input.options ;
                const str_options = JSON.stringify(options);
                formInput.setAttribute('options', str_options);
            }
            formInput.value = JSON.stringify(input.default || {});
        }
        if (input.type === 'number') {
            formInput.type = 'number';
            formInput.step = input.step || 'any';
        }
        if (input.type === 'select') {
            formInput = document.createElement('select');
            input.options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option[0];
                optionElement.text = option[1];
                formInput.appendChild(optionElement);
            });
        }
        if (input.onchange) {
            formInput.setAttribute('onchange', input.onchange);
        }
        if (input.select_onchange) {
            formInput.classList.add('select-onchange');
            formInput.classList.add(input.select_onchange);
        }
        // TODO: add placeholder
        return formInput;
    }

    createLabel(input) {
        const label = document.createElement('label');
        label.innerHTML = input.string;
        if (input.select_onchange) {
            label.classList.add('select-onchange');
            label.classList.add(input.select_onchange);
        };
        return label;
    }

    createInfoNote(input) {
        if (input.info) {
            const infoNote = document.createElement('div');
            infoNote.className = 'info-note';
            infoNote.innerHTML = `<i class="fas fa-info-circle"></i> ${input.info}`;
            if (input.select_onchange) {
                infoNote.classList.add('select-onchange');
                infoNote.classList.add(input.select_onchange);
            };
            return infoNote;
        };
        return null;
    }

    createSubmitButton() {
        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.className = 'btn-primary';
        submitButton.textContent = 'Confirm';
        return submitButton;
    }

    completeInputs(form, data={}) {
        for (const key in data) {
            if (data.hasOwnProperty(key)) {
                const inputElement = form.querySelector(`#${key}`);
                if (inputElement) {
                    inputElement.value = data[key];
                } else {
                    console.warn(`Element with id ${key} not found in the form.`);
                }
            }
        }
    }

    toggleSelect(select) {
        // TODO: fix this (won't work if multiple selects + ...)
        let toggleOptionalArgs = document.querySelectorAll(".select-onchange");
        toggleOptionalArgs.forEach(element => {
            if (element.classList.contains(select.value)) {
                element.style.display = "block";
                element.required = true;
            } else {
                element.style.display = "none";
                element.required = false
            }
        });
    }
}
