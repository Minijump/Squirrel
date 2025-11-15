import { SquirrelWidget } from '/static/utils/widgets/widget/widget.js';

export class TableInputWidget extends SquirrelWidget {
    constructor(element, defaultOptions) {
        super(element, ['TEXTAREA']);
        this.defaultOptions = defaultOptions;
        this.options = this.parseOptions();
        this.data = this.parseInitialData();
        this.initialize();
    }

    getDefaultValue() {
        throw new Error('getDefaultValue must be implemented by subclass');
    }

    parseInitialData() {
        const value = this.element.value.trim();
        if (!value) return this.getDefaultValue();
        
        try {
            return JSON.parse(value);
        } catch (error) {
            console.warn('Invalid JSON in textarea, starting with default value:', error);
            return this.getDefaultValue();
        }
    }

    initialize() {
        this.createWrapper();
        this.createTable();
        this.loadData();
    }

    createWrapper() {
        this.wrapper = document.createElement('div');
        this.wrapper.className = this.getWrapperClass();
        this.element.parentNode.insertBefore(this.wrapper, this.element);
        this.element.style.display = 'none';
    }

    getWrapperClass() {
        throw new Error('getWrapperClass must be implemented by subclass');
    }

    createTable() {
        this.table = document.createElement('table');
        
        const tbody = document.createElement('tbody');
        this.table.appendChild(tbody);
        
        if (this.options.create) {
            const footer = this.createTableFooter();
            this.table.appendChild(footer);
        }
        
        this.wrapper.appendChild(this.table);
        this.bindFooterEvent();
    }

    createTableFooter() {
        const tfoot = document.createElement('tfoot');
        const colspan = this.getColumnCount();
        tfoot.innerHTML = `
            <tr>
                <td colspan="${colspan}" style="text-align: right;">
                    <button type="button" class="btn-add-line" title="Add row">+</button>
                </td>
            </tr>
        `;
        return tfoot;
    }

    getColumnCount() {
        throw new Error('getColumnCount must be implemented by subclass');
    }

    bindFooterEvent() {
        if (this.options.create) {
            const addBtn = this.table.querySelector('.btn-add-line');
            if (addBtn) {
                addBtn.addEventListener('click', (event) => {
                    event.preventDefault();
                    this.addRow();
                });
            }
        }
    }

    loadData() {
        throw new Error('loadData must be implemented by subclass');
    }

    addRow() {
        const row = document.createElement('tr');
        const args = Array.from(arguments);
        const isDefault = args[args.length - 1];

        this.createRowElements(row, ...args);
        this.addRemoveButton(row, isDefault);
        this.table.querySelector('tbody').appendChild(row);

        this.updateTextarea();
    }

    createRowElements(row) {
        throw new Error('createRowElements must be implemented by subclass');
    }

    addRemoveButton(row, isDefault) {
        if (this.options.remove !== false || !isDefault) {
            const actionCell = row.querySelector('td:last-child');
            actionCell.innerHTML = '<button type="button" class="btn-remove-line" title="Remove row"><i class="fas fa-times"></i></button>';
        }
        this.bindRemoveButtonEvent(row);
    }

    bindRemoveButtonEvent(row) {
        const removeBtn = row.querySelector('.btn-remove-line');
        if (removeBtn) {
            removeBtn.addEventListener('click', () => {
                row.remove();
                this.updateTextarea();
            });
        }

        row.querySelectorAll('input').forEach(input => {
            input.addEventListener('change', () => this.updateTextarea());
            input.addEventListener('input', () => this.updateTextarea());
        });
    }

    updateTextarea() {
        throw new Error('updateTextarea must be implemented by subclass');
    }

    parseValue(value) {
        const trimmedValue = value.trim();
        if (trimmedValue === '') return '';
        
        const numValue = Number(trimmedValue);
        return !isNaN(numValue) && isFinite(numValue) ? numValue : value;
    }
}
