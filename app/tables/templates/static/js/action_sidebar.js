import { FormSidebar } from '/static/base/js/components/sidebar.js';
import { Field } from '/static/base/js/components/field.js';
import { ConditionalFieldManager } from '/static/base/js/components/conditional_field_manager.js';
import { SquirrelDictionary } from '/static/base/js/widgets/dictionary_widget.js';

export class ActionSidebar extends FormSidebar {
    constructor(options = {}) {
        options.width = options.width || '320px';
        options.hasOverlay = options.hasOverlay !== false;
        super(options);
        
        this.actionName = options.actionName || '';
        this.actionData = options.actionData || {};
        this.projectDir = options.projectDir || new URLSearchParams(window.location.search).get('project_dir');
        this.hasAdvancedTab = false;
        this.conditionalManager = null;
        
        // Remove the default form content and create tabs
        this.createTabbedContent();
    }

    createContent() {
        // Return a plain div that will be added directly to the sidebar
        const content = document.createElement('div');
        return content;
    }

    createTabbedContent() {
        const sidebarContent = this.sidebarHtml.querySelector('div');
        sidebarContent.innerHTML = '';

        // Create tabs
        const tabsContainer = document.createElement('div');
        tabsContainer.className = 'sidebar-tabs';
        
        const basicTab = document.createElement('button');
        basicTab.className = 'tab-button active n-l-border n-r-border';
        basicTab.textContent = 'Basic';
        basicTab.onclick = (evt) => this.switchTab(evt, 'basic-tab');
        
        const advancedTab = document.createElement('button');
        advancedTab.id = 'kwargs-btn';
        advancedTab.className = 'tab-button n-r-border';
        advancedTab.textContent = 'Advanced';
        advancedTab.style.display = 'none'; // Hidden by default
        advancedTab.onclick = (evt) => this.switchTab(evt, 'advanced-tab');
        
        tabsContainer.appendChild(basicTab);
        tabsContainer.appendChild(advancedTab);
        sidebarContent.appendChild(tabsContainer);

        // Create basic tab content
        const basicTabContent = document.createElement('div');
        basicTabContent.id = 'basic-tab';
        basicTabContent.className = 'tab-content active';
        
        const basicForm = document.createElement('form');
        basicForm.action = '/tables/execute_action/';
        basicForm.method = 'post';
        basicForm.className = 'std-form';
        
        // Hidden inputs
        const actionNameInput = document.createElement('input');
        actionNameInput.type = 'hidden';
        actionNameInput.name = 'action_name';
        actionNameInput.className = 'sync-action-name';
        actionNameInput.required = true;
        
        const projectDirInput = document.createElement('input');
        projectDirInput.type = 'hidden';
        projectDirInput.name = 'project_dir';
        projectDirInput.value = this.projectDir;
        
        const tableNameInput = document.createElement('input');
        tableNameInput.type = 'hidden';
        tableNameInput.name = 'table_name';
        tableNameInput.id = 'table_name';
        tableNameInput.className = 'sync-table-name';
        tableNameInput.required = true;
        
        const argsDiv = document.createElement('div');
        argsDiv.id = 'args';
        
        const submitBtn = document.createElement('button');
        submitBtn.type = 'submit';
        submitBtn.className = 'btn-primary';
        submitBtn.textContent = 'Confirm';
        submitBtn.style.marginTop = '10px';
        
        basicForm.appendChild(actionNameInput);
        basicForm.appendChild(projectDirInput);
        basicForm.appendChild(tableNameInput);
        basicForm.appendChild(argsDiv);
        basicForm.appendChild(submitBtn);
        
        basicTabContent.appendChild(basicForm);
        sidebarContent.appendChild(basicTabContent);

        // Create advanced tab content
        const advancedTabContent = document.createElement('div');
        advancedTabContent.id = 'advanced-tab';
        advancedTabContent.className = 'tab-content';
        
        const advancedForm = document.createElement('form');
        advancedForm.action = '/tables/execute_action/';
        advancedForm.method = 'post';
        advancedForm.id = 'args-kwargs-form';
        advancedForm.className = 'std-form';
        
        // Hidden inputs for advanced form
        const advActionNameInput = actionNameInput.cloneNode();
        advActionNameInput.className = 'sync-action-name';
        
        const advProjectDirInput = projectDirInput.cloneNode();
        
        const advTableNameInput = tableNameInput.cloneNode();
        advTableNameInput.className = 'sync-table-name';
        
        const colNameInput = document.createElement('input');
        colNameInput.type = 'hidden';
        colNameInput.name = 'col_name';
        colNameInput.id = 'col_name';
        colNameInput.required = true;
        
        const colIdxInput = document.createElement('input');
        colIdxInput.type = 'hidden';
        colIdxInput.name = 'col_idx';
        colIdxInput.id = 'col_idx';
        colIdxInput.required = true;
        
        const advancedInput = document.createElement('input');
        advancedInput.type = 'hidden';
        advancedInput.name = 'advanced';
        advancedInput.value = 'true';
        
        const argsKwargsDiv = document.createElement('div');
        argsKwargsDiv.id = 'args-kwargs';
        argsKwargsDiv.style.paddingLeft = '8px';
        
        const advSubmitBtn = submitBtn.cloneNode(true);
        
        advancedForm.appendChild(advActionNameInput);
        advancedForm.appendChild(advProjectDirInput);
        advancedForm.appendChild(advTableNameInput);
        advancedForm.appendChild(colNameInput);
        advancedForm.appendChild(colIdxInput);
        advancedForm.appendChild(advancedInput);
        advancedForm.appendChild(argsKwargsDiv);
        advancedForm.appendChild(advSubmitBtn);
        
        advancedTabContent.appendChild(advancedForm);
        sidebarContent.appendChild(advancedTabContent);
    }

    open() {
        super.open();
        
        // Store reference to sidebar instance for external access
        if (this.sidebarHtml) {
            this.sidebarHtml.sidebarInstance = this;
        }
    }

    async openForAction(actionName, data = {}) {
        this.actionName = actionName;
        this.actionData = data;
        
        await this.addInputs();
        await this.addKwargs();
        this.completeInputs(data);
        
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
                this.hasAdvancedTab = false;
                return;
            }
            
            kwargsForm.style.display = 'block';
            kwargsBtn.style.display = 'block';
            this.hasAdvancedTab = true;
            
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

    /**
     * Legacy method for backward compatibility - now delegates to ConditionalFieldManager
     */
    toggleSelect() {
        if (this.conditionalManager) {
            this.conditionalManager.updateAll();
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

    defaultFocus() {
        // Focus on first visible input in active tab
        const activeTab = this.sidebarHtml.querySelector('.tab-content.active');
        if (activeTab) {
            Array.from(activeTab.querySelectorAll('input, textarea, select'))
                .find(input => input.offsetParent !== null && !input.disabled && input.type !== 'hidden')
                ?.focus();
        }
    }
}
