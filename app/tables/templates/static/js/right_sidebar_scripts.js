import { SquirrelDictionary } from '/static/base/js/widgets/dictionary_widget.js';

// Sidebar ---------------------------------------------------------------
function closeSidebarForm(id) {
    document.getElementById(id).style.width = "0";
    const overlay = document.getElementById("sidebar-overlay");
    overlay.style.display = "none";
}
function openSidebarForm(id, data = {}) {
    const form = document.getElementById(id);
    const overlay = document.getElementById("sidebar-overlay");
    form.style.width = "300px";
    overlay.style.display = "block";
    completeInputs(form, action=null, data=data);
    focusOnInput();
}
function completeInputs(form, action=null, data={}) {
    if (action !== null) {
        form.querySelector('input[name="action_name"]').value = action;
    }
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
function addLabel(argsDiv, arg) {
    const label = document.createElement('label');
    label.innerHTML = arg.string;
    if (arg.select_onchange) {
        label.className += ' select-onchange ';
        label.className += arg.select_onchange;
    };
    argsDiv.appendChild(label);

    if (arg.info) {
        const infoNote = document.createElement('div');
        infoNote.className = 'info-note';
        infoNote.innerHTML = `<i class="fas fa-info-circle"></i> ${arg.info}`;
        if (arg.select_onchange) {
            infoNote.className += ' select-onchange ';
            infoNote.className += arg.select_onchange;
        };
        argsDiv.appendChild(infoNote);
    };
}
function createInput(arg) {
    let input = document.createElement('input');
    if (arg.type === 'txt') {
        input = document.createElement('textarea');
    }
    if (arg.type === 'dict') {
        input = document.createElement('textarea');
        input.setAttribute('widget', 'squirrel-dictionary');
        defaultOptions = {create:true, remove:true};
        const userOptions = arg.options;
        const options = userOptions ? { ...defaultOptions, ...userOptions } : defaultOptions;
        const str_options = JSON.stringify(options);
        input.setAttribute('options', str_options);
        input.value = JSON.stringify(arg.default || {});
    }
    if (arg.type === 'number') {
        input.type = 'number';
        input.step = arg.step || 'any';
    }
    if (arg.type === 'select') {
        input = document.createElement('select');
        arg.options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option[0];
            optionElement.text = option[1];
            input.appendChild(optionElement);
        });
        input.className += 'right-sidebar-select';
    }
    if (arg.onchange) {
        input.setAttribute('onchange', arg.onchange);
    }
    if (arg.select_onchange) {
        input.className += ' select-onchange ';
        input.className += arg.select_onchange;
    }
    return input;
}
async function addInputs(action, form) {
    return fetch(`/tables/get_action_args/?action_name=${action}`)
        .then(response => response.json())
        .then(args => {
            const argsDiv = form.querySelector('#args');
            argsDiv.innerHTML = '';
            Object.keys(args).forEach(key => {
                let input
                if (args[key].invisible) {
                    input = createInput(args[key]);
                    input.type = 'hidden';
                }
                else{
                    addLabel(argsDiv, args[key]);
                    input = createInput(args[key]);
                    input.required = (args[key].required !== undefined) ? args[key].required : true;
                }
                input.name = key;
                input.id = key;
                argsDiv.appendChild(input);
                if (args[key].type === 'dict') {
                    new SquirrelDictionary(input);
                }
        });
    });
}
async function addKwargs(action, form, data = {}) {
    return fetch(`/tables/get_action_kwargs/?action_name=${action}`)
        .then(response => response.json())
        .then(kwargs => {
            const kwargsForm = form.querySelector('#args-kwargs-form');
            const kwargsBtn = form.querySelector('#kwargs-btn');
            if (Object.keys(kwargs).length === 0) {
                kwargsForm.style.display = 'none';
                kwargsBtn.style.display = 'none';
                return;
            }
            kwargsForm.style.display = 'block';
            kwargsBtn.style.display = 'block';
            
            kwargsForm.querySelector('input[name="action_name"]').value = action;
            for (const key in data) {
                if (data.hasOwnProperty(key)) {
                    const inputElement = kwargsForm.querySelector(`#${key}`);
                    if (inputElement) {
                        inputElement.value = data[key];
                    } else {
                        console.warn(`Element with id ${key} not found in the form.`);
                    }
                }
            }

            const kwargsDiv = form.querySelector('#args-kwargs');
            kwargsDiv.innerHTML = '';            
            const kwargsInput = document.createElement('textarea');
            kwargsInput.name = "kwargs";
            kwargsInput.setAttribute('widget', 'squirrel-dictionary');
            kwargsInput.value = JSON.stringify(kwargs, function(key, value) {
                // Convert JavaScript booleans to Python string representations
                if (typeof value === 'boolean') {
                    return value ? 'True' : 'False';  
                }
                // Convert JavaScript null to Python None
                if (value === null) {
                    return 'None';
                }
                return value;
            });
            kwargsDiv.appendChild(kwargsInput);
            new SquirrelDictionary(kwargsInput);
    });
}

