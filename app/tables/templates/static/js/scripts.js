// Table selection ---------------------------------------------------------------
function saveSelectedTable(tableName) {
    localStorage.setItem('selectedTable', tableName);
}
function getSelectedTable() {
    return localStorage.getItem('selectedTable');
}
function showTable(tableName) {
    // Show selected table
    document.querySelectorAll('.table-container').forEach(function(table) {
        table.style.display = 'none';
    });
    document.getElementById('table-' + tableName).style.display = 'block';

    // Change selected table button
    document.querySelectorAll('.select-table-btn').forEach(function(button) {
        button.classList.remove('active');
    });
    document.querySelectorAll('.select-table-btn').forEach(function(button) {
        if (button.textContent.trim() === tableName) {
            button.classList.add('active');
        }
    });

    // Save selected table
    saveSelectedTable(tableName);
}
document.addEventListener('DOMContentLoaded', function() {
    const selectedTable = getSelectedTable();
    if (selectedTable && document.getElementById('table-' + selectedTable)) {
        showTable(selectedTable);
    } else {
        const firstTableButton = document.querySelector('.select-table-btn');
        if (firstTableButton) {
            showTable(firstTableButton.textContent.trim());
        }
    }
});

// Sidebar ---------------------------------------------------------------
function getColumnInfo(additionalData = {}) {
    let infos = {
        'table_name': document.querySelector('#InfoColModal input[name="table_name"]').value,
        'col_name': document.querySelector('#InfoColModal input[name="col_name"]').value,
        'col_idx': document.querySelector('#InfoColModal input[name="col_idx"]').value,
    };
    if (additionalData) {
        infos = {...infos, ...additionalData};
    };
    return infos;
}
function closeSidebarForm(id) {
    document.getElementById(id).style.width = "0";
}
function openSidebarForm(id, data = {}) {
    const form = document.getElementById(id);
    form.style.width = "250px";
    completeInputs(form, data);
    focusOnInput();
}
function completeInputs(form, action, data) {
    form.querySelector('input[name="action_name"]').value = action;
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
            // kwargsInput.value = JSON.stringify(kwargs);
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
    form.style.width = "250px";
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

// InfoColModal ---------------------------------------------------------------
function formatNumber(num) {
    if (typeof num === 'string' && !isNaN(num)) {
        num = parseFloat(num);
    }
    return (typeof num === 'number' && num % 1 !== 0) ? num.toFixed(2) : num;
}
async function openInfoColModal(colName, colIdx, tableName) {
    const projectDir = document.querySelector('input[name="project_dir"]').value;
    document.getElementById('InfoColModal').style.display = "flex";
    document.getElementById('modalTitle').innerHTML = `<b>${colName}</b>`;
    document.querySelector('#InfoColModal input[name="table_name"]').value = tableName;
    document.querySelector('#InfoColModal input[name="col_name"]').value = colName;
    document.querySelector('#InfoColModal input[name="col_idx"]').value = colIdx;

    try {
        const response = await fetch(`/tables/column_infos/?project_dir=${projectDir}&table=${tableName}&column_name=${colName}&column_idx=${colIdx}`);
        if (!response.ok) {
            throw new Error(`Error in response${response.status}`);
        }
        const data = await response.json();

        const fields = ['dtype', 'count', 'unique', 'null',
                        'is_numeric', 'mean', 'std', 'min', '25', '50', '75', 'max'];
        fields.forEach(field => {
            // display numeric divs (values and buttons)
            if (field === 'is_numeric') {
                const numericDivs = document.querySelectorAll('.numeric-only');
                numericDivs.forEach(div => {
                    div.style.display = data[field] ? 'block' : 'none';
                });
                return;
            }

            // display the fields
            const element = document.getElementById(`col_${field}`);
            if (!element) {
                return;
            }
            if (data[field] !== undefined) {
                element.style.display = 'inline';
                element.querySelector('span').innerText = `${formatNumber(data[field])}`;
            } else {
                element.style.display = 'none';
            }
        });
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('error_infos_computation').innerHTML = `Error computing informations: ${error.message}`;
    }
}
function closeInfoColModal() {
    document.getElementById('InfoColModal').style.display = "none";
}

// CustomActionModal ---------------------------------------------------------------
function openCustomActionModal() {
    document.getElementById('CustomActionModal').style.display = "flex";
}
function closeCustomActionModal() {
    document.getElementById('CustomActionModal').style.display = "none";
}

// Add info buttons to the table headers ---------------------------------------------------------------
function addInfoButtons() {
    document.querySelectorAll('.df-table thead').forEach(function(thead) {
        const lastTr = thead.querySelector('tr:last-child');
        lastTr.querySelectorAll('th').forEach(function(th) {
            const colName = th.textContent.trim();
            const colIdx = th.dataset.columnidx;
            const infoColButton = document.createElement('button');
            infoColButton.className = 'table-header-btn';
            infoColButton.innerHTML = '&middot;&middot;&middot;';
            const tableName = th.closest('.table-container').id.split('-')[1];
            infoColButton.onclick = function() {
                openInfoColModal(colName, colIdx, tableName);
            };
            if (!th.querySelector('.table-header-btn')) {
                th.appendChild(infoColButton);
            }
        });
    });
}
document.addEventListener('DOMContentLoaded', function() { addInfoButtons(); });

// Pager logic ---------------------------------------------------------------
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.pager').forEach(function(pager) {
        const tableName = pager.dataset.table;
        let currentPage = 0;
        const n = parseInt(pager.dataset.displaylen);
        const tableNumLines = parseInt(pager.dataset.totallen);
        const projectDir = pager.dataset.project_dir;

        function loadPage(page) {
            fetch(`/tables/pager/?project_dir=${projectDir}&table_name=${tableName}&page=${page}&n=${n}`)
                .then(response => response.text())
                .then(data => {
                    const cleanData = data.replace(/\\n/g, '').replace(/\\/g, '').slice(1, -1);
                    document.getElementById(`table-html-${tableName}`).innerHTML = cleanData;
                    currentPage = page;

                    const startElement = page * n + 1;
                    const endElement = startElement + n - 1;
                    const displayEndElement = Math.min(endElement, tableNumLines);                    
                    console.log(startElement, displayEndElement, tableNumLines);
                    document.getElementById(`pager-info-${tableName}`).innerText = `${startElement}-${displayEndElement} / ${tableNumLines}`;
                    addInfoButtons();
                })
                .catch(error => console.error('Error:', error));
        }

        pager.querySelector('#prev').addEventListener('click', function() {
            if (currentPage > 0) {
                loadPage(currentPage - 1);
            }
        });
        pager.querySelector('#next').addEventListener('click', function() {
            const lastElement = currentPage * n + n;
            if (lastElement < tableNumLines) {
                loadPage(currentPage + 1);
            }
        });
    });

});
