class SquirrelDictionary {
    constructor(element) {
        this.textarea = element;
        const defaultOptions = {
            create: true,
            remove: true
        };
        const userOptions = element.getAttribute('options');
        this.options = userOptions ? { ...defaultOptions, ...JSON.parse(userOptions) } : defaultOptions;
        this.initialize();
    }

    initialize() {
        this.wrapper = document.createElement('div');
        this.wrapper.className = 'squirrel-dict-widget';
        this.textarea.parentNode.insertBefore(this.wrapper, this.textarea);
        this.textarea.style.display = 'none';
        
        this.table = document.createElement('table');
        this.table.innerHTML = `
            <tbody></tbody>
            ${this.options.create ? '<tfoot><tr><td></td><td></td><td><button type="button" class="btn-add-line">+</button></td></tr></tfoot>' : ''}
        `;
        this.wrapper.appendChild(this.table);

        if (this.options.create) {
            const addBtn = this.table.querySelector('.btn-add-line');
            addBtn.onclick = (event) => {
                event.preventDefault();
                this.addRow();
            };
        }

        this.loadData();
    }

    loadData() {
        if (!this.textarea.value.trim()) {
            return;
        }
        const data = JSON.parse(this.textarea.value || '{}');
        Object.entries(data).forEach(([key, value]) => {
            this.addDefaultRow(key, value);
        });
    }

    addDefaultRow(key = '', value = '') {
        this.addRow(key, value, true);
    }

    addRow(key = '', value = '', default_row = false) {
        const row = document.createElement('tr');
        const isKeyReadOnly = default_row && this.options.remove === false;

        row.innerHTML = `
            <td><input type="text" value="${key}" ${isKeyReadOnly ? 'readonly' : ''}></td>
            <td><input type="text" value="${value}"></td>
            <td></td>
        `;
        if (this.options.remove !== false || !default_row) {
            row.querySelector('td:last-child').innerHTML = '<button class="btn-remove-line">X</button>';
        }
            

        const removeBtn = row.querySelector('button');
        if (removeBtn) {
            removeBtn.onclick = () => {
                row.remove();
                this.updateTextarea();
            };
        }

        row.querySelectorAll('input').forEach(input => {
            input.onchange = () => this.updateTextarea();
        });

        this.table.querySelector('tbody').appendChild(row);
        this.updateTextarea();
    }

    updateTextarea() {
        const data = {};
        this.table.querySelectorAll('tbody tr').forEach(row => {
            const inputs = row.querySelectorAll('input');
            const key = inputs[0].value.trim();
            if (key) {
                const value = inputs[1].value;
                const numValue = Number(value);
                data[key] = !isNaN(numValue) && value.trim() !== '' ? numValue : value;
            }
        });
        this.textarea.value = JSON.stringify(data);
    }
}

// Initialize widgets when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('textarea[widget="squirrel-dictionary"]').forEach(elem => {
        new SquirrelDictionary(elem);
    });
});
