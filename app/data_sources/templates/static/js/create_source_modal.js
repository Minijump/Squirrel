import { FormModal } from '/static/utils/components/modal/modal.js';
import { Field } from '/static/utils/components/field/field.js';


async function generateFormInputs() {
    const response = await fetch('/data_sources/get_available_data_sources_type/');
    const data = await response.json();
    const availableDataSourcesType = data.available_types || [];
    const formInputs = {
        'project_dir': {
            'label': 'Project Directory',
            'type': 'text',
            'required': true,
            'invisible': true,
        },
        'source_name': {
            'label': 'Source Name',
            'type': 'text',
            'required': true,
            'placeholder': 'Enter source name',
        },
        'source_description': {
            'label': 'Source Description',
            'type': 'textarea',
            'required': false,
            'placeholder': 'Enter source description',
        },
        'source_type': {
            'label': 'Source Type',
            'type': 'select',
            'required': true,
            'select_options': availableDataSourcesType,
        },
    };
    return formInputs;
}


export class CreateSourceModal extends FormModal {
    constructor(options = {}) {
        options['id'] = 'createSourceModal';
        options['title'] = 'Create New Source';
        options['formId'] = 'createSourceModalForm';
        options['formSubmitRoute'] = '/source/create/';
        super(options);
    }

    createContent() {
        const content = super.createContent();

        const sourceTypeSpecificArgs = document.createElement('div');
        sourceTypeSpecificArgs.id = 'sourceTypeSpecificArgs';
        const form = content.querySelector('#createSourceModalForm');
        const submitButton = form.querySelector('button[type="submit"]');
        form.insertBefore(sourceTypeSpecificArgs, submitButton);

        return content;
    }

    bindEvents() {
        super.bindEvents();
        const sourceTypeSelect = document.querySelector('#createSourceModalForm select[name="source_type"]');
        sourceTypeSelect.addEventListener('change', (event) => {
            this.onchangeSourceType(event);
        });
    }

    async onchangeSourceType(event) {
        const specificSourceArgs = await this.getSourceTypeSpecificArgs(event.target.value);
        const sourceTypeSpecificArgsDiv = document.querySelector('#sourceTypeSpecificArgs');
        sourceTypeSpecificArgsDiv.innerHTML = '';
        Object.keys(specificSourceArgs).forEach(key => {
            const input = new Field(key, specificSourceArgs[key]);
            sourceTypeSpecificArgsDiv.appendChild(input.inputDivHTML);
        });
        return;
    }

    async getSourceTypeSpecificArgs(sourceType) {
        const response = await fetch(`/data_sources/get_source_creation_specific_args/${sourceType}/`);
        return response.json();
    }
    
    fillData() {
        const sourceTypeSelect = document.querySelector('#createSourceModalForm select[name="source_type"]');
        if (sourceTypeSelect) {
            // Required for when the modal opens
            sourceTypeSelect.dispatchEvent(new Event('change'));
        }
    }
}

export async function openCreateSourcetModal() {
    const formInputs = await generateFormInputs();
    const formData = {
        'project_dir': new URLSearchParams(window.location.search).get('project_dir'),
    };
    const modal = new CreateSourceModal({
        formInputs: formInputs,
        formData: formData,
    });
    modal.open();
}
