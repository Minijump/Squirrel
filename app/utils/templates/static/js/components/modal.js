import { Form } from './form.js';
import { TransientComponent } from './transient_component.js';


export class Modal extends TransientComponent {
    constructor(options = {}) {
        super(options);
        this.id = options.id || 'modal-' + Math.random().toString(36).substring(2, 11);
        this.title = options.title || 'Modal';
        this.componentHtml = null;
        this.overlayId = this.id || 'modal-overlay';
        this.create();
    }

    create() {
        this.componentHtml = this.getOrCreateOverlay();
        this.componentHtml.classList.add('modal');
        
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        
        const header = this.createHeader();
        const content = this.createContent();
        content.className = 'modal-body';
        
        modalContent.appendChild(header);
        modalContent.appendChild(content);
        this.componentHtml.appendChild(modalContent);
        document.body.appendChild(this.componentHtml); 
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

    componentOpen() {
        this.componentHtml.style.display = 'flex';
    }

    componentClose() {
        this.componentHtml.style.display = 'none';
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
        options.content = new Form(formOptions);
        super(options);
    }
}
