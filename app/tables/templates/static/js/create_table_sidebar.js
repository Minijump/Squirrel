import { FormSidebar } from '/static/base/js/components/sidebar.js';

export function openCreateTableSidebar() {
    const formInputs = getCreateTableFormInputs();
    const formData = {
        action_name: 'CreateTable',
        project_dir: new URLSearchParams(window.location.search).get('project_dir')
    };
    
    const sidebar = new FormSidebar({
        id: 'CreateTableSidebar',
        title: 'Create Table',
        formInputs: formInputs,
        formData: formData,
        formSubmitRoute: '/tables/execute_action/'
    });

    sidebar.open();
    return sidebar;
}

function getCreateTableFormInputs() {
    return {
        action_name: {type: 'text', invisible: true, required: true},
        project_dir: {type: 'text', invisible: true, required: true},
        table_name: {
            label: 'Table Name:',
            type: 'text',
            required: true,
            placeholder: 'Enter table name'
        },
        source_creation_type: {
            label: 'From:',
            type: 'select',
            required: true,
            select_options: [
                ['data_source', 'Data Sources'],
                ['other_tables', 'Other Tables']
            ],
            onchange: "onchangeFormValue('TableCreation_source_creation_type', event)"
        },
        data_source_dir: {
            label: 'Data Source:',
            type: 'select',
            required: false,
            select_options: getAvailableDataSources(),
            onchange_visibility: ["TableCreation_source_creation_type", "data_source"]
        },
        table_df: {
            label: 'Table:',
            type: 'select',
            required: false,
            select_options: getAvailableTables(),
            onchange_visibility: ["TableCreation_source_creation_type", "other_tables"]
        }
    };
}


function getAvailableDataSources() {
    const sourcesScript = document.getElementById('sources-data');
    const sources = JSON.parse(sourcesScript.textContent);
    if (Array.isArray(sources)) {
        return sources.map(source => [
            source.directory,
            source.name
        ]);
    }
}

function getAvailableTables() {
    const tablesScript = document.getElementById('tables-data');
    const tables = JSON.parse(tablesScript.textContent);
    if (typeof tables === 'object') {
        const tableKeys = Object.keys(tables);
        return tableKeys.map(table => [table, table]);
    }
}
