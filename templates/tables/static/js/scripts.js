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
}

function closeForm(id) {
    document.getElementById(id).style.width = "0";
}
function openForm(id) {
    document.getElementById(id).style.width = "250px";
}
function openActionForm(id, name) {
    const form = document.getElementById(id);
    form.style.width = "250px";
    form.querySelector('input[name="table_name"]').value = name;
}
function openInfoColForm(colName, tableName) {
    document.getElementById('InfoColForm').style.display = "flex";
    document.getElementById('del_col_name').value = colName;
    document.querySelector('#InfoColForm input[name="table_name"]').value = tableName;
    document.getElementById('modalTitle').innerHTML = `Column "<i>${colName}</i>" Infos`;
}
function closeInfoColForm() {
    document.getElementById('InfoColForm').style.display = "none";
}

function addInfoButtons() {
    document.querySelectorAll('.df-table th').forEach(function(th) {
        const colName = th.textContent.trim();
        const delButton = document.createElement('button');
        delButton.className = 'table-header-btn';
        delButton.innerHTML = '&middot;&middot;&middot;';
        const tableName = th.closest('.table-container').id.split('-')[1];
        delButton.onclick = function() {
            openInfoColForm(colName, tableName);
        };
        if (!th.querySelector('.table-header-btn')) {
            th.appendChild(delButton);
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    addInfoButtons();

    document.querySelectorAll('.pager').forEach(function(pager) {
        const tableName = pager.dataset.table;
        var currentPage = 0;
        const n = 10;
        const tableNumLines = pager.dataset.len
        const projectDir = pager.dataset.project_dir;

        function loadPage(page) {
            fetch(`/tables/pager/?project_dir=${projectDir}&table_name=${tableName}&page=${page}&n=${n}`)
                .then(response => response.text())
                .then(data => {
                    const cleanData = data.replace(/\\n/g, '').replace(/\\/g, '').slice(1, -1);;
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
