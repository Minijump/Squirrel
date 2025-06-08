import { AutocompleteForm } from './form.js';

export class Modal {
    constructor(options = {}) {
        this.id = options.id || 'modal-' + Math.random().toString(36).substring(2, 11);
        this.title = options.title || 'Modal';
        this.className = options.className || '';
        this.backdrop = options.backdrop || true;
        this.bodyContent = options.content || '';
        this.element = null;
        this.isOpen = false;
        this.create();
    }

    create() {
        this.element = document.createElement('div');
        this.element.className = `modal ${this.className}`;
        this.element.id = this.id;
        
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        
        const header = this.createHeader();
        const content = this.createContent();
        
        modalContent.appendChild(header);
        modalContent.appendChild(content);
        this.element.appendChild(modalContent);
        document.body.appendChild(this.element); 
        this.bindEvents();
    }

    createHeader() {
        const header = document.createElement('div');
        header.className = 'modal-header';
        header.innerHTML = `
            <h3 class="modal-title">${this.title}</h3>
            <a href="javascript:void(0)" class="close-btn">&times;</a>
        `;
        return header;
    }

    createContent() {
        const content = document.createElement('div');
        content.className = 'modal-body';
        if (typeof this.bodyContent === 'string') {
            content.innerHTML = this.bodyContent;
        } else if (this.bodyContent instanceof HTMLElement) {
            content.appendChild(this.bodyContent);
        }
        return content;
    }

    bindEvents() {
        const closeBtn = this.element.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }
        
        if (this.backdrop) {
            this.element.addEventListener('click', (e) => {
                if (e.target === this.element) {
                    this.close();
                }
            });
        }
        
        this.escapeHandler = (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        };
    }

    open() {
        this.fillData();
        if (this.isOpen) return;
        
        this.element.style.display = 'flex';
        this.isOpen = true;
        document.addEventListener('keydown', this.escapeHandler);
        
        this.defaultFocus();
    }

    fillData() {
        return;
    }

    defaultFocus() {
        const inputs = document.querySelectorAll('input, textarea');
        for (const input of inputs) {
            if (input.offsetParent !== null) { // Check if the element is visible
                input.focus();
                break;
            }
        }
    }

    close() {
        if (!this.isOpen) return;
        
        this.element.style.display = 'none';
        this.isOpen = false;
        document.removeEventListener('keydown', this.escapeHandler);
        this.destroy();
    }

    destroy() {
        if (this.element) {
            this.element.remove();
            this.element = null;
        }
    }
}

export class FormModal extends Modal {
    constructor(options = {}) {
        const formOptions = {
            'id': options.formId || {},
            'inputs': options.formInputs || {},
            'submitRoute': options.formSubmitRoute || '',
            'data': options.formData || {},
        }
        const content = new AutocompleteForm(formOptions);
        options.content = content.formCode;
        super(options);
    }
}
