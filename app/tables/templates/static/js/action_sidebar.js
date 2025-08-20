import { FormSidebar } from '/static/utils/components/sidebar/sidebar.js';
import { Field } from '/static/utils/components/field/field.js';


export class ActionSidebar extends FormSidebar {
    constructor(actionName, actionData, options = {}) {
        options.title = options.actionString || `Action: ${actionName}`;
        options.id = `ActionSidebar-${actionName}-${Math.random().toString(36).substring(2, 11)}`;
        super(options);
        Object.assign(this, {actionName, actionData});
    }

    createContent() {
        const sidebarContent = document.createElement('div')
        sidebarContent.innerHTML = `
            <form id="action-sidebar-form" action="/tables/execute_action/" method="post" class="std-form">
                <input type="hidden" name="action_name" class="sync-action-name" required>
                <input type="hidden" name="project_dir" value="${this.projectDir}">
                <input type="hidden" name="table_name" required>
                <div id="args"></div>
                <button type="submit" class="btn-primary" style="margin-top: 10px;">Confirm</button>
            </form>
        `;

        return sidebarContent;
    }

    async addInputs() {
        try {
            const response = await fetch(`/tables/get_action_args/?action_name=${this.actionName}`);
            const args = await response.json();
            
            const argsDiv = this.componentHtml.querySelector('#args');
            argsDiv.innerHTML = '';
            Object.keys(args).forEach(key => {
                const field = new Field(key, args[key]);
                argsDiv.appendChild(field.inputDivHTML);
            });
        } catch (error) {
            console.error('Error loading action arguments:', error);
        }
    }

    async fillData() {
        await this.addInputs();
        let data = this.actionData || {};
        // table_name, col_name and coll_idx already in data 
        // (see getColumnInfo or infos provided in openSidebarActionForm)
        const hiddenInputs = {'action_name': this.actionName, 'project_dir': this.projectDir};
        data = {...data, ...hiddenInputs};

        Object.keys(data).forEach(key => {
            const inputElements = this.componentHtml.querySelectorAll(`[name="${key}"], #${key}`);
            if (inputElements.length > 0) {
                inputElements.forEach(element => {
                    element.value = data[key];
                });
            }
            else console.warn(`Element with id ${key} not found in the form.`);
        });
        const onchangeElements = this.componentHtml.querySelectorAll('[onchange]');
        onchangeElements.forEach(element => {
            element.dispatchEvent(new Event('change'));
        });
        this.defaultFocus();
    }
}