async function openSidebarActionForm(action, data = {}) {
    const form = document.getElementById("ActionSidebar");
    const overlay = document.getElementById("sidebar-overlay");
    form.style.width = "300px";
    overlay.style.display = "block";
    await addInputs(action, form);
    await addKwargs(action, form, data);
    completeInputs(form, action, data);
    toggleSelect();
    focusOnInput();
}
function toggleSelect() {
    let Select = document.querySelector(".right-sidebar-select");
    let toggleOptionalArgs = document.querySelectorAll(".select-onchange");
    toggleOptionalArgs.forEach(element => {
        if (element.classList.contains(Select.value)) {
            element.style.display = "block";
            element.required = true;
        } else {
            element.style.display = "none";
            element.required = false
        }
    });
}
function focusOnInput() {
    let inputs = document.querySelectorAll('input, textarea');
    for (const input of inputs) {
        if (input.offsetParent !== null) { // Check if the element is visible
            input.focus();
            break;
        }
    }
}

function switchTab(evt, tabId) {
    var tabContents = document.querySelectorAll(".tab-content");
    tabContents.forEach(function(tab) {
        tab.classList.remove("active");
    });
    var tabButtons = document.querySelectorAll(".tab-button");
    tabButtons.forEach(function(button) {
        button.classList.remove("active");
    });
    
    document.getElementById(tabId).classList.add("active");
    evt.currentTarget.classList.add("active");
    
    syncFormValues();
}

function syncFormValues() {
    // Sync action name between forms
    var actionInputs = document.querySelectorAll(".sync-action-name");
    var actionValue = "";
    actionInputs.forEach(function(input) {
        if (input.value) actionValue = input.value;
    });
    actionInputs.forEach(function(input) {
        input.value = actionValue;
    });
    
    // Sync table name between forms
    var tableInputs = document.querySelectorAll(".sync-table-name");
    var tableValue = "";
    tableInputs.forEach(function(input) {
        if (input.value) tableValue = input.value;
    });
    tableInputs.forEach(function(input) {
        input.value = tableValue;
    });
}

// Create-Table Sidebar -------------------------------------------------------
function sourceCreationTypeToggle() {
    let select_value = document.getElementById('source_creation_type').value;
    let elements = document.getElementsByClassName('data_source_type_onchange');
    
    for (let i = 0; i < elements.length; i++) {
        if (elements[i].classList.contains(select_value)) {
            elements[i].style.display = "block";
        } else {
            elements[i].style.display = "none";
        }
    }
}
document.getElementById('source_creation_type').addEventListener('change', sourceCreationTypeToggle);
document.addEventListener('DOMContentLoaded', function() { sourceCreationTypeToggle(); });


window.closeSidebarForm = closeSidebarForm;
window.openSidebarForm = openSidebarForm;
window.openSidebarActionForm = openSidebarActionForm;
window.switchTab = switchTab;
window.syncFormValues = syncFormValues;
window.sourceCreationTypeToggle = sourceCreationTypeToggle;
