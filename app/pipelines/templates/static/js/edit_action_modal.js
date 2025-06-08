import { Modal } from '/static/base/js/components/modal.js';


export class EditActionModal extends Modal {
    constructor(actionId, actionName, actionCode, options = {}) {
        options['content'] = document.getElementById('editActionModalBody').innerHTML;
        options['id'] = 'editActionModal';
        options['title'] = 'Edit Action';
        super(options);
        this.actionId = actionId ;
        this.actionName = actionName;
        this.actionCode = actionCode;
        this.projectDir = new URLSearchParams(window.location.search).get('project_dir');
    }

    createContent() {
        const content = super.createContent();

        const deleteBtn = content.querySelector('#deleteButton');
        deleteBtn.onclick = () => {
            if (confirm('Are you sure you want to delete this action?')) {
                const modalInstance = this; 
                modalInstance.deletePipelineAction();
            }
        }

        return content;
    }

    async fillData() {
        this.element.querySelector('strong[id="modal-action-name"]').textContent = this.actionName;
        this.element.querySelector('input[name="project_dir"]').value = this.projectDir;
        this.element.querySelector('input[name="action_id"]').value = this.actionId;
        this.element.querySelector('textarea[name="action_code"]').value = this.actionCode;
    }

    deletePipelineAction() {
        const url = `/pipeline/delete_action?project_dir=${this.projectDir}&delete_action_id=${this.actionId}`;  
        fetch(url, { method: 'POST' })
            .then(response => response.ok 
                ? window.location.href = `/pipeline/?project_dir=${this.projectDir}`
                : console.error('Error:', response.statusText))
            .catch(error => console.error('Error:', error));
    }
}
