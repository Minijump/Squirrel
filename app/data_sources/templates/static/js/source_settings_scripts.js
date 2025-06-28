import { Field } from '/static/base/js/components/field.js';


async function getSourceTypeSpecificArgs(sourceType) {
    const response = await fetch(`/data_sources/get_source_settings_specific_args/${sourceType}/`);
    return response.json();
}

function fillInput(sourceTypeSpecificArgsDiv, key, input) {
    const sourceDataStr = sourceTypeSpecificArgsDiv.dataset.source;
    const sourceData = sourceDataStr ? JSON.parse(sourceDataStr) : {};
    if (sourceData[key] !== undefined) {
        const inputElement = input.inputDivHTML.querySelector('input, select, textarea');
        if (inputElement) {
            inputElement.value = sourceData[key];
        }
    }
}

async function generateAdditionalArgs(sourceType) {
    const specificSourceArgs = await getSourceTypeSpecificArgs(sourceType.value);
    const sourceTypeSpecificArgsDiv = document.querySelector('#sourceSettingsAdditionalArgsDiv');
    sourceTypeSpecificArgsDiv.innerHTML = '';
    Object.keys(specificSourceArgs).forEach(key => {
        const input = new Field(key, specificSourceArgs[key]);
        sourceTypeSpecificArgsDiv.appendChild(input.inputDivHTML);
        fillInput(sourceTypeSpecificArgsDiv, key, input);
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    const sourceType = document.querySelector('#sourceType');
    await generateAdditionalArgs(sourceType);
});
