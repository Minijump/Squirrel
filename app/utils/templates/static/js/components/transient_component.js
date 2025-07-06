import { Form } from './form.js';


export class TransientComponent {
    constructor(options = {}) {
        this.bodyContent = options.content || '';
        this.isOpen = false;
        this.componentHtml = null;
        this.hasOverlay = options.hasOverlay !== false;
        this.overlayId = options.overlayId || 'transiant-overlay';
        this.overlayHtml = null;
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
        const closeBtn = this.componentHtml.querySelector('.close-btn');
        if (closeBtn) closeBtn.addEventListener('click', () => this.close());
        
        if (this.hasOverlay && this.overlayHtml) this.overlayHtml.addEventListener('click', () => this.close());
        
        this.escapeHandler = (e) => {
            if (e.key === 'Escape' && this.isOpen) this.close();
        };
    }

    open() {
        if (this.isOpen) return;

        this.fillData();
        this.componentOpen();
        if (this.hasOverlay && this.overlayHtml) this.overlayHtml.style.display = 'block';
        
        this.isOpen = true;
        document.addEventListener('keydown', this.escapeHandler);
        this.defaultFocus();
        this.triggerAllOnchangeVisibility();
    }

    componentOpen() {
        return;
    }

    defaultFocus() {
        Array.from(this.componentHtml.querySelectorAll('input, textarea, select'))
            .find(input => input.offsetParent !== null && !input.disabled && input.type !== 'hidden')
            ?.focus();
    }

    triggerAllOnchangeVisibility() {
        const fields = this.componentHtml.querySelectorAll('.onchange-trigger');
        fields.forEach(field => {
            field.dispatchEvent(new Event('change'));
        });
    }

    fillData() {
        return;
    }

    close() {
        if (!this.isOpen) return;

        this.componentClose();
        if (this.hasOverlay && this.overlayHtml) this.overlayHtml.style.display = 'none';
        
        this.isOpen = false;
        document.removeEventListener('keydown', this.escapeHandler);
        this.destroy();
    }

    componentClose() {
        return;
    }

    destroy() {
        this.componentHtml?.remove();
        this.componentHtml = null;
    }
}
