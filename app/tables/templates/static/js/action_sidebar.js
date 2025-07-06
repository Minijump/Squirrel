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
                <input type="hidden" name="table_name" class="sync-table-name" required>
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
                <input type="hidden" name="table_name" class="sync-table-name" required>
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

    async openForAction() {
        await this.addInputs();
        await this.addKwargs();
        this.completeInputs(this.actionData);
        
        // Update conditional fields after all data is populated
        if (this.conditionalManager) {
            this.conditionalManager.updateAll();
        }
        
        this.open();
    }

    async addInputs() {
        try {
            const response = await fetch(`/tables/get_action_args/?action_name=${this.actionName}`);
            const args = await response.json();
            
            const argsDiv = this.sidebarHtml.querySelector('#args');
            argsDiv.innerHTML = '';
            
            Object.keys(args).forEach(key => {
                if (args[key].invisible) {
                    // For invisible inputs, create them directly without Field wrapper
                    const input = this.createInput(args[key]);
                    input.type = 'hidden';
                    input.name = key;
                    input.id = key;
                    argsDiv.appendChild(input);
                } else {
                    // Use Field component for visible inputs
                    const field = new Field(key, args[key]);
                    argsDiv.appendChild(field.inputDivHTML);
                    
                    // Add the right-sidebar-select class specifically for sidebar selects
                    const selectElement = field.inputDivHTML.querySelector('select');
                    if (selectElement) {
                        selectElement.classList.add('right-sidebar-select');
                    }
                    
                    if (args[key].type === 'dict') {
                        const input = field.inputDivHTML.querySelector('textarea');
                        new SquirrelDictionary(input);
                    }
                }
            });
            
            // Initialize conditional field manager after all inputs are added
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
            
            kwargsForm.querySelector('input[name="action_name"]').value = this.actionName;
            
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

    // Helper method for backward compatibility with hidden inputs
    createInput(arg) {
        let input = document.createElement('input');
        
        if (arg.type === 'textarea') {
            input = document.createElement('textarea');
        }
        
        if (arg.type === 'dict') {
            input = document.createElement('textarea');
            input.setAttribute('widget', 'squirrel-dictionary');
            const defaultOptions = {create: true, remove: true};
            const userOptions = arg.dict_options;
            const options = userOptions ? {...defaultOptions, ...userOptions} : defaultOptions;
            input.setAttribute('options', JSON.stringify(options));
            input.value = JSON.stringify(arg.default || {});
        }
        
        if (arg.type === 'number') {
            input.type = 'number';
            input.step = arg.step || 'any';
        }
        
        if (arg.type === 'select') {
            input = document.createElement('select');
            arg.select_options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option[0];
                optionElement.text = option[1];
                input.appendChild(optionElement);
            });
        }
        
        return input;
    }

    completeInputs(data = {}) {
        // Set action name in both forms
        const actionNameInputs = this.sidebarHtml.querySelectorAll('.sync-action-name');
        actionNameInputs.forEach(input => input.value = this.actionName);
        
        // Set table name in both forms
        const tableNameInputs = this.sidebarHtml.querySelectorAll('.sync-table-name');
        tableNameInputs.forEach(input => {
            if (data.table_name) input.value = data.table_name;
        });
        
        // Fill other data
        for (const key in data) {
            if (data.hasOwnProperty(key)) {
                const inputElement = this.sidebarHtml.querySelector(`#${key}`);
                if (inputElement) {
                    inputElement.value = data[key];
                } else {
                    console.warn(`Element with id ${key} not found in the form.`);
                }
            }
        }
    }

    switchTab(evt, tabId) {
        const tabContents = this.sidebarHtml.querySelectorAll(".tab-content");
        tabContents.forEach(function(tab) {
            tab.classList.remove("active");
        });
        
        const tabButtons = this.sidebarHtml.querySelectorAll(".tab-button");
        tabButtons.forEach(function(btn) {
            btn.classList.remove("active");
        });
        
        this.sidebarHtml.querySelector(`#${tabId}`).classList.add("active");
        evt.currentTarget.classList.add("active");
        
        this.syncFormValues();
    }

    syncFormValues() {
        // Sync hidden input values between forms
        const basicForm = this.sidebarHtml.querySelector('#basic-tab form');
        const advancedForm = this.sidebarHtml.querySelector('#advanced-tab form');
        
        if (basicForm && advancedForm) {
            const hiddenInputs = ['action_name', 'project_dir', 'table_name'];
            hiddenInputs.forEach(name => {
                const basicInput = basicForm.querySelector(`input[name="${name}"]`);
                const advancedInput = advancedForm.querySelector(`input[name="${name}"]`);
                if (basicInput && advancedInput) {
                    advancedInput.value = basicInput.value;
                }
            });
        }
    }
}
