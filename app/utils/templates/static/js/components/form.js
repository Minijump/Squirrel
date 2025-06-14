import { SquirrelDictionary } from '/static/base/js/widgets/dictionary_widget.js';


/**
 * // Structure for options.inputs parameter:
 * 
 * @property {'str'|'txt'|'dict'|'number'|'select'|'file'} type - Input type
 *   - 'str': string input TODO: rename to 'text'
 *   - 'txt': textarea TODO: rename to 'textarea'
 *   - 'dict': squirrel dict
 *   - 'number': number input
 *   - 'select': dropdown select
 *   - 'file': file input
 *   - TODO: password, date
 * @property {string} [string] - Input label text TODO: rename to 'label'
 * @property {string} [info] - Info text displayed above input (supports HTML)
 * @property {string} [placeholder] - Placeholder text for input and textarea
 * @property {boolean} [required=true] - Whether the input is required
 * @property {boolean} [invisible=false] - Whether the input is hidden
 * @property {Array<Array<string>>|Object} [options] - Configuration options:
 *   - For 'select' type: [['value1', 'Label 1'], ['value2', 'Label 2'], ...]
 *   - For 'dict' type: {create: boolean, remove: boolean} (default: {create: true, remove: true})
 *   TODO: differentiate options in: select_options, dict_options
 * @property {string} [accept] - File input accept attribute (e.g., '.txt,.csv')
 *  
 * @example
 * const formInputs = {
 *   username: {
 *     type: 'str',
 *     string: 'Username',
 *     required: true
 *   },
 *   description: {
 *     type: 'txt',
 *     string: 'Description',
 *     info: 'Enter a detailed description'
 *   },
 *   category: {
 *     type: 'select',
 *     string: 'Category',
 *     options: [['cat1', 'Category 1'], ['cat2', 'Category 2']]
 *   },
 *  fileUpload: {
 *    type: 'file',
 *    string: 'Upload File',
 *    accept: '.txt,.csv',
 * };
 */
export class AutocompleteForm {
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
            const inputDiv = this.generateInputdiv(this.inputs[key], key);
            form.appendChild(inputDiv);
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

    generateInputdiv(inputInfo, inputId) {
        console.log('generateInputdiv', inputInfo, inputId);
        let inputDiv = document.createElement('div');
        let input
        let label = null;
        let infoNote
        if (inputInfo.invisible) {
            input = this.createInput(inputInfo);
            input.type = 'hidden';
        }
        else{
            label = this.createLabel(inputInfo);
            infoNote = this.createInfoNote(inputInfo);
            input = this.createInput(inputInfo);
            input.required = (inputInfo.required !== undefined) ? inputInfo.required : true;
        }
        input.name = inputId;
        input.id = inputId;
        if (label) {
            inputDiv.appendChild(label);
        }
        if (infoNote) {
            inputDiv.appendChild(infoNote);
        }
        inputDiv.appendChild(input);
        if (inputInfo.type === 'dict') {
            new SquirrelDictionary(input);
        }
        return inputDiv;
    }

    createInput(input) {
        let formInput = document.createElement('input');
        if (input.type === 'str') {
            if (input.placeholder) {
                formInput.placeholder = input.placeholder;
            }
        }
        if (input.type === 'txt') {
            formInput = document.createElement('textarea');
            if (input.placeholder) {
                formInput.placeholder = input.placeholder;
            }
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
            if (input.placeholder) {
                formInput.placeholder = input.placeholder;
            }
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
        if (input.type === 'file') {
            formInput.type = 'file';
            formInput.accept = input.accept || '*/*';
        }

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

    // TODO: add an easy way to bind events to inputs?
    // TODO: create a input component instead of filling form
}
