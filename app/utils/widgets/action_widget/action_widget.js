import { SquirrelWidget } from '/static/utils/widgets/widget/widget.js';

export class SquirrelAction extends SquirrelWidget {
    constructor(element) {
        super(element, ['TEXTAREA']);
        this.options = this.parseOptions();
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
        this.element.addEventListener('blur', () => { setTimeout(() => this.hideSuggestions(), 200);});
    }

    checkForAutocomplete() {
        if (!this.autocompleteData) return;

        const cursorPos = this.element.selectionStart;
        const textBeforeCursor = this.element.value.substring(0, cursorPos);
        
        const tMatch = textBeforeCursor.match(/t\[['"]?(\w*)$/);
        if (tMatch) {
            this.showSuggestions(Object.keys(this.autocompleteData), tMatch[1]);
            return;
        }

        const cMatch = textBeforeCursor.match(/c\[['"]?(\w*)$/);
        if (cMatch) {
            const tableName = this.getTableName(textBeforeCursor);
            const columns = this.autocompleteData[tableName] || [];
            this.showSuggestions(columns, cMatch[1]);
            return;
        }

        this.hideSuggestions();
    }

    getTableName(textBeforeCursor) {
        const afterTableMatch = textBeforeCursor.match(/t\[['"](\w+)['"]\]c\[['"]?(\w*)$/);
        if (afterTableMatch) {
            return afterTableMatch[1];
        }
        // NOT working, input is filled by js after the widget is initialized (In Form class?)
        return document.querySelector('input[name="table_name"]')?.value;
    }

    showSuggestions(items, prefix) {
        this.currentSuggestions = items.filter(item => 
            String(item).toLowerCase().startsWith(prefix.toLowerCase())
        );
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
            if (index === this.selectedIndex) {
                item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            }
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
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('textarea[widget="squirrel-action"]').forEach(elem => {
        new SquirrelAction(elem);
    });
});
