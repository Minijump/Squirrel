import { FormModal } from '/static/base/js/components/modal.js';

const FORM_INPUTS = {
    'name': {
        'string': 'Project Name',
        'type': 'str',
        'required': true,
        'placeholder': 'Enter project name',
    },
    'description': {
        'string': 'Project Description',
        'type': 'txt',
        'required': false,
        'placeholder': 'Enter project description',
    },
    'project_type': {
        'string': 'Project Type',
        'type': 'select',
        'required': true,
        "options": [["std", "Standard"]],
    },
    // TODO: get type from PROJECT_TYPE_REGISTRY
}

document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('click', function() {
        if (card.classList.contains('card-new')) {
            const modal = new FormModal({
                title: 'Create New Project',
                formId: 'createProjectModalForm',
                inputs: FORM_INPUTS,
                submitRoute: '/projects/create/',
            });
            modal.open();
            return;
        }
        const projectDir = this.getAttribute('data-project-dir');
        window.location.href = `/projects/open/?project_dir=${encodeURIComponent(projectDir)}`;
    });
});
