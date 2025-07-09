import { FormSidebar } from '/static/utils/components/sidebar/sidebar.js';


export function openExportTableSidebar(options = {}) {
    const formInputs = getExportTableFormInputs();
    const formData = {
        table_name: options.table_name || '',
        project_dir: new URLSearchParams(window.location.search).get('project_dir')
    };
    
    const sidebar = new FormSidebar({
        id: 'ExportTableSidebar',
        title: 'Export Table',
        formInputs: formInputs,
        formData: formData,
        formSubmitRoute: '/tables/export_table/'
    });
    
    sidebar.open();
    return sidebar;
}

function getExportTableFormInputs() {
    return {
        table_name: {type: 'text', invisible: true, required: true},
        project_dir: {type: 'text', invisible: true, required: true},
        export_type: {
            label: 'Export Format:',
            type: 'select',
            required: true,
            select_options: [
                ['csv', 'CSV'],
                ['xlsx', 'Excel (XLSX)'],
                ['json', 'JSON'],
                ['pkl', 'Pickle']
            ]
        }
    };
}
