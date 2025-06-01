import { AutocompleteForm } from './form.js';

export class Modal {
    constructor(options = {}) {
        this.id = options.id || 'modal-' + Math.random().toString(36).substring(2, 11);
        this.title = options.title || 'Modal';
        this.content = options.content || '';
        this.width = options.width || '500px';
        this.maxHeight = options.maxHeight || '500px';
        this.closable = options.closable || true;
        this.backdrop = options.backdrop || true;
        this.onOpen = options.onOpen || null;
        this.onClose = options.onClose || null;
        this.className = options.className || '';
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
        modalContent.style.width = this.width;
        modalContent.style.maxHeight = this.maxHeight;
        
        const header = document.createElement('div');
        header.className = 'modal-header';
        header.innerHTML = `
            <h3 class="modal-title">${this.title}</h3>
            ${this.closable ? '<a href="javascript:void(0)" class="close-btn">&times;</a>' : ''}
        `;
        
        const content = document.createElement('div');
        content.className = 'modal-body';
        if (typeof this.content === 'string') {
            content.innerHTML = this.content;
        } else if (this.content instanceof HTMLElement) {
            content.appendChild(this.content);
        }
        
        modalContent.appendChild(header);
        modalContent.appendChild(content);
        this.element.appendChild(modalContent);
        document.body.appendChild(this.element);
        
        this.bindEvents();
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
        if (this.isOpen) return;
        
        this.element.style.display = 'flex';
        this.isOpen = true;
        document.addEventListener('keydown', this.escapeHandler);
        
        const firstInput = this.element.querySelector('input, textarea, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
        
        if (this.onOpen) {
            this.onOpen(this);
        }
    }

    close() {
        if (!this.isOpen) return;
        
        this.element.style.display = 'none';
        this.isOpen = false;
        document.removeEventListener('keydown', this.escapeHandler);
        
        if (this.onClose) {
            this.onClose(this);
        }
    }

    destroy() {
        this.close();
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
    }
}

export class FormModal extends Modal {
    constructor(options = {}) {
        const formOptions = {
            'id': options.formId || {},
            'inputs': options.inputs || {},
            'submitRoute': options.submitRoute || '',
            'cancelButtonOnClick': options.cancelButtonOnClick || null,
            'data': options.data || {},
        }
        const content = new AutocompleteForm(formOptions);
        options.content = content.formCode;
        super(options);
    }
}
