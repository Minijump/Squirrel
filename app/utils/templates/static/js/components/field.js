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
 * @property {string} [placeholder] - Placeholder text for text, password, textarea, and number inputs
 * @property {boolean} [required=true] - Whether the input is required
 * @property {boolean} [invisible=false] - Whether the input is hidden
 * @property {Array<Array<string>>|Object} [select_options] - Set select input options: [['value1', 'Label 1'], ['value2', 'Label 2'], ...]
 * @property {Object} [dict_options={'create': true, 'remove': true}] - Set dict input options
 * @property {Object} [dict_default={}] - Default value for the dictionnary input
 * @property {string} [accept] - File input accept attribute (e.g., '.txt,.csv')
 * @property {string} [step='any'] - Step attribute for number inputs
 * @property {string} [className] - CSS class name(s) to add to the input element
 * @property {string} [onchange] - JavaScript code to execute on change event
 * @property {string} [select_onchange] - CSS class for conditional display logic
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
        this.inputDivHTML = this.generateInputdiv(inputInfo, inputId);
    }

    generateInputdiv(inputInfo, inputId) {
        const inputDivHTML = document.createElement('div');
        
        const input = this.createInput(inputInfo);
        input.name = input.id = inputId;
        input.required = (inputInfo.required !== undefined) ? inputInfo.required : true;

        // Add select_onchange classes to the container div
        if (inputInfo.select_onchange) {
            inputDivHTML.className += ' select-onchange ';
            inputDivHTML.className += inputInfo.select_onchange;
        }

        if (inputInfo.invisible) input.type = 'hidden';
        else{
            const label = this.createLabel(inputInfo);
            label && inputDivHTML.appendChild(label);
            const infoNote = this.createInfoNote(inputInfo);
            infoNote && inputDivHTML.appendChild(infoNote);
        }

        inputDivHTML.appendChild(input);
        if (inputInfo.type === 'dict') new SquirrelDictionary(input);
        return inputDivHTML;
    }

    createInput(input) {
        let formInput = document.createElement('input');
        if (['password', 'date', 'number', 'file'].includes(input.type)) formInput.type = input.type;

        if (input.type === 'number') formInput.step = input.step || 'any';
        if (input.type === 'file' && input.accept) formInput.accept = input.accept;
        if (input.type === 'textarea') formInput = document.createElement('textarea');
        if (input.type === 'dict') {
            formInput = document.createElement('textarea');
            formInput.setAttribute('widget', 'squirrel-dictionary');
            input.dict_options && formInput.setAttribute('options', JSON.stringify(input.dict_options));
            formInput.value = JSON.stringify(input.dict_default || {});
        }
        if (input.type === 'select') {
            formInput = document.createElement('select');
            input.select_options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option[0];
                optionElement.text = option[1];
                formInput.appendChild(optionElement);
            });
        }

        if (['text', 'password', 'textarea', 'number'].includes(input.type) && input.placeholder) {
            formInput.placeholder = input.placeholder;
        }

        // Add support for onchange attribute
        if (input.onchange) {
            formInput.setAttribute('onchange', input.onchange);
        }

        // Add support for custom CSS classes
        if (input.className) {
            formInput.className = input.className;
        }

        return formInput;
    }

    createLabel(input) {
        if (!input.label) return null;

        const label = document.createElement('label');
        label.innerHTML = input.label;
        return label;
    }

    createInfoNote(input) {
        if (!input.info) return null;

        const infoNote = document.createElement('div');
        infoNote.className = 'info-note';
        infoNote.innerHTML = `<i class="fas fa-info-circle"></i> ${input.info}`;
        return infoNote;
    }

    // TODO: add an easy way to bind events to inputs? (or in Form class?)
    // TODO: add a way to 'sanitize' data (create a new class Input, so we can we it in dict widget?)
}
