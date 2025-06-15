import { AutocompleteForm } from './form.js';

export class Modal {
    constructor(options = {}) {
        this.id = options.id || 'modal-' + Math.random().toString(36).substring(2, 11);
        this.title = options.title || 'Modal';
        this.bodyContent = options.content || '';
        this.modalHtml = null;
        this.isOpen = false;
        this.create();
    }

    create() {
        this.modalHtml = document.createElement('div');
        this.modalHtml.className = `modal`;
        this.modalHtml.id = this.id;
        
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        
        const header = this.createHeader();
        const content = this.createContent();
        
        modalContent.appendChild(header);
        modalContent.appendChild(content);
        this.modalHtml.appendChild(modalContent);
        document.body.appendChild(this.modalHtml); 
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
        if (typeof this.bodyContent === 'string') content.innerHTML = this.bodyContent;
        else if (this.bodyContent instanceof HTMLElement) content.appendChild(this.bodyContent);
        else if (this.bodyContent instanceof AutocompleteForm) content.appendChild(this.bodyContent.formHTML);
        else console.warn('Modal body expects string, HTMLElement or AutocompleteForm');
        return content;
    }

    bindEvents() {
        const closeBtn = this.modalHtml.querySelector('.close-btn');
        if (closeBtn) closeBtn.addEventListener('click', () => this.close());
        
        this.modalHtml.addEventListener('click', (e) => {
            if (e.target === this.modalHtml) this.close();
        });
        this.escapeHandler = (e) => {
            if (e.key === 'Escape' && this.isOpen) this.close();
        };
    }

    open() {
        if (this.isOpen) return;

        this.fillData();
        this.modalHtml.style.display = 'flex';
        this.isOpen = true;
        document.addEventListener('keydown', this.escapeHandler);
        this.defaultFocus();  
    }

    fillData() {
        return;
    }

    defaultFocus() {
        Array.from(document.querySelectorAll('input, textarea'))
            .find(input => input.offsetParent !== null) // find 1st visible element
            ?.focus();
    }

    close() {
        if (!this.isOpen) return;

        this.modalHtml.style.display = 'none';
        this.isOpen = false;
        document.removeEventListener('keydown', this.escapeHandler);
        this.destroy();
    }

    destroy() {
        this.modalHtml?.remove();
        this.modalHtml = null;
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
        options.content = new AutocompleteForm(formOptions);
        super(options);
    }
}
