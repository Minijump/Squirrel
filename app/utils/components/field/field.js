import { Input } from '/static/utils/components/input/input.js';
import { SquirrelDictionary } from '/static/utils/widgets/dictionary_widget/dictionary_widget.js';


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
 * @property {Array} [onchange_visibility] - [onchange_id, value where the input should be visible]
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

        if (inputInfo.onchange_visibility) {
            inputDivHTML.classList.add('onchange-visibility');
            const [triggerField, triggerValue] = inputInfo.onchange_visibility;
            inputDivHTML.dataset.visibilitytrigger = triggerField;
            inputDivHTML.dataset.visibilityvalue = triggerValue;
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
        let formInput;
        
        const inputOptions = {
            placeholder: input.placeholder,
            className: input.className,
            onchange: input.onchange,
            step: input.step,
            accept: input.accept,
            selectOptions: input.select_options,
            dictOptions: input.dict_options,
            dictDefault: input.dict_default
        };
        formInput = Input.createInput(input.type, inputOptions);

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
}

function onchangeFormValue(onchangeId, event) {
    const fields = document.querySelectorAll('.onchange-visibility');
    fields.forEach(field => {
        const triggerOnchageId = field.dataset.visibilitytrigger;
        const triggerValue = field.dataset.visibilityvalue;
        const inputElement = event.target

        if (triggerOnchageId === onchangeId && inputElement.value === triggerValue) field.style.display = 'block';
        else field.style.display = 'none';
    });
};
window.onchangeFormValue = onchangeFormValue;
