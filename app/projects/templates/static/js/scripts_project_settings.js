class SquirrelDictionary {
    constructor(element) {
        this.textarea = element;
        this.options = JSON.parse(element.getAttribute('options') || '{}');
        this.initialize();
    }

    initialize() {
        // Create wrapper
        this.wrapper = document.createElement('div');
        this.wrapper.className = 'squirrel-dict-widget';
        this.textarea.parentNode.insertBefore(this.wrapper, this.textarea);
        this.textarea.style.display = 'none';
        
        // Create table
        this.table = document.createElement('table');
        this.table.innerHTML = `
            <tbody></tbody>
        `;
        this.wrapper.appendChild(this.table);

        // Add button if creation allowed
        if (this.options.create) {
            const addBtn = document.createElement('button');
            addBtn.textContent = 'Add Entry';
            addBtn.className = 'btn btn-sm btn-primary';
            addBtn.onclick = () => this.addRow();
            this.wrapper.appendChild(addBtn);
        }

        // Load initial data
        this.loadData();
    }

    loadData() {
        const data = JSON.parse(this.textarea.value || '{}');
        Object.entries(data).forEach(([key, value]) => {
            this.addRow(key, value);
        });
    }

    addRow(key = '', value = '') {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><input type="text" class="form-control" value="${key}"></td>
            <td><input type="text" class="form-control" value="${value}"></td>
            <td>
                ${this.options.remove_default !== false ? 
                '<button class="btn btn-sm btn-danger">Remove</button>' : ''}
            </td>
        `;

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