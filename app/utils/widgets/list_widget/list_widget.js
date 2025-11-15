import { TableInputWidget } from '/static/utils/widgets/table_input_widget/table_input_widget.js';
import { Input } from '/static/utils/components/input/input.js';

export class SquirrelList extends TableInputWidget {
    constructor(element) {
        super(element, {
            create: true,
            remove: true,
            placeholder: 'Value'
        });
    }

    getDefaultValue() {
        return [];
    }

    getWrapperClass() {
        return 'squirrel-list-widget squirrel-table-input-widget';
    }

    getColumnCount() {
        return 2;
    }

    loadData() {
        this.data.forEach((value) => {
            this.addRow(value, true);
        });
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

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('textarea[widget="squirrel-list"]').forEach(elem => {
        new SquirrelList(elem);
    });
});
