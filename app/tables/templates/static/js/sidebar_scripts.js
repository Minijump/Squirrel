import { ActionSidebar } from './action_sidebar.js';
import { openCreateTableSidebar } from './create_table_sidebar.js';
import { openExportTableSidebar } from './export_table_sidebar.js';


export async function openSidebarActionForm(actionName, data = {}) {
    const actionSidebar = new ActionSidebar({
        title: `Action: ${actionName}`,
        id: 'ActionSidebar',
        projectDir: data.project_dir || new URLSearchParams(window.location.search).get('project_dir')
    });
    
    await actionSidebar.openForAction(actionName, data);
}

export function openSidebarForm(sidebarType, options = {}) {
    if (sidebarType === 'CreateTable') return openCreateTableSidebar();
    if (sidebarType === 'ExportTable') return openExportTableSidebar(options);
}
