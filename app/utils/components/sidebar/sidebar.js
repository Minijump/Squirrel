import { Form } from '/static/utils/components/form/form.js';
import { TransientComponent } from '/static/utils/components/transient_component/transient_component.js';


export class Sidebar extends TransientComponent {
    constructor(options = {}) {
        super(options);
        this.id = options.id || 'sidebar-' + Math.random().toString(36).substring(2, 11);
        this.title = options.title || 'Sidebar';
        this.width = options.width || '320px';
        this.position = options.position || 'right';
        this.overlayId = options.overlayId || 'sidebar-overlay';
        this.create();
    }

    create() {
        this.componentHtml = Object.assign(document.createElement('div'), {
            className: `${this.position}-sidebar transient-component`,
            id: this.id
        });
        this.componentHtml.innerHTML = `<a href="javascript:void(0)" class="close-btn">&times;</a>`;
        this.componentHtml.appendChild(this.createContent());
        
        if (this.hasOverlay) this.overlayHtml = this.getOrCreateOverlay();
        
        document.body.appendChild(this.componentHtml);
        this.bindEvents();
    }

    componentOpen() {
        this.componentHtml.style.width = this.width;
    }

    componentClose() {
        this.componentHtml.style.width = '0';
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
}
