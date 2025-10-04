import { Field } from '/static/utils/components/field/field.js';


async function getSourceTypeSpecificArgs(sourceType) {
    const response = await fetch(`/data_sources/get_source_settings_specific_args/${sourceType}/`);
    return response.json();
}

async function generateAdditionalArgs(sourceType) {
    const specificSourceArgs = await getSourceTypeSpecificArgs(sourceType.value);
    const sourceTypeSpecificArgsDiv = document.querySelector('#sourceSettingsAdditionalArgsDiv');
    const sourceDataStr = sourceTypeSpecificArgsDiv.dataset.source;
    const sourceData = sourceDataStr ? JSON.parse(sourceDataStr) : {};
    
    sourceTypeSpecificArgsDiv.innerHTML = '';
    Object.keys(specificSourceArgs).forEach(key => {
        const defaultValue = sourceData[key];
        const input = new Field(key, specificSourceArgs[key], defaultValue);
        input.inputDivHTML.classList.add('setting-item');
        sourceTypeSpecificArgsDiv.appendChild(input.inputDivHTML);
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    const sourceType = document.querySelector('#sourceType');
    await generateAdditionalArgs(sourceType);
});
