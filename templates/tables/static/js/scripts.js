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

function openDelColForm(colName, tableName) {
    console.log(tableName)
    openForm('DelColForm');
    document.getElementById('del_col_name').value = colName;
    document.querySelector('#DelColForm input[name="table_name"]').value = tableName;
}

document.addEventListener('DOMContentLoaded', function() {
    function addDeleteButtons() {
        // Add delete buttons to each column
        document.querySelectorAll('.df-table th').forEach(function(th) {
            const colName = th.textContent.trim();
            const delButton = document.createElement('button');
            delButton.className = 'table-header-btn';
            delButton.innerHTML = '&middot;&middot;&middot;';
            const tableName = th.closest('.table-container').id.split('-')[1];
            delButton.onclick = function() {
                openDelColForm(colName, tableName);
            };
            th.appendChild(delButton);
        });
    }
    addDeleteButtons(); // Initial call

    document.querySelectorAll('.pager').forEach(function(pager) {
        const tableName = pager.dataset.table;
        let currentPage = 0;
        const n = 10;
        const tableNumLines = pager.dataset.len

        function loadPage(page) {
            fetch(`/tables/pager/?project_dir={{ project_dir }}&table_name=${tableName}&page=${page}&n=${n}`)
                .then(response => response.text())
                .then(data => {
                    let cleanData = data.replace(/\\n/g, '').replace(/\\/g, '').slice(1, -1);;
                    document.getElementById(`table-html-${tableName}`).innerHTML = cleanData;
                    currentPage = page;

                    const startElement = page * n + 1;
                    const endElement = startElement + n - 1;
                    document.getElementById(`pager-info-${tableName}`).innerText = `${startElement}-${endElement} / ${tableNumLines}`;
                    addDeleteButtons();
                })
                .catch(error => console.error('Error:', error));
        }

        pager.querySelector('.prev').addEventListener('click', function() {
            if (currentPage > 0) {
                loadPage(currentPage - 1);
            }
        });

        pager.querySelector('.next').addEventListener('click', function() {
            const lastElement = currentPage * n + n;
            if (lastElement < tableNumLines) {
                loadPage(currentPage + 1);
            }
        });
    });

});
