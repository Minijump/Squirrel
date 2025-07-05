import { FormSidebar } from '/static/base/js/components/sidebar.js';


export class CreateTableSidebar extends FormSidebar {
    bindEvents() {
        super.bindEvents();
        
        const sourceTypeSelect = this.sidebarHtml.querySelector('#source_creation_type');
        if (sourceTypeSelect) {
            sourceTypeSelect.addEventListener('change', () => {
                this.toggleSourceElements();
            });
            this.toggleSourceElements();
        }
    }

    toggleSourceElements() {
        const select = this.sidebarHtml.querySelector('#source_creation_type');
        if (!select) return;
        
        const dataSourceDiv = this.sidebarHtml.querySelector('#data_source_dir').closest('div');
        const tableDiv = this.sidebarHtml.querySelector('#table_df').closest('div');
        
        const isDataSourceSelected = select.value === 'data_source';
        dataSourceDiv.style.display = isDataSourceSelected ? 'block' : 'none';
        tableDiv.style.display = isDataSourceSelected ? 'none' : 'block';
        this.sidebarHtml.querySelector('#data_source_dir').required = isDataSourceSelected;
        this.sidebarHtml.querySelector('#table_df').required = !isDataSourceSelected;
    }
}

export function openCreateTableSidebar() {
    const formInputs = getCreateTableFormInputs();
    const formData = {
        action_name: 'CreateTable',
        project_dir: new URLSearchParams(window.location.search).get('project_dir')
    };
    
    // TODO: Everything is set up here and not in the sidebar constructor
    // This is because the goal is to implement a reusable way to change depending of a select field (and then use FormSidebar only)
    // see ConditionalFieldManager?
    const sidebar = new CreateTableSidebar({
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
            ]
        },
        data_source_dir: {
            label: 'Data Source:',
            type: 'select',
            required: false,
            select_options: getAvailableDataSources()
        },
        table_df: {
            label: 'Table:',
            type: 'select',
            required: false,
            select_options: getAvailableTables()
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
