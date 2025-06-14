import { FormModal } from '/static/base/js/components/modal.js';


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
    'default_table_name': {
        'type': 'text',
        'required': true,
        'invisible': true,
    },
    'custom_action_type': {
        'string': 'Action Type',
        'type': 'select',
        'required': true,
        "options": [["sq_action", "Squirrel Action"], ["python", "Python Code"]],
    },
    'custom_action_code': {
        'string': 'Action Code',
        'type': 'textarea',
        'required': true,
        'info': "Your tables are available in a dictionnary called dfs, to edit it use dfs['table_name']<br>i.e.: dfs['table_name']['col_name'] = dfs['table_name']['col_name'] * 2",
    },
    'custom_action_name': {
        'string': 'Action Name',
        'type': 'text',
        'required': true,
        'info': 'Name used in the pipeline',
    },
};

export async function openCustomActionModal(tableName='') {
    console.log(tableName)
    const modal = new FormModal({
        title: 'Custom Action',
        formId: 'customActionModalForm',
        formInputs: FORMINPUTS,
        formSubmitRoute: '/tables/execute_action/',
        formData: {
            'action_name': 'CustomAction',
            'project_dir': new URLSearchParams(window.location.search).get('project_dir'),
            'default_table_name': tableName,
        },
    });
    modal.open();
}
