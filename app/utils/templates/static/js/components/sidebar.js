import { Form } from './form.js';

export class Sidebar {
    constructor(options = {}) {
        this.id = options.id || 'sidebar-' + Math.random().toString(36).substring(2, 11);
        this.title = options.title || 'Sidebar';
        this.bodyContent = options.content || '';
        this.width = options.width || '320px';
        this.position = options.position || 'right';
        this.hasOverlay = options.hasOverlay !== false;
        this.overlayId = options.overlayId || 'sidebar-overlay';
        this.sidebarHtml = null;
        this.overlayHtml = null;
        this.isOpen = false;
        this.create();
    }

    create() {
        this.sidebarHtml = Object.assign(document.createElement('div'), {
            className: `${this.position}-sidebar`,
            id: this.id
        });
        this.sidebarHtml.innerHTML = `<a href="javascript:void(0)" class="close-btn">&times;</a>`;
        this.sidebarHtml.appendChild(this.createContent());
        
        if (this.hasOverlay) this.overlayHtml = this.getOrCreateOverlay();
        
        document.body.appendChild(this.sidebarHtml);
        this.bindEvents();
    }

    createContent() {
        const content = document.createElement('div');
        if (typeof this.bodyContent === 'string') content.innerHTML = this.bodyContent;
        else if (this.bodyContent instanceof HTMLElement) content.appendChild(this.bodyContent);
        else if (this.bodyContent instanceof Form) content.appendChild(this.bodyContent.formHTML);
        else console.warn('Modal body expects string, HTMLElement or Form');
        return content;
    }

    getOrCreateOverlay() {
        let overlay = document.getElementById(this.overlayId);
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = this.overlayId;
            overlay.className = 'sidebar-overlay';
            overlay.style.display = 'none';
            document.body.appendChild(overlay);
        }
        return overlay;
    }

    bindEvents() {
        const closeBtn = this.sidebarHtml.querySelector('.close-btn');
        if (closeBtn) closeBtn.addEventListener('click', () => this.close());
        
        if (this.hasOverlay && this.overlayHtml) {
            this.overlayHtml.addEventListener('click', () => this.close());
        }
        
        this.escapeHandler = (e) => {
            if (e.key === 'Escape' && this.isOpen) this.close();
        };
    }

    open() {
        if (this.isOpen) return;

        this.fillData();
        this.sidebarHtml.style.width = this.width;
        
        if (this.hasOverlay && this.overlayHtml) {
            this.overlayHtml.style.display = 'block';
        }
        
        this.isOpen = true;
        document.addEventListener('keydown', this.escapeHandler);
        this.defaultFocus();
    }

    fillData() {
        return;
    }

    defaultFocus() {
        const sidebar = this.sidebarHtml;
        Array.from(sidebar.querySelectorAll('input, textarea, select'))
            .find(input => input.offsetParent !== null && !input.disabled && input.type !== 'hidden')
            ?.focus();
    }

    close() {
        if (!this.isOpen) return;

        this.sidebarHtml.style.width = '0';
        
        if (this.hasOverlay && this.overlayHtml) {
            this.overlayHtml.style.display = 'none';
        }
        
        this.isOpen = false;
        document.removeEventListener('keydown', this.escapeHandler);
        this.destroy();
    }

    destroy() {
        this.sidebarHtml?.remove();
        this.sidebarHtml = null;
    }
}

export class FormSidebar extends Sidebar {
    constructor(options = {}) {
        const formOptions = {
            'id': options.formId || 'form-' + Math.random().toString(36).substring(2, 11),
            'inputs': options.formInputs || {},
            'submitRoute': options.formSubmitRoute || '',
            'data': options.formData || {},
        }
        options.content = new Form(formOptions);
        super(options);
        this.form = options.content;
    }

    completeInputs(data = {}) {
        if (this.form && this.form.completeInputs) {
            const form = this.sidebarHtml.querySelector('form');
            this.form.completeInputs(form, data);
        }
    }
}
