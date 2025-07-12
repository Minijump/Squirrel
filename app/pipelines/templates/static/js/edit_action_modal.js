import { FormModal } from '/static/utils/components/modal/modal.js';
import { ConfirmationModal } from '/static/utils/components/modal/confirmation_modal.js';


export class EditActionModal extends FormModal {
    constructor(actionId, actionName, actionCode, options = {}) {
        const formInputs = {
            'project_dir': {'type': 'text', 'required': true, 'invisible': true},
            'action_id': {'type': 'text', 'required': true, 'invisible': true},
            'action_code': {'label': 'Python Code:', 'type': 'textarea','required': true}
        };
        
        const formData = {
            'project_dir': new URLSearchParams(window.location.search).get('project_dir'),
            'action_id': actionId,
            'action_code': actionCode
        };

        super({
            formInputs, formData,
            formSubmitRoute: '/pipeline/edit_action/', id: 'editActionModal', title: 'Edit Action',
            ...options
        });
        Object.assign(this, { actionId, actionName, actionCode });
    }

    createContent() {
        const content = super.createContent();
        const form = content.querySelector('form');
        
        // Add action name display
        const actionNameDisplay = Object.assign(document.createElement('strong'), {
            textContent: this.actionName,
            style: 'display: block; margin-bottom: 15px;'
        });
        form.insertBefore(actionNameDisplay, form.firstChild);
        
        // Add delete button
        const deleteButton = Object.assign(document.createElement('button'), {
            type: 'button',
            className: 'btn-danger',
            textContent: 'Delete Action',
            style: 'margin-left: 10px; height: 100%;',
            onclick: () => this.showDeleteConfirmation()
        });
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.parentNode.insertBefore(deleteButton, submitButton.nextSibling);

        // Resize textarea (action code input)
        const actionCodeInput = form.querySelector('textarea[name="action_code"]');
        if (actionCodeInput) Object.assign(actionCodeInput.style, {height: '100px', width: '600px'});

        return content;
    }

    showDeleteConfirmation() {
        const confirmationModal = new ConfirmationModal({
            title: 'Delete Action',
            message: `Are you sure you want to delete this action ?`,
            confirmText: 'Delete',
            cancelText: 'Cancel',
            confirmClass: 'btn-danger',
            cancelClass: 'btn-secondary',
            onConfirm: () => this.deletePipelineAction()
        });
        confirmationModal.open();
    }

    deletePipelineAction() {
        const url = `/pipeline/delete_action?project_dir=${this.projectDir}&delete_action_id=${this.actionId}`;  
        fetch(url, { method: 'POST' })
            .then(async response => {
                if (!response.ok) {
                    console.error('Error deleting action:', response.statusText);
                }
                await window.handleRedirectNotification(response);
                window.location.href = `/pipeline/?project_dir=${this.projectDir}`;
            })
            .catch(error => {
                console.error('Error deleting action:', response.statusText);
                storeNotification(`Failed to delete action: ${error}`, 'error');
            });
    }
}
