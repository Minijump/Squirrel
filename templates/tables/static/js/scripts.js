function saveSelectedTable(tableName) {
    localStorage.setItem('selectedTable', tableName);
}
function getSelectedTable() {
    return localStorage.getItem('selectedTable');
}
function showTable(tableName) {
    document.querySelectorAll('.table-container').forEach(function(table) {
        table.style.display = 'none';
    });
    document.getElementById('table-' + tableName).style.display = 'block';

    document.querySelectorAll('.select-table-btn').forEach(function(button) {
        button.classList.remove('active');
    });
    document.querySelectorAll('.select-table-btn').forEach(function(button) {
        if (button.textContent.trim() === tableName) {
            button.classList.add('active');
        }
    });
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

// Sidebar
function closeSidebarForm(id) {
    document.getElementById(id).style.width = "0";
}
function openSidebarForm(id, data = {}) {
    const form = document.getElementById(id);
    form.style.width = "250px";
    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            form.querySelector(`input[name="${key}"]`).value = data[key];
        }
    }
}

// InfoColModal
function formatNumber(num) {
    if (typeof num === 'string' && !isNaN(num)) {
        num = parseFloat(num);
    }
    return (typeof num === 'number' && num % 1 !== 0) ? num.toFixed(2) : num;
}
async function openInfoColModal(colName, tableName) {
    const projectDir = document.querySelector('input[name="project_dir"]').value;
    document.getElementById('InfoColModal').style.display = "flex";
    document.getElementById('modalTitle').innerHTML = `<b>${colName}</b>`;
    document.querySelector('#InfoColModal input[name="table_name"]').value = tableName;
    document.querySelector('#InfoColModal input[name="col_name"]').value = colName;

    try {
        const response = await fetch(`/tables/column_infos/?project_dir=${projectDir}&table=${tableName}&column=${colName}`);
        if (!response.ok) {
            throw new Error(`Error in response${response.status}`);
        }
        const data = await response.json();

        const fields = ['dtype', 'count', 'unique', 'null',
                        'is_numeric', 'mean', 'std', 'min', '25', '50', '75', 'max'];
        fields.forEach(field => {
            if (field === 'is_numeric') {
                const numericDivs = document.querySelectorAll('.numeric-only');
                numericDivs.forEach(div => {
                    div.style.display = data[field] ? 'inline' : 'none';
                });
                return;
            }

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
        document.getElementById('error_infos_computattion').innerHTML = `Error computing informations: ${error.message}`;
    }
}
function closeInfoColModal() {
    document.getElementById('InfoColModal').style.display = "none";
}

// Add info buttons to the table headers
function addInfoButtons() {
    document.querySelectorAll('.df-table thead').forEach(function(thead) {
        const lastTr = thead.querySelector('tr:last-child');
        lastTr.querySelectorAll('th').forEach(function(th) {
            const colName = th.textContent.trim();
            const infoColButton = document.createElement('button');
            infoColButton.className = 'table-header-btn';
            infoColButton.innerHTML = '&middot;&middot;&middot;';
            const tableName = th.closest('.table-container').id.split('-')[1];
            infoColButton.onclick = function() {
                openInfoColModal(colName, tableName);
            };
            if (!th.querySelector('.table-header-btn')) {
                th.appendChild(infoColButton);
            }
        });
    });
}

// Pager logic 
// + Add the info buttons
document.addEventListener('DOMContentLoaded', function() {
    addInfoButtons();

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
