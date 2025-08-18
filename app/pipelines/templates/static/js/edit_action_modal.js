import { FormModal } from '/static/utils/components/modal/modal.js';
import { ConfirmationModal } from '/static/utils/components/modal/confirmation_modal.js';
import { Field } from '/static/utils/components/field/field.js';

// TODO editaction: refactor + improve + remove useless things
export class EditActionModal extends FormModal {
    constructor(actionId, options = {}) {
        const formInputs = {
            'project_dir': {'type': 'text', 'required': true, 'invisible': true},
            'action_id': {'type': 'text', 'required': true, 'invisible': true}
        };
        
        const formData = {
            'project_dir': new URLSearchParams(window.location.search).get('project_dir'),
            'action_id': actionId
        };

        super({
            formInputs, formData,
            formSubmitRoute: '/pipeline/edit_action/', id: 'editActionModal', title: 'Edit Action',
            ...options
        });
        this.actionId = actionId;
        this.actionData = null;
    }

    async open() {
        // Load action data before opening
        await this.loadActionData();
        super.open();
        // Add dynamic inputs after modal is created
        setTimeout(() => this.addDynamicInputsAfterOpen(), 100);
    }

    createContent() {
        const content = super.createContent();
        const form = content.querySelector('form');
        
        // Add action name display placeholder
        const actionNameDisplay = Object.assign(document.createElement('strong'), {
            textContent: 'Loading...',
            style: 'display: block; margin-bottom: 15px;',
            id: 'action-name-display'
        });
        form.insertBefore(actionNameDisplay, form.firstChild);
        
        // Add container for dynamic inputs
        const argsDiv = document.createElement('div');
        argsDiv.id = 'dynamic-args';
        const submitButton = form.querySelector('button[type="submit"]');
        form.insertBefore(argsDiv, submitButton);
        
        // Add delete button
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

    async loadActionData() {
        try {
            const response = await fetch(`/pipeline/get_action_data/?project_dir=${this.projectDir}&action_id=${this.actionId}`);
            this.actionData = await response.json();
        } catch (error) {
            console.error('Error loading action data:', error);
        }
    }

    async addDynamicInputsAfterOpen() {
        if (!this.actionData) return;

        const form = this.componentHtml.querySelector('form');
        
        // Update action name display
        const actionNameDisplay = form.querySelector('#action-name-display');
        if (actionNameDisplay && this.actionData.action_name) {
            actionNameDisplay.textContent = this.actionData.action_name;
        }
        
        // Add dynamic inputs
        const argsDiv = form.querySelector('#dynamic-args');
        Object.keys(this.actionData.args).forEach(key => {
            const field = new Field(key, this.actionData.args[key]);
            argsDiv.appendChild(field.inputDivHTML);
        });

        // Pre-fill form data
        this.fillFormData(form);
    }

    fillFormData(form) {
        if (!this.actionData || !this.actionData.form_data) return;

        Object.keys(this.actionData.form_data).forEach(key => {
            const inputElements = form.querySelectorAll(`[name="${key}"], #${key}`);
            if (inputElements.length > 0) {
                inputElements.forEach(element => {
                    element.value = this.actionData.form_data[key];
                });
            }
        });

        // Trigger change events for conditional visibility
        const onchangeElements = form.querySelectorAll('[onchange]');
        onchangeElements.forEach(element => {
            element.dispatchEvent(new Event('change'));
        });
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
