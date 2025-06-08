import { Modal } from '/static/base/js/components/modal.js';

export class InfoColModal extends Modal {
    constructor(colName, colIdx, tableName, options = {}) {
        options['content'] = document.getElementById('infoColModalBody').innerHTML;
        options['id'] = 'InfoColModal';
        super(options);
        this.colName = colName;
        this.colIdx = colIdx;
        this.tableName = tableName;
    }

    createHeader() {
        const header = document.createElement('div');
        const headerTemplate = document.getElementById('headerInfoColModal');
        header.innerHTML = headerTemplate.innerHTML
        header.className = headerTemplate.className;
        header.style.cssText = headerTemplate.style.cssText;

        const editBtn = header.querySelector('#editBtn');
        if (editBtn) {
            const modalInstance = this;
            editBtn.onclick = function() {
                modalInstance.close();
                openSidebarActionForm('RenameColumn', modalInstance.getColumnInfo());
            };
        }
        return header;
    }

    createContent() {
        const content = super.createContent();

        const generalBtnDiv = content.querySelector('.btn-div:not(.numeric-only)');
        const numericBtnDiv = content.querySelector('.btn-div.numeric-only');
        
        const generalButtons = [
            {'action': 'HandleMissingValues', 'label': 'Missing vals.'},
            {'action': 'ReplaceVals', 'label': 'Replace vals.'},
            {'action': 'ChangeType', 'label': 'Change type'},
            {'action': 'SortColumn', 'label': 'Sort'},
            {'action': 'ApplyFunction', 'label': 'Apply Function'}
        ];
        const numericButtons = [
            {'action': 'NormalizeColumn', 'label': 'Normalize'},
            {'action': 'RemoveUnderOver', 'label': 'Remove under/over'},
            {'action': 'CutValues', 'label': 'Cut'},
            {'action': 'NLargest', 'label': 'Keep N largest'},
            {'action': 'NSmallest', 'label': 'Keep N smallest'},
            {'action': 'ColDiff', 'label': 'Diff'}
        ];

        if (generalBtnDiv) {
            generalButtons.forEach(btn => {
                const button = this.createActionButton(btn);
                generalBtnDiv.appendChild(button);
            });
        }
        if (numericBtnDiv) {
            numericButtons.forEach(btn => {
                const button = this.createActionButton(btn);
                numericBtnDiv.appendChild(button);
            });
        }

        return content;
    }

    createActionButton(btn) {
        const button = document.createElement('button');
        button.className = 'table-action-btn';
        button.textContent = btn.label;
        const modalInstance = this;
        button.onclick = function() {
            modalInstance.close();
            openSidebarActionForm(btn.action, modalInstance.getColumnInfo());
        };
        return button;
    }

    open() {
        this.fillData();
        super.open();
    }

    async fillData() {
        // Add column name
        const modalTitle = this.element.querySelector('#modalTitle');
        if (modalTitle) {
            modalTitle.innerText = this.colName;
        }

        // Fill 'delete column' form
        this.element.querySelector('#col_name').innerText = this.colName;
        this.element.querySelector('#col_idx').innerText = this.colIdx;
        this.element.querySelector('#table_name').innerText = this.tableName;
        const projectDir = new URLSearchParams(window.location.search).get('project_dir')
        
        // Fill column information
        try {
            const response = await fetch(`/tables/column_infos/?project_dir=${projectDir}&table=${this.tableName}&column_name=${this.colName}&column_idx=${this.colIdx}`);
            if (!response.ok) {
                throw new Error(`Error in response${response.status}`);
            }
            const data = await response.json();

            const fields = ['dtype', 'count', 'unique', 'null',
                            'is_numeric', 'mean', 'std', 'min', '25', '50', '75', 'max'];
            fields.forEach(field => {
                if (field === 'is_numeric') {
                    const numericDivs = this.element.querySelectorAll('.numeric-only');
                    numericDivs.forEach(div => {
                        div.style.display = data[field] ? 'flex' : 'none';
                    });
                    return;
                }

                const element = this.element.querySelector(`#col_${field}`);
                if (!element) {
                    return;
                }
                if (data[field] !== undefined) {
                    element.style.display = 'inline';
                    element.querySelector('span').innerText = `${this.formatNumber(data[field])}`;
                } else {
                    element.style.display = 'none';
                }
            });
        } catch (error) {
            console.error('Error:', error);
            const errorElement = this.element.querySelector('#error_infos_computation');
            if (errorElement) {
                errorElement.innerHTML = `Error computing informations: ${error.message}`;
            }
        }
    }

    formatNumber(num) {
        if (typeof num === 'string' && !isNaN(num)) {
            num = parseFloat(num);
        }
        return (typeof num === 'number' && num % 1 !== 0) ? num.toFixed(2) : num;
    }

    getColumnInfo(additionalData = {}) {
        let infos = {
            'table_name': this.tableName,
            'col_name': this.colName,
            'col_idx': this.colIdx,
        };
        if (additionalData) {
            infos = {...infos, ...additionalData};
        };
        return infos;
    }
}
