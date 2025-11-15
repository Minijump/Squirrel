import { TableInputWidget } from '/static/utils/widgets/table_input_widget/table_input_widget.js';
import { Input } from '/static/utils/components/input/input.js';

export class SquirrelDictionary extends TableInputWidget {
    constructor(element) {
        super(element, {
            create: true,
            remove: true,
            placeholder: {
                key: 'Key',
                value: 'Value'
            }
        });
    }

    getDefaultValue() {
        return {};
    }

    getWrapperClass() {
        return 'squirrel-dict-widget squirrel-table-input-widget';
    }

    getColumnCount() {
        return 3;
    }

    loadData() {
        Object.entries(this.data).forEach(([key, value]) => {
            this.addRow(key, value, true);
        });
    }

    createRowElements(row, key, value, isDefault) {
        const isKeyReadOnly = isDefault && this.options.remove === false;
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
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('textarea[widget="squirrel-dictionary"]').forEach(elem => {
        new SquirrelDictionary(elem);
    });
});
