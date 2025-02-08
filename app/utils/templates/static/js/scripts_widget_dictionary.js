class SquirrelDictionary {
    constructor(element) {
        this.textarea = element;
        this.options = JSON.parse(element.getAttribute('options') || '{}');
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
        `;
        this.wrapper.appendChild(this.table);

        if (this.options.create) {
            const addBtn = document.createElement('button');
            addBtn.textContent = 'Add Line';
            addBtn.className = 'btn-add-line';
            addBtn.onclick = (event) => {
                event.preventDefault();
                this.addRow();
            };
            this.wrapper.appendChild(addBtn);
        }

        this.loadData();
    }

    loadData() {
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
        row.innerHTML = `
            <td><input type="text" value="${key}"></td>
            <td><input type="text" value="${value}"></td>
            <td></td>
        `;
        if (this.options.remove_default !== false || !default_row) {
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
                data[key] = inputs[1].value;
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
