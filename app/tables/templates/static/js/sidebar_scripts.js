import { ActionSidebar } from './action_sidebar.js';
import { openCreateTableSidebar } from './create_table_sidebar.js';
import { openExportTableSidebar } from './export_table_sidebar.js';


export async function openSidebarActionForm(actionName, data = {}) {
    const actionSidebar = new ActionSidebar(actionName, data, {});
    await actionSidebar.open();
}

export function openSidebarForm(sidebarType, options = {}) {
    if (sidebarType === 'CreateTable') return openCreateTableSidebar();
    if (sidebarType === 'ExportTable') return openExportTableSidebar(options);
}
