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
                    input.required = true;
                }
                input.name = key;
                input.id = key;
                argsDiv.appendChild(input);
        });
    });
}
async function openSidebarActionForm(action, data = {}) {
    const form = document.getElementById("ActionSidebar");
    form.style.width = "250px";
    await addInputs(action, form);
    completeInputs(form, action, data);
    toggleSelect();
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
                    div.style.display = data[field] ? 'inline' : 'none';
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
                    document.getElementById(`pager-info-${tableName}`).innerText = `${startElement}-${endElement} / ${tableNumLines}`;
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
