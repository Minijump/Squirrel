import { Modal } from '/static/utils/components/modal/modal.js';
import { openSidebarActionForm } from './sidebar_scripts.js';

export class InfoColModal extends Modal {
    constructor(colName, colIdx, tableName, options = {}) {
        options['content'] = document.getElementById('infoColModalBody').innerHTML;
        options['id'] = 'InfoColModal';
        super(options);
        Object.assign(this, {colName, colIdx, tableName});
    }

    createHeader() {
        const headerTemplate = document.getElementById('headerInfoColModal');
        const header = headerTemplate.cloneNode(true)
        header.removeAttribute('id');
        
        const editBtn = header.querySelector('#editBtn');
        if (editBtn) {
            editBtn.onclick = () => {
                this.close();
                openSidebarActionForm('RenameColumn', this.getColumnInfo());
            };
        }
        
        return header;
    }

    createContent() {
        const content = super.createContent();

        const buttonConfigs = [
            ['.btn-div:not(.numeric-only)', [
                {'action': 'HandleMissingValues', 'label': 'Missing vals.'},
                {'action': 'ReplaceVals', 'label': 'Replace vals.'},
                {'action': 'ChangeType', 'label': 'Change type'},
                {'action': 'SortColumn', 'label': 'Sort'},
                {'action': 'ApplyFunction', 'label': 'Apply Function'}
            ]],
            ['.btn-div.numeric-only', [
                {'action': 'NormalizeColumn', 'label': 'Normalize'},
                {'action': 'RemoveUnderOver', 'label': 'Remove under/over'},
                {'action': 'CutValues', 'label': 'Cut'},
                {'action': 'NLargest', 'label': 'Keep N largest'},
                {'action': 'NSmallest', 'label': 'Keep N smallest'},
                {'action': 'ColDiff', 'label': 'Diff'},
                {'action': 'MathOperations', 'label': 'Math operations'},
            ]]
        ];

        buttonConfigs.forEach(([selector, buttons]) => {
            const div = content.querySelector(selector);
            if (div) {
                buttons.forEach(btn => div.appendChild(this.createActionButton(btn)));
            }
        });

        return content;
    }

    createActionButton(btn) {
        const button = document.createElement('button');
        button.className = 'table-action-btn';
        button.textContent = btn.label;
        button.onclick = () => {
            this.close();
            openSidebarActionForm(btn.action, this.getColumnInfo());
        };
        return button;
    }

    async fillData() {
        this.componentHtml.querySelector('#modalTitle').innerText = this.colName;
        this.componentHtml.querySelector('#col_name').value = this.colName;
        this.componentHtml.querySelector('#col_idx').value = this.colIdx;
        this.componentHtml.querySelector('#table_name').value = this.tableName;
        this.componentHtml.querySelector('#project_dir').value = this.projectDir;
                
        try {
            const response = await fetch(`/tables/column_infos/?project_dir=${this.projectDir}&table=${this.tableName}&column_name=${this.colName}&column_idx=${this.colIdx}`);
            if (!response.ok) throw new Error(`Error in response ${response.status}`);
            const data = await response.json();

            this.componentHtml.querySelectorAll('.numeric-only').forEach(div => 
                div.style.display = data['is_numeric'] ? 'flex' : 'none'
            );

            const fields = ['dtype', 'count', 'unique', 'null',
                            'mean', 'std', 'min', '25', '50', '75', 'max'];    
            fields.forEach(field => {       
                const element = this.componentHtml.querySelector(`#col_${field}`);
                if (element) {
                    const hasValue = data[field] !== undefined;
                    element.style.display = hasValue ? 'inline' : 'none';
                    element.querySelector('span').innerText = hasValue ? this.formatNumber(data[field]) : 'N/A';
                }
            });
        } catch (error) {
            this.componentHtml.querySelector('#error_infos_computation').innerHTML = `Error computing informations: ${error.message}`;
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
