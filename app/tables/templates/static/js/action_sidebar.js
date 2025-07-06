import { FormSidebar } from '/static/base/js/components/sidebar.js';
import { Field } from '/static/base/js/components/field.js';
import { ConditionalFieldManager } from '/static/base/js/components/conditional_field_manager.js';
import { SquirrelDictionary } from '/static/base/js/widgets/dictionary_widget.js';


export class ActionSidebar extends FormSidebar {
    constructor(actionName, actionData, projectDir, options = {}) {
        options.title = `Action: ${actionName}`;
        options.id = `ActionSidebar-${actionName}-${Math.random().toString(36).substring(2, 11)}`;
        super(options);
        Object.assign(this, {actionName, actionData, projectDir});
        this.conditionalManager = null;
    }

    createContent() {
        const projectDir = new URLSearchParams(window.location.search).get('project_dir')
        const sidebarContent = document.createElement('div')
        sidebarContent.innerHTML = '';

        // Create tabs container
        const tabsContainer = document.createElement('div');
        tabsContainer.className = 'sidebar-tabs';
        tabsContainer.innerHTML = `
            <button class="tab-button active n-l-border n-r-border">Basic</button>
            <button id="kwargs-btn" class="tab-button n-r-border" style="display: none;">Advanced</button>
        `;
        const basicTabBtn = tabsContainer.querySelector('.tab-button');
        const advancedTabBtn = tabsContainer.querySelector('#kwargs-btn');
        basicTabBtn.onclick = (evt) => this.switchTab(evt, 'basic-tab');
        advancedTabBtn.onclick = (evt) => this.switchTab(evt, 'advanced-tab');
        sidebarContent.appendChild(tabsContainer);

        // Create basic tab content
        const basicTabContent = document.createElement('div');
        basicTabContent.id = 'basic-tab';
        basicTabContent.className = 'tab-content active';
        basicTabContent.innerHTML = `
            <form action="/tables/execute_action/" method="post" class="std-form">
                <input type="hidden" name="action_name" class="sync-action-name" required>
                <input type="hidden" name="project_dir" value="${projectDir}"> 
                <input type="hidden" name="table_name" required>
                <div id="args" style="padding-left: 8px;"></div>
                <button type="submit" class="btn-primary" style="margin-top: 10px;">Confirm</button>
            </form>
        `;
        sidebarContent.appendChild(basicTabContent);

        // Create advanced tab content
        const advancedTabContent = document.createElement('div');
        advancedTabContent.id = 'advanced-tab';
        advancedTabContent.className = 'tab-content';
        advancedTabContent.innerHTML = `
            <form action="/tables/execute_action/" method="post" id="args-kwargs-form" class="std-form">
                <input type="hidden" name="action_name" class="sync-action-name" required>
                <input type="hidden" name="project_dir" value="${projectDir}">
                <input type="hidden" name="table_name" required>
                <input type="hidden" name="col_name" id="col_name" required>
                <input type="hidden" name="col_idx" id="col_idx" required>
                <input type="hidden" name="advanced" value="true">
                <div id="args-kwargs" style="padding-left: 8px;"></div>
                <button type="submit" class="btn-primary" style="margin-top: 10px;">Confirm</button>
            </form>
        `;
        sidebarContent.appendChild(advancedTabContent);

        return sidebarContent;
    }

    async open() {
        await this.addInputs();
        await this.addKwargs();
        
        super.open();

        if (this.conditionalManager) this.conditionalManager.updateAll(); 
    }

    async addInputs() {
        try {
            const response = await fetch(`/tables/get_action_args/?action_name=${this.actionName}`);
            const args = await response.json();
            
            const argsDiv = this.sidebarHtml.querySelector('#args');
            argsDiv.innerHTML = '';
            
            Object.keys(args).forEach(key => {
                const field = new Field(key, args[key]);
                argsDiv.appendChild(field.inputDivHTML);
            });
            
            this.conditionalManager = new ConditionalFieldManager(this.sidebarHtml);
        } catch (error) {
            console.error('Error loading action arguments:', error);
        }
    }

    async addKwargs() {
        try {
            const response = await fetch(`/tables/get_action_kwargs/?action_name=${this.actionName}`);
            const kwargs = await response.json();
            
            const kwargsForm = this.sidebarHtml.querySelector('#args-kwargs-form');
            const kwargsBtn = this.sidebarHtml.querySelector('#kwargs-btn');
            
            if (Object.keys(kwargs).length === 0) {
                kwargsForm.style.display = 'none';
                kwargsBtn.style.display = 'none';
                return;
            }
            kwargsForm.style.display = 'block';
            kwargsBtn.style.display = 'block';
                        
            const kwargsDiv = this.sidebarHtml.querySelector('#args-kwargs');
            kwargsDiv.innerHTML = '';
            
            const kwargsInput = document.createElement('textarea');
            kwargsInput.name = "kwargs";
            kwargsInput.setAttribute('widget', 'squirrel-dictionary');
            kwargsInput.value = JSON.stringify(kwargs, function(key, value) {
                // Convert JavaScript booleans to Python string representations
                if (typeof value === 'boolean') {
                    return value ? 'True' : 'False';
                }
                // Convert JavaScript null to Python None
                if (value === null) {
                    return 'None';
                }
                return value;
            });
            
            kwargsDiv.appendChild(kwargsInput);
            new SquirrelDictionary(kwargsInput);
        } catch (error) {
            console.error('Error loading action kwargs:', error);
        }
    }

    fillData() {
        let data = this.actionData || {};
        // table_name, col_name and coll_idx already in data (see getColumnInfo or infos provided in openSidebarActionForm)
        const hiddenInputs = {'action_name': this.actionName, 'project_dir': this.projectDir};
        data = {...data, ...hiddenInputs};

        Object.keys(data).forEach(key => {
            const inputElements = this.sidebarHtml.querySelectorAll(`[name="${key}"], #${key}`);
            if (inputElements.length > 0) {
                inputElements.forEach(element => {
                    element.value = data[key];
                });
            }
            else console.warn(`Element with id ${key} not found in the form.`);
        });
    }

    switchTab(evt, tabId) {
        this.sidebarHtml.querySelectorAll(".tab-content, .tab-button").forEach(el => el.classList.remove("active"));
        this.sidebarHtml.querySelector(`#${tabId}`).classList.add("active");
        evt.currentTarget.classList.add("active");
    }
}
