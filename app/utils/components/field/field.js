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
        this.inputDivHTML = this._build(inputInfo, inputId, defaultValue);
    }

    _build(inputInfo, inputId, defaultValue) {
        const container = document.createElement('div');
        const input = this._createInput(inputInfo, inputId, defaultValue);
        
        this._configureVisibility(container, input, inputInfo);
        this._appendLabelAndInfo(container, inputInfo);
        
        container.appendChild(input);
        this._initializeWidget(input, inputInfo.type);
        
        return container;
    }

    _createInput(inputInfo, inputId, defaultValue) {
        const input = Input.createInput(inputInfo.type, {
            placeholder: inputInfo.placeholder,
            className: inputInfo.className,
            onchange: inputInfo.onchange,
            step: inputInfo.step,
            accept: inputInfo.accept,
            selectOptions: inputInfo.select_options,
            dictOptions: inputInfo.dict_options,
            dictDefault: inputInfo.dict_default,
            listOptions: inputInfo.list_options,
            listDefault: inputInfo.list_default
        });
        
        input.name = input.id = inputId;
        
        if (defaultValue !== undefined) {
            input.value = (inputInfo.type === 'dict' || inputInfo.type === 'list')
                ? (typeof defaultValue === 'string' ? defaultValue : JSON.stringify(defaultValue))
                : defaultValue;
        }
        
        if (inputInfo.invisible) input.type = 'hidden';
        
        return input;
    }

    _configureVisibility(container, input, inputInfo) {
        const isRequired = inputInfo.required ?? true;
        
        if (inputInfo.onchange_visibility) {
            const [triggerField, triggerValue] = inputInfo.onchange_visibility;
            container.classList.add('onchange-visibility');
            container.dataset.visibilitytrigger = triggerField;
            container.dataset.visibilityvalue = triggerValue;
            container.dataset.requiredwhenvisible = isRequired;
        } else {
            input.required = isRequired;
        }
    }

    _appendLabelAndInfo(container, inputInfo) {
        if (inputInfo.invisible) return;
        
        if (inputInfo.label) {
            const label = document.createElement('label');
            label.innerHTML = inputInfo.label;
            container.appendChild(label);
        }
        
        if (inputInfo.info) {
            const infoNote = document.createElement('div');
            infoNote.className = 'info-note';
            infoNote.innerHTML = `<i class="fas fa-info-circle"></i> ${inputInfo.info}`;
            container.appendChild(infoNote);
        }
    }

    _initializeWidget(input, type) {
        if (type === 'dict') new SquirrelDictionary(input);
        else if (type === 'list') new SquirrelList(input);
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
