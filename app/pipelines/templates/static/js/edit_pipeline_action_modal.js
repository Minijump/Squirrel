import { FormModal } from '/static/utils/components/modal/modal.js';

export class EditPipelineActionModal extends FormModal {
    constructor(actionId, options = {}) {
        const formInputs = {
            'project_dir': {'type': 'text', 'required': true, 'invisible': true},
            'action_id': {'type': 'text', 'required': true, 'invisible': true},
            'custom_description': {
                'type': 'textarea',
                'label': 'Custom Description',
                'placeholder': 'Enter a custom description for this action in the pipeline...',
                'required': false,
                'info': 'Leave empty to use the automatic description'
            }
        };
        const formData = {
            'project_dir': new URLSearchParams(window.location.search).get('project_dir'),
            'action_id': actionId,
        };

        super({
            formInputs,
            formData,
            formSubmitRoute: '/pipeline/edit_pipeline_action/', id: 'editPipelineActionModal', title: 'Edit Pipeline Action',
            ...options
        });
        this.actionId = actionId;
    }

    async fillData() {
        const data = await this.getActionData();
        
        const customDescInput = this.componentHtml.querySelector('[name="custom_description"]');
        if (customDescInput && data) {
            customDescInput.value = data.custom_description || '';
        }
        
        this.defaultFocus();
    }

    async getActionData() {
        const response = await fetch(`/pipeline/get_pipeline_action_data/?project_dir=${this.projectDir}&action_id=${this.actionId}`);
        if (!response.ok) {
            console.error('Error fetching action data:', response.statusText);
            return null;
        }
        return await response.json();
    }
}
