import { SquirrelWidget } from '/static/utils/widgets/widget/widget.js';
import { Input } from '/static/utils/components/input/input.js';

export class SquirrelList extends SquirrelWidget {
    constructor(element) {
        super(element, ['TEXTAREA']);

        this.defaultOptions = {
            create: true,
            remove: true,
            placeholder: 'Value'
        };
        this.options = this.parseOptions();
        this.data = this.parseInitialData();
        this.initialize();
    }

    parseInitialData() {
        const value = this.element.value.trim();
        if (!value) return [];
        
        try {
            return JSON.parse(value);
        } catch (error) {
            console.warn('Invalid JSON in textarea, starting with empty array:', error);
            return [];
        }
    }

    initialize() {
        this.createWrapper();
        this.createTable();
        this.loadData();
    }

    createWrapper() {
        this.wrapper = document.createElement('div');
        this.wrapper.className = 'squirrel-list-widget';
        this.element.parentNode.insertBefore(this.wrapper, this.element);
        this.element.style.display = 'none';
    }

    createTable() {
        this.table = document.createElement('table');
        this.table.className = 'squirrel-list-table';
        
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
                <td></td>
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
        this.data.forEach((value) => {
            this.addRow(value, true);
        });
    }

    addRow(value = '', isDefault = false) {
        const row = document.createElement('tr');

        this.createRowElements(row, value);
        this.addRemoveButton(row, isDefault);
        this.table.querySelector('tbody').appendChild(row);

        this.updateTextarea();
    }

    createRowElements(row, value) {
        const valueCell = document.createElement('td');
        const actionCell = document.createElement('td');

        const valueInput = Input.createInput('text', {
            value: value,
            placeholder: this.options.placeholder
        });

        valueCell.appendChild(valueInput);

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
        const data = [];
        this.table.querySelectorAll('tbody tr').forEach(row => {
            const input = row.querySelector('input');
            const value = input.value.trim();
            if (value) {
                data.push(value);
            }
        });
        this.element.value = JSON.stringify(data);
        this.element.dispatchEvent(new Event('change'));
    }
}

// Initialize widgets when DOM is loaded 
// Needs to do it manually for widgets added dynamically (js) after dom is loaded
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('textarea[widget="squirrel-list"]').forEach(elem => {
        new SquirrelList(elem);
    });
});
