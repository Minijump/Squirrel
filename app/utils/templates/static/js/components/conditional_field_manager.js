/**
 * ConditionalFieldManager handles conditional visibility of form fields
 * based on select element values, providing a more robust and flexible
 * alternative to the simple toggleSelect function.
 */
export class ConditionalFieldManager {
    constructor(container) {
        this.container = container;
        this.conditionalElements = new Map(); // Map select -> conditional elements
        this.init();
    }

    init() {
        // Find all select elements that have onchange with conditional logic
        const selectElements = this.container.querySelectorAll('select[onchange*="toggleConditionalFields"], select[data-conditional="true"]');
        
        selectElements.forEach(select => {
            this.setupConditionalLogic(select);
        });

        // Also find elements with select_onchange class for backward compatibility
        this.setupLegacyConditionalLogic();
    }

    setupConditionalLogic(selectElement) {
        // Find all elements that should be conditionally shown/hidden based on this select
        const conditionalElements = this.container.querySelectorAll('.conditional-field');
        const selectName = selectElement.name || selectElement.id;
        
        const relevantElements = Array.from(conditionalElements).filter(elem => {
            return elem.dataset.showWhen === selectName || 
                   elem.dataset.hideWhen === selectName;
        });

        if (relevantElements.length > 0) {
            this.conditionalElements.set(selectElement, relevantElements);
            
            // Add event listener
            selectElement.addEventListener('change', () => {
                this.updateConditionalFields(selectElement);
            });

            // Trigger initial update
            this.updateConditionalFields(selectElement);
        }
    }

    setupLegacyConditionalLogic() {
        // Support for the old select_onchange system for backward compatibility
        const selectElements = this.container.querySelectorAll('select');
        
        selectElements.forEach(select => {
            const conditionalElements = this.container.querySelectorAll('.select-onchange');
            
            if (conditionalElements.length > 0) {
                // Add event listener if not already added
                if (!this.conditionalElements.has(select)) {
                    select.addEventListener('change', () => {
                        this.updateLegacyConditionalFields(select);
                    });
                }
            }
        });
    }

    updateConditionalFields(selectElement) {
        const conditionalElements = this.conditionalElements.get(selectElement);
        const selectedValue = selectElement.value;

        conditionalElements.forEach(element => {
            const showWhen = element.dataset.showWhen;
            const hideWhen = element.dataset.hideWhen;
            const showValues = element.dataset.showValues ? element.dataset.showValues.split(',') : [];
            const hideValues = element.dataset.hideValues ? element.dataset.hideValues.split(',') : [];

            let shouldShow = true;

            if (showWhen && showValues.length > 0) {
                shouldShow = showValues.includes(selectedValue);
            } else if (hideWhen && hideValues.length > 0) {
                shouldShow = !hideValues.includes(selectedValue);
            }

            this.setElementVisibility(element, shouldShow);
        });
    }

    updateLegacyConditionalFields(selectElement) {
        const conditionalElements = this.container.querySelectorAll('.select-onchange');
        
        conditionalElements.forEach(element => {
            const classList = Array.from(element.classList);
            let shouldShow = false;
            
            classList.forEach(className => {
                if (className === 'select-onchange') return; // Skip the base class
                if (className === selectElement.value) {
                    shouldShow = true;
                }
            });
            
            this.setElementVisibility(element, shouldShow);
        });
    }

    setElementVisibility(element, visible) {
        element.style.display = visible ? 'block' : 'none';
        
        // Update required attribute for inputs inside the element
        const inputs = element.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            if (visible) {
                // Restore original required state
                if (input.dataset.originalRequired === 'true') {
                    input.required = true;
                }
            } else {
                // Store original required state and set to false
                input.dataset.originalRequired = input.required.toString();
                input.required = false;
            }
        });
    }

    /**
     * Manually trigger update for all conditional fields
     */
    updateAll() {
        this.conditionalElements.forEach((elements, select) => {
            this.updateConditionalFields(select);
        });
        
        // Also update legacy conditional fields
        const selectElements = this.container.querySelectorAll('select');
        selectElements.forEach(select => {
            this.updateLegacyConditionalFields(select);
        });
    }

    /**
     * Add a new conditional relationship
     * @param {HTMLSelectElement} selectElement - The select element that controls visibility
     * @param {HTMLElement} targetElement - The element to show/hide
     * @param {string|string[]} showValues - Values that should show the target element
     */
    addConditionalField(selectElement, targetElement, showValues) {
        if (typeof showValues === 'string') {
            showValues = [showValues];
        }
        
        targetElement.dataset.showValues = showValues.join(',');
        targetElement.classList.add('conditional-field');
        
        if (!this.conditionalElements.has(selectElement)) {
            this.conditionalElements.set(selectElement, []);
            selectElement.addEventListener('change', () => {
                this.updateConditionalFields(selectElement);
            });
        }
        
        this.conditionalElements.get(selectElement).push(targetElement);
        this.updateConditionalFields(selectElement);
    }
}
