import { ActionSidebar } from './action_sidebar.js';
import { openCreateTableSidebar } from './create_table_sidebar.js';
import { openExportTableSidebar } from './export_table_sidebar.js';


export async function openSidebarActionForm(actionName, data = {}) {
    const projectDir = new URLSearchParams(window.location.search).get('project_dir')
    const actionSidebar = new ActionSidebar(actionName, data, projectDir, {});
    await actionSidebar.openForAction();
}

export function openSidebarForm(sidebarType, options = {}) {
    if (sidebarType === 'CreateTable') return openCreateTableSidebar();
    if (sidebarType === 'ExportTable') return openExportTableSidebar(options);
}
