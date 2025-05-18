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
                    div.style.display = data[field] ? 'flex' : 'none';
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
function openCustomActionModal(tableName='') {
    document.getElementById('CustomActionModal').style.display = "flex";
    document.querySelector('#CustomActionModal input[name="default_table_name"]').value = tableName;
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
