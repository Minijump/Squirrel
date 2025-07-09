import { SquirrelWidget } from '/static/utils/widgets/widget/widget.js';
import { Input } from '/static/utils/components/input/input.js';

export class SquirrelDictionary extends SquirrelWidget {
    constructor(element) {
        super(element, ['TEXTAREA']);

        this.defaultOptions = {
            create: true,
            remove: true,
            placeholder: {
                key: 'Key',
                value: 'Value'
            }
        };
        this.options = this.parseOptions();
        this.data = this.parseInitialData();
        this.initialize();
    }

    parseInitialData() {
        const value = this.element.value.trim();
        if (!value) return {};
        
        try {
            return JSON.parse(value);
        } catch (error) {
            console.warn('Invalid JSON in textarea, starting with empty object:', error);
            return {};
        }
    }

    initialize() {
        this.createWrapper();
        this.createTable();
        this.loadData();
    }

    createWrapper() {
        this.wrapper = document.createElement('div');
        this.wrapper.className = 'squirrel-dict-widget';
        this.element.parentNode.insertBefore(this.wrapper, this.element);
        this.element.style.display = 'none';
    }

    createTable() {
        this.table = document.createElement('table');
        this.table.className = 'squirrel-dict-table';
        
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
        tfoot.innerHTML = `
            <tr>
                <td colspan="2"></td>
                <td><button type="button" class="btn-add-line" title="Add row">+</button></td>
            </tr>
        `;
        return tfoot;
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
        Object.entries(this.data).forEach(([key, value]) => {
            this.addRow(key, value, true);
        });
    }

    addRow(key = '', value = '', isDefault = false) {
        const row = document.createElement('tr');
        const isKeyReadOnly = isDefault && this.options.remove === false;

        this.createRowElements(row, key, value, isKeyReadOnly);
        this.addRemoveButton(row, isDefault);
        this.table.querySelector('tbody').appendChild(row);

        this.updateTextarea();
    }

    createRowElements(row, key, value, isKeyReadOnly) {
        const keyCell = document.createElement('td');
        const valueCell = document.createElement('td');
        const actionCell = document.createElement('td');

        const keyInput = Input.createInput('text', {
            value: key,
            placeholder: this.options.placeholder.key,
            readonly: isKeyReadOnly
        });

        const valueInput = Input.createInput('text', {
            value: value,
            placeholder: this.options.placeholder.value
        });

        keyCell.appendChild(keyInput);
        valueCell.appendChild(valueInput);

        row.appendChild(keyCell);
        row.appendChild(valueCell);
        row.appendChild(actionCell);
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
        const data = {};
        this.table.querySelectorAll('tbody tr').forEach(row => {
            const inputs = row.querySelectorAll('input');
            const key = inputs[0].value.trim();
            if (key) {
                const value = inputs[1].value;
                data[key] = this.parseValue(value);
            }
        });
        this.element.value = JSON.stringify(data);
        this.element.dispatchEvent(new Event('change'));
    }

    parseValue(value) {
        const trimmedValue = value.trim();
        if (trimmedValue === '') return '';
        
        const numValue = Number(trimmedValue);
        return !isNaN(numValue) && isFinite(numValue) ? numValue : value;
    }
}

// Initialize widgets when DOM is loaded 
// Needs to do it manually for widgets added dynamically (js) after dom is loaded
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('textarea[widget="squirrel-dictionary"]').forEach(elem => {
        new SquirrelDictionary(elem);
    });
});
