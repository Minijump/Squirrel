import { Modal } from './modal.js';

export class ConfirmationModal extends Modal {
    constructor(options = {}) {
        const modalOptions = {
            title: options.title || 'Confirm Action',
            id: 'confirmation-modal-' + Math.random().toString(36).substring(2, 11)
        };
        const confirmModalOptions = {
            message: options.message || 'Are you sure you want to proceed?',
            confirmText: options.confirmText || 'Confirm',
            cancelText: options.cancelText || 'Cancel',
            confirmClass: options.confirmClass || 'btn-primary',
            cancelClass: options.cancelClass || 'btn-secondary',
            onConfirm: options.onConfirm || (() => {}),
            onCancel: options.onCancel || (() => {}),
        };   
        super(modalOptions);
        Object.assign(this, confirmModalOptions);
    }

    createContent() {
        const content = document.createElement('div');
        content.innerHTML = `
            <p id="message" style="margin-bottom: 20px; color: var(--primary-text-color);">${this.message}</p>
            <div style="display: flex; justify-content: flex-end; gap: 10px;">
                <button type="button" id="cancel-btn" class="${this.cancelClass}">${this.cancelText}</button>
                <button type="button" id="confirm-btn" class="${this.confirmClass}">${this.confirmText}</button>
            </div>
        `;
        return content;
    }

    bindEvents() {
        super.bindEvents();
        
        const confirmBtn = this.componentHtml.querySelector('#confirm-btn');
        const cancelBtn = this.componentHtml.querySelector('#cancel-btn');
        
        confirmBtn.addEventListener('click', () => {
            this.close();
            this.onConfirm();
        });
        
        cancelBtn.addEventListener('click', () => {
            this.close();
            this.onCancel();
        });
    }
}
