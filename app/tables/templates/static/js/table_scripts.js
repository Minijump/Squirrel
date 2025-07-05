import { openCustomActionModal } from './custom_action_modal.js';
import { InfoColModal } from './info_col_modal.js';
import { openSidebarActionForm, openSidebarForm } from './sidebar_scripts.js';


// Table selection
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

    document.querySelectorAll('.table-select-btn').forEach(function(button) {
        button.classList.remove('active');
    });
    document.querySelectorAll('.table-select-btn').forEach(function(button) {
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
        const firstTableButton = document.querySelector('.table-select-btn');
        if (firstTableButton) {
            showTable(firstTableButton.textContent.trim());
        }
    }
});

// Pager
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


// Dropdown
document.addEventListener('DOMContentLoaded', function() {
    // Toggle dropdown on click
    document.addEventListener('click', function(e) {
        if (e.target.matches('.dropdown-toggle')) {
            e.preventDefault();
            const content = e.target.nextElementSibling;
            
            // Close all other dropdowns
            document.querySelectorAll('.dropdown-content').forEach(item => {
                if (item !== content) {
                    item.classList.remove('show');
                }
            });
            
            // Toggle current dropdown
            content.classList.toggle('show');
        } else if (!e.target.closest('.dropdown-content')) {
            // Close all dropdowns when clicking outside
            document.querySelectorAll('.dropdown-content').forEach(content => {
                content.classList.remove('show');
            });
        }
    });
});

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
                const infoColModal = new InfoColModal(colName, colIdx, tableName, {});
                infoColModal.open();
            };
            if (!th.querySelector('.table-header-btn')) {
                th.appendChild(infoColButton);
            }
        });
    });
}
document.addEventListener('DOMContentLoaded', function() { addInfoButtons(); });


window.openCustomActionModal = openCustomActionModal;
window.showTable = showTable;
window.openSidebarActionForm = openSidebarActionForm;
window.openSidebarForm = openSidebarForm;
