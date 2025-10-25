import { FormModal } from '/static/utils/components/modal/modal.js';
import { ConfirmationModal } from '/static/utils/components/modal/confirmation_modal.js';
import { Field } from '/static/utils/components/field/field.js';

export class EditActionModal extends FormModal {
    constructor(actionId, actionName, actionError = '', options = {}) {
        const formInputs = {
            'project_dir': {'type': 'text', 'required': true, 'invisible': true},
            'action_id': {'type': 'text', 'required': true, 'invisible': true}
        };
        const formData = {
            'project_dir': new URLSearchParams(window.location.search).get('project_dir'),
            'action_id': actionId
        };

        super({
            formInputs,
            formData,
            formSubmitRoute: '/pipeline/edit_action/', id: 'editActionModal', title: 'Edit Action',
            ...options
        });
        this.actionId = actionId;
        this.actionName = actionName;
        this.actionError = actionError;
    }

    createContent() {
        const content = super.createContent();
        const form = content.querySelector('form');
        
        const actionNameDisplay = Object.assign(document.createElement('strong'), {
            textContent: this.actionName,
            style: 'display: block; margin-bottom: 15px;',
            id: 'action-name-display'
        });
        form.insertBefore(actionNameDisplay, form.firstChild);

        if (this.actionError) {
            const errorDiv = Object.assign(document.createElement('div'), {
                style: 'color: red; margin-bottom: 15px;',
                textContent: this.actionError
            });
            form.insertBefore(errorDiv, form.firstChild);
        }

        const argsDiv = document.createElement('div');
        argsDiv.id = 'args';
        const submitButton = form.querySelector('button[type="submit"]');
        form.insertBefore(argsDiv, submitButton);
        
        const deleteButton = Object.assign(document.createElement('button'), {
            type: 'button',
            className: 'btn-danger',
            textContent: 'Delete Action',
            style: 'margin-left: 10px; height: 100%;',
            onclick: () => this.showDeleteConfirmation()
        });
        submitButton.parentNode.insertBefore(deleteButton, submitButton.nextSibling);

        return content;
    }

    async fillData() {
        // Similar to ActionSidebar (TO FACTORIZE)
        const data = await this.getActionData(); // Called before addInputs, else we see a little glitch cause by the time of the request
        await this.addInputs(data);

        const onchangeElements = this.componentHtml.querySelectorAll('[onchange]');
        onchangeElements.forEach(element => {
            element.dispatchEvent(new Event('change'));
        });
        this.defaultFocus();
    }

    async addInputs(actionData = {}) {
        // Same than ActionSidebar (TO FACTORIZE)
        try {
            const response = await fetch(`/tables/get_action_args/?action_name=${this.actionName}&project_dir=${this.projectDir}`);
            const args = await response.json();
            
            const argsDiv = this.componentHtml.querySelector('#args');
            argsDiv.innerHTML = '';
            Object.keys(args).forEach(key => {
                const defaultValue = actionData[key];
                const field = new Field(key, args[key], defaultValue);
                argsDiv.appendChild(field.inputDivHTML);
            });
        } catch (error) {
            console.error('Error loading action arguments:', error);
        }
    }

    async getActionData() {
        const response = await fetch(`/pipeline/get_action_data/?project_dir=${this.projectDir}&action_id=${this.actionId}`);
        if (!response.ok) {
            console.error('Error fetching action data:', response.statusText);
            return null;
        }
        return await response.json();
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
                window.showNotification(`Failed to delete action: ${error}`, 'error');
            });
    }
}
