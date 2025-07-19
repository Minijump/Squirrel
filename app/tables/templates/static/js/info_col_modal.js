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
                openSidebarActionForm('RenameColumn', this.getColumnInfo(), 'Rename Column');
            };
        }
        
        return header;
    }

    createContent() {
        const content = super.createContent();

        const buttonConfigs = [
            ['.btn-div:not(.numeric-only):not(.string-only)', [
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
            ]],
            ['.btn-div.string-only', [
                {'action': 'ReplaceInCell', 'label': 'Replace in cell'},
                {'action': 'FormatString', 'label': 'String formats'},
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
            openSidebarActionForm(btn.action, this.getColumnInfo(), btn.label);
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
            
            this.componentHtml.querySelectorAll('.string-only').forEach(div => 
                div.style.display = data['is_string'] ? 'flex' : 'none'
            );

            const fields = ['dtype', 'count', 'unique', 'null',
                            'mean', 'std', 'min', '25', '50', '75', 'max', // numeric only
                            'avg_length', 'min_length', 'max_length', 'empty_strings']; // string only   
            fields.forEach(field => {       
                const element = this.componentHtml.querySelector(`#col_${field}`);
                if (element) {
                    const hasValue = data[field] !== undefined;
                    element.style.display = hasValue ? 'inline' : 'none';
                    element.querySelector('span').innerText = hasValue ? this.formatNumber(data[field]) : 'N/A';
                }
            });
            
            // Handle top values
            const topValuesDiv = this.componentHtml.querySelector('#top_values_list');
            if (topValuesDiv && data['top_values']) {
                topValuesDiv.innerHTML = '';
                Object.entries(data['top_values']).forEach(([value, count]) => {
                    const valueDiv = document.createElement('div');
                    valueDiv.className = 'top-value-item';
                    valueDiv.innerHTML = `<span class="value">"${value}"</span>: <span class="count">${count}</span>`;
                    topValuesDiv.appendChild(valueDiv);
                });
                
                // Add fold/unfold feature
                const title = this.componentHtml.querySelector('#top_values_title');
                const values = this.componentHtml.querySelector('#top_values_list');
                const sign = this.componentHtml.querySelector('#fold_sign');
                let isExpanded = true;
                function fold() {
                    isExpanded = !isExpanded;
                    sign.textContent = isExpanded ? '-' : '+';
                    const items = topValuesDiv.querySelectorAll('.top-value-item');
                    items.forEach((item, index) => {
                        item.style.display = (isExpanded || index === 0) ? 'block' : 'none';
                    });
                }
                fold(); // Initially folded
                title.onclick = () => {
                    fold();
                };
                values.onclick = () => {
                    fold();
                }
            }
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
