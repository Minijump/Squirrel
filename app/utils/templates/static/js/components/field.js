import { SquirrelDictionary } from '/static/base/js/widgets/dictionary_widget.js';


/**
 * // Structure of inputInfo to create a field:
 * 
 * @property {string} type - Input type
 *   - 'text': string input
 *   - 'textarea': textarea input
 *   - 'dict': squirrel dict
 *   - 'number': number input
 *   - 'select': dropdown select
 *   - 'file': file input
 *   - 'password': password input (text with type 'password')
 *   - 'date': date input
 * @property {string} [label] - Input label text
 * @property {string} [info] - Info text displayed above input (supports HTML)
 * @property {string} [placeholder] - Placeholder text for input and textarea
 * @property {boolean} [required=true] - Whether the input is required
 * @property {boolean} [invisible=false] - Whether the input is hidden
 * @property {Array<Array<string>>|Object} [select_options] - Set select input options: [['value1', 'Label 1'], ['value2', 'Label 2'], ...]
 * @property {Object} [dict_options] - Set dict input options: {create: boolean, remove: boolean} (default: {create: true, remove: true})
 * @property {string} [accept] - File input accept attribute (e.g., '.txt,.csv')
 *  
 * @example
 *   username: {
 *     type: 'text',
 *     label: 'Username',
 *     required: true,
 *     placeholder: 'Enter your username',
 *     info: 'This will be your login name'
 *   },
 *   category: {
 *     type: 'select',
 *     label: 'Category',
 *     select_options: [['cat1', 'Category 1'], ['cat2', 'Category 2']]
 *   },
 *  fileUpload: {
 *    type: 'file',
 *    label: 'Upload File',
 *    accept: '.txt,.csv',
 *   },
 */
export class Field {
    constructor(inputId, inputInfo) {
        this.id = 'field-' + Math.random().toString(36).substring(2, 11);
        this.inputInfo = inputInfo;
        this.inputId = inputId;
        this.inputDiv = this.generateInputdiv(inputInfo, inputId);
    }

    generateInputdiv(inputInfo, inputId) {
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
        if (input.type === 'text') {
            if (input.placeholder) {
                formInput.placeholder = input.placeholder;
            }
        }
        if (input.type === 'password') {
            formInput.type = 'password';
            if (input.placeholder) {
                formInput.placeholder = input.placeholder;
            }
        }
        if (input.type === 'date') {
            formInput.type = 'date';
        }
        if (input.type === 'textarea') {
            formInput = document.createElement('textarea');
            if (input.placeholder) {
                formInput.placeholder = input.placeholder;
            }
        }
        if (input.type === 'dict') {
            formInput = document.createElement('textarea');
            formInput.setAttribute('widget', 'squirrel-dictionary');
            if (input.dict_options) {
                const options = input.dict_options ;
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
            console.log(input.select_options);
            input.select_options.forEach(option => {
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
        label.innerHTML = input.label;
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

    // TODO: add an easy way to bind events to inputs? (or in Form class?)
}
