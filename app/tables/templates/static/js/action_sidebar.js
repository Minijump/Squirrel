import { FormSidebar } from '/static/utils/components/sidebar/sidebar.js';
import { Field } from '/static/utils/components/field/field.js';
import { SquirrelDictionary } from '/static/utils/widgets/dictionary_widget/dictionary_widget.js';


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
            <div id="sidebar-tabs-buttons" class="sidebar-tabs" style="display: none;">
                <button class="tab-button active n-l-border n-r-border" onclick="this.switchTab(event, 'basic-tab')">Basic</button>
                <button id="kwargs-btn" class="tab-button n-r-border" style="display: none;" onclick="this.switchTab(event, 'advanced-tab')">Advanced</button>
            </div>
            <div id="basic-tab" class="tab-content active">
                <form action="/tables/execute_action/" method="post" class="std-form">
                    <input type="hidden" name="action_name" class="sync-action-name" required>
                    <input type="hidden" name="project_dir" value="${this.projectDir}">
                    <input type="hidden" name="table_name" required>
                    <div id="args"></div>
                    <button type="submit" class="btn-primary" style="margin-top: 10px;">Confirm</button>
                </form>
            </div>
            <div id="advanced-tab" class="tab-content">
                <form action="/tables/execute_action/" method="post" id="args-kwargs-form" class="std-form">
                    <input type="hidden" name="action_name" class="sync-action-name" required>
                    <input type="hidden" name="project_dir" value="${this.projectDir}">
                    <input type="hidden" name="table_name" required>
                    <input type="hidden" name="col_name" id="col_name" required>
                    <input type="hidden" name="col_idx" id="col_idx" required>
                    <input type="hidden" name="advanced" value="true">
                    <div id="args-kwargs" style="padding-left: 8px;"></div>
                    <button type="submit" class="btn-primary" style="margin-top: 10px;">Confirm</button>
                </form>
            </div>
        `;
        const basicTabBtn = sidebarContent.querySelector('.tab-button');
        const advancedTabBtn = sidebarContent.querySelector('#kwargs-btn');
        basicTabBtn.onclick = (evt) => this.switchTab(evt, 'basic-tab');
        advancedTabBtn.onclick = (evt) => this.switchTab(evt, 'advanced-tab');

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

    async addKwargs() {
        try {
            const response = await fetch(`/tables/get_action_kwargs/?action_name=${this.actionName}`);
            const kwargs = await response.json();
            
            const tabButtons = this.componentHtml.querySelector('#sidebar-tabs-buttons');
            const kwargsForm = this.componentHtml.querySelector('#args-kwargs-form');
            const kwargsBtn = this.componentHtml.querySelector('#kwargs-btn');
            const kwargsDiv = this.componentHtml.querySelector('#args-kwargs');
            
            const hasKwargs = Object.keys(kwargs).length > 0;
            tabButtons.style.display = hasKwargs ? 'flex' : 'none';
            kwargsForm.style.display = hasKwargs ? 'block' : 'none';
            kwargsBtn.style.display = hasKwargs ? 'block' : 'none';
            if (!hasKwargs) return;
                        
            kwargsDiv.innerHTML = '';
            const kwargsInput = document.createElement('textarea');
            kwargsInput.name = "kwargs";
            kwargsInput.setAttribute('widget', 'squirrel-dictionary');
            kwargsInput.value = JSON.stringify(kwargs, function(key, value) {
                // Convert JavaScript to Python readable
                if (typeof value === 'boolean') return value ? 'True' : 'False';
                if (value === null) return 'None';
                return value;
            });
            
            kwargsDiv.appendChild(kwargsInput);
            new SquirrelDictionary(kwargsInput);
        } catch (error) {
            console.error('Error loading action kwargs:', error);
        }
    }

    async fillData() {
        await this.addInputs();
        await this.addKwargs();
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
    }

    switchTab(evt, tabId) {
        this.componentHtml.querySelectorAll(".tab-content, .tab-button").forEach(el => el.classList.remove("active"));
        this.componentHtml.querySelector(`#${tabId}`).classList.add("active");
        evt.currentTarget.classList.add("active");
    }
}
