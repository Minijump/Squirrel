import { SquirrelWidget } from '/static/utils/widgets/widget/widget.js';

export class SquirrelAction extends SquirrelWidget {
    constructor(element) {
        super(element, ['TEXTAREA']);
        this.autocompleteData = null;
        this.currentSuggestions = [];
        this.selectedIndex = -1;
        this.initialize();
    }

    async initialize() {
        this.createWrapper();
        await this.loadAutocompleteData();
        this.bindEvents();
    }

    createWrapper() {
        this.wrapper = document.createElement('div');
        this.wrapper.className = 'squirrel-action-widget';
        
        this.suggestionBox = document.createElement('div');
        this.suggestionBox.className = 'action-suggestion-box';
        this.suggestionBox.style.display = 'none';

        this.element.parentNode.insertBefore(this.wrapper, this.element);
        this.wrapper.appendChild(this.element);
        this.wrapper.appendChild(this.suggestionBox);
        this.element.style.display = 'block';
    }

    async loadAutocompleteData() {
        const projectDir = new URLSearchParams(window.location.search).get('project_dir');
        if (!projectDir) return;

        try {
            const response = await fetch(`/tables/autocomplete_data/?project_dir=${projectDir}`);
            this.autocompleteData = await response.json();
        } catch (error) {
            console.warn('Could not load autocomplete data:', error);
        }
    }

    bindEvents() {
        this.element.addEventListener('input', () => this.checkForAutocomplete());
        this.element.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.element.addEventListener('blur', () => {
            setTimeout(() => this.hideSuggestions(), 200);
        });
    }

    checkForAutocomplete() {
        if (!this.autocompleteData) return;

        const cursorPos = this.element.selectionStart;
        const textBeforeCursor = this.element.value.substring(0, cursorPos);
        
        const tMatch = textBeforeCursor.match(/t\[['"]?(\w*)$/);
        if (tMatch) {
            const prefix = tMatch[1];
            this.showTableSuggestions(prefix);
            return;
        }

        const cMatch = textBeforeCursor.match(/c\[['"]?(\w*)$/);
        if (cMatch) {
            const prefix = cMatch[1];
            const tableName = this.getCurrentTableName();
            if (tableName) {
                this.showColumnSuggestions(tableName, prefix);
                return;
            }
        }

        const afterTableMatch = textBeforeCursor.match(/t\[['"](\w+)['"]\]c\[['"]?(\w*)$/);
        if (afterTableMatch) {
            const tableName = afterTableMatch[1];
            const prefix = afterTableMatch[2];
            this.showColumnSuggestions(tableName, prefix);
            return;
        }

        this.hideSuggestions();
    }

    getCurrentTableName() {
        const tableNameInput = document.querySelector('input[name="table_name"]');
        const tableName = tableNameInput ? tableNameInput.value : null;
        console.log('Current table name:', tableName);
        return tableName;
    }

    showTableSuggestions(prefix) {
        const tables = Object.keys(this.autocompleteData);
        this.currentSuggestions = tables.filter(t => t.toLowerCase().startsWith(prefix.toLowerCase()));
        console.log('Table suggestions for prefix', prefix, ':', this.currentSuggestions);
        this.renderSuggestions();
    }

    showColumnSuggestions(tableName, prefix) {
        console.log('Looking for columns in table:', tableName, 'with prefix:', prefix);
        const columns = this.autocompleteData[tableName];
        if (!columns) {
            console.warn('No columns found for table:', tableName);
            this.hideSuggestions();
            return;
        }
        this.currentSuggestions = columns.filter(c => String(c).toLowerCase().startsWith(prefix.toLowerCase()));
        console.log('Column suggestions:', this.currentSuggestions);
        this.renderSuggestions();
    }

    renderSuggestions() {
        if (this.currentSuggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        this.selectedIndex = 0;
        this.suggestionBox.innerHTML = this.currentSuggestions
            .map((suggestion, index) => 
                `<div class="suggestion-item${index === 0 ? ' selected' : ''}" data-index="${index}">${suggestion}</div>`
            )
            .join('');

        this.suggestionBox.style.display = 'block';
        
        const rect = this.element.getBoundingClientRect();
        const wrapperRect = this.wrapper.getBoundingClientRect();
        this.suggestionBox.style.left = `${rect.left - wrapperRect.left}px`;
        this.suggestionBox.style.top = `${rect.bottom - wrapperRect.top + 2}px`;

        this.suggestionBox.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                this.insertSuggestion(item.textContent);
            });
        });
    }

    hideSuggestions() {
        this.suggestionBox.style.display = 'none';
        this.currentSuggestions = [];
        this.selectedIndex = -1;
    }

    handleKeydown(e) {
        if (this.suggestionBox.style.display !== 'block') return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.selectedIndex = Math.min(this.selectedIndex + 1, this.currentSuggestions.length - 1);
            this.updateSelectedSuggestion();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
            this.updateSelectedSuggestion();
        } else if (e.key === 'Enter' || e.key === 'Tab') {
            if (this.selectedIndex >= 0) {
                e.preventDefault();
                this.insertSuggestion(this.currentSuggestions[this.selectedIndex]);
            }
        } else if (e.key === 'Escape') {
            this.hideSuggestions();
        }
    }

    updateSelectedSuggestion() {
        this.suggestionBox.querySelectorAll('.suggestion-item').forEach((item, index) => {
            item.classList.toggle('selected', index === this.selectedIndex);
        });
    }

    insertSuggestion(suggestion) {
        const cursorPos = this.element.selectionStart;
        const text = this.element.value;
        const textBeforeCursor = text.substring(0, cursorPos);
        
        const match = textBeforeCursor.match(/(['"]?)(\w*)$/);
        if (match) {
            const hasQuote = match[1];
            const wordStart = textBeforeCursor.length - match[2].length - (hasQuote ? 1 : 0);
            const newText = text.substring(0, wordStart) + (hasQuote || "'") + suggestion + "']" + text.substring(cursorPos);
            this.element.value = newText;
            const newCursorPos = wordStart + suggestion.length + 3;
            this.element.selectionStart = this.element.selectionEnd = newCursorPos;
        }

        this.hideSuggestions();
        this.element.focus();
    }

    getCursorCoordinates() {
        const textBeforeCursor = this.element.value.substring(0, this.element.selectionStart);
        const dummy = document.createElement('div');
        const computedStyle = window.getComputedStyle(this.element);
        
        dummy.style.position = 'absolute';
        dummy.style.visibility = 'hidden';
        dummy.style.whiteSpace = 'pre-wrap';
        dummy.style.font = computedStyle.font;
        dummy.style.padding = computedStyle.padding;
        dummy.style.border = computedStyle.border;
        dummy.style.width = computedStyle.width;
        dummy.textContent = textBeforeCursor;
        
        const span = document.createElement('span');
        span.textContent = '|';
        dummy.appendChild(span);
        document.body.appendChild(dummy);
        
        const rect = this.element.getBoundingClientRect();
        const spanRect = span.getBoundingClientRect();
        const coordinates = {
            left: spanRect.left - rect.left,
            top: spanRect.top - rect.top
        };
        
        document.body.removeChild(dummy);
        return coordinates;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('textarea[widget="squirrel-action"]').forEach(elem => {
        new SquirrelAction(elem);
    });
});
