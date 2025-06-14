import { FormModal } from '/static/base/js/components/modal.js';


async function generateFormInputs() {
    let projectTypeOptions = [["std", "Standard"]];
    try {
        const response = await fetch('/projects/get_type_options/');
        const data = await response.json();
        projectTypeOptions = data.options;
    } catch (error) {
        console.error('Error fetching project type options:', error);
    }
    const formInputs = {
        'name': {
            'string': 'Project Name',
            'type': 'text',
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
            "options": projectTypeOptions,
        },
    };
    return formInputs;
}

export async function openCreateProjectModal() {
    const formInputs = await generateFormInputs();
    const modal = new FormModal({
        title: 'Create New Project',
        id: 'createProjectModal',
        formId: 'createProjectModalForm',
        formInputs: formInputs,
        formSubmitRoute: '/projects/create/',
    });
    modal.open();
}
