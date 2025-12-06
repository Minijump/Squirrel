import { FormModal } from '/static/utils/components/modal/modal.js';

// TODO: use dynamic inputs such as in ActionSidebar
const FORMINPUTS = {
    'action_name': {
        'type': 'text',
        'required': true,
        'invisible': true,
    },
    'project_dir': {
        'type': 'text',
        'required': true,
        'invisible': true,
    },
    'table_name': {
        'type': 'text',
        'required': true,
        'invisible': true,
    },
    'custom_action_code': {
        'label': 'Action Code',
        'type': 'sq_action',
        'required': true,
        'info': "Your tables are available in a dictionnary called tables, to edit it use tables['table_name']<br>i.e.: tables['table_name']['col_name'] = tables['table_name']['col_name'] * 2",
    },
    'custom_action_name': {
        'label': 'Action Name',
        'type': 'text',
        'required': true,
        'info': 'Name used in the pipeline',
    },
};

export async function openCustomActionModal(tableName='') {
    const modal = new FormModal({
        title: 'Custom Action',
        formId: 'customActionModalForm',
        formInputs: FORMINPUTS,
        formSubmitRoute: '/tables/add_action/',
        formData: {
            'action_name': 'CustomAction',
            'project_dir': new URLSearchParams(window.location.search).get('project_dir'),
            'table_name': tableName,
        },
    });
    modal.open();
}
