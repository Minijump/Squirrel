import { Input } from '/static/utils/components/input/input.js';
import { SquirrelDictionary } from '/static/utils/widgets/dictionary_widget/dictionary_widget.js';
import { SquirrelList } from '/static/utils/widgets/list_widget/list_widget.js';


/**
 * // Structure of inputInfo to create a field:
 * 
 * @property {string} type - Input type
 *   - 'text': string input
 *   - 'textarea': textarea input
 *   - 'dict': squirrel dict
 *   - 'list': squirrel list
 *   - 'number': number input
 *   - 'select': dropdown select
 *   - 'file': file input
 *   - 'password': password input (text with type 'password')
 *   - 'date': date input
 * @property {string} [label] - Input label text
 * @property {string} [info] - Info text displayed above input (supports HTML)
 * @property {string} [placeholder] - Placeholder text for text, password, textarea, and number inputs
 * @property {boolean} [required=true] - Whether the input is required (for field displayed conditionally, only required if dislayed)
 * @property {boolean} [invisible=false] - Whether the input is hidden
 * @property {Array<Array<string>>|Object} [select_options] - Set select input options: [['value1', 'Label 1'], ['value2', 'Label 2'], ...]
 * @property {Object} [dict_options={'create': true, 'remove': true}] - Set dict input options
 * @property {Object} [dict_default={}] - Default value for the dictionnary input
 * @property {Object} [list_options={'create': true, 'remove': true}] - Set list input options
 * @property {Array} [list_default=[]] - Default value for the list input
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
    constructor(inputId, inputInfo, defaultValue = undefined) {
        this.id = 'field-' + Math.random().toString(36).substring(2, 11);
        this.inputDivHTML = this.generateInputdiv(inputInfo, inputId, defaultValue);
    }

    generateInputdiv(inputInfo, inputId, defaultValue = undefined) {
        const inputDivHTML = document.createElement('div');
        
        const input = this.createInput(inputInfo, defaultValue);
        input.name = input.id = inputId;
        if (!inputInfo.onchange_visibility){
            // For field displayed conditionally, see 'onchangeFormValue'
            input.required = (inputInfo.required !== undefined) ? inputInfo.required : true;
        }

        if (inputInfo.onchange_visibility) {
            inputDivHTML.classList.add('onchange-visibility');
            const [triggerField, triggerValue] = inputInfo.onchange_visibility;
            inputDivHTML.dataset.visibilitytrigger = triggerField;
            inputDivHTML.dataset.visibilityvalue = triggerValue;
            inputDivHTML.dataset.requiredwhenvisible = (inputInfo.required !== undefined) ? inputInfo.required : true;
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
        if (inputInfo.type === 'list') new SquirrelList(input);
        return inputDivHTML;
    }

    createInput(input, defaultValue = undefined) {
        let formInput;
        
        const inputOptions = {
            placeholder: input.placeholder,
            className: input.className,
            onchange: input.onchange,
            step: input.step,
            accept: input.accept,
            selectOptions: input.select_options,
            dictOptions: input.dict_options,
            dictDefault: input.dict_default,
            listOptions: input.list_options,
            listDefault: input.list_default
        };
        
        formInput = Input.createInput(input.type, inputOptions);
        
        if (defaultValue !== undefined) {
            if (input.type === 'dict' || input.type === 'list') {
                formInput.value = typeof defaultValue === 'string' ? defaultValue : JSON.stringify(defaultValue);
            } else {
                formInput.value = defaultValue;
            }
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
}

function onchangeFormValue(onchangeId, event) {
    const fields = document.querySelectorAll('.onchange-visibility');
    fields.forEach(field => {
        const triggerOnchageId = field.dataset.visibilitytrigger;
        const triggerValue = field.dataset.visibilityvalue;
        const requiredWhenVisible = field.dataset.requiredwhenvisible === 'true';
        const inputElement = event.target

        const shouldBeVisible = (triggerOnchageId === onchangeId && inputElement.value === triggerValue);
        if (shouldBeVisible) field.style.display = 'block';
        else field.style.display = 'none';
        if (requiredWhenVisible){
            const input = field.querySelector('input, select, textarea');
            if (input) input.required = shouldBeVisible;
        }
    });
};
window.onchangeFormValue = onchangeFormValue;
