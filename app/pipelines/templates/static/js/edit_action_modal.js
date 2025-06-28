import { Modal } from '/static/base/js/components/modal.js';


export class EditActionModal extends Modal {
    // Does not extends FormModal because we need to add a delete button (TODO?)
    constructor(actionId, actionName, actionCode, options = {}) {
        options['content'] = document.getElementById('editActionModalBody').innerHTML;
        options['id'] = 'editActionModal';
        options['title'] = 'Edit Action';
        super(options);
        Object.assign(this, { actionId, actionName, actionCode });
        this.projectDir = new URLSearchParams(window.location.search).get('project_dir');
    }

    createContent() {
        const content = super.createContent();

        content.querySelector('#deleteButton').onclick = () => {
            if (confirm('Are you sure you want to delete this action?')) {
                this.deletePipelineAction();
            }
        };

        return content;
    }

    fillData() {
        this.modalHtml.querySelector('strong[id="modal-action-name"]').textContent = this.actionName;
        this.modalHtml.querySelector('input[name="project_dir"]').value = this.projectDir;
        this.modalHtml.querySelector('input[name="action_id"]').value = this.actionId;
        this.modalHtml.querySelector('textarea[name="action_code"]').value = this.actionCode;
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
