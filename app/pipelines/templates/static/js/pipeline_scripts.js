import { EditActionModal } from './edit_action_modal.js';

function editPipelineActionOpenModal(action_id) {
    const actionModal = new EditActionModal(action_id);
    actionModal.open();
}

function getOrder() {
    const container = document.getElementById('pipeline');
    const items = container.querySelectorAll('[data-swapy-item]');
    const order = Array.from(items).map(item => item.getAttribute('data-swapy-item'));
    return order;
}

function saveNewOrderVisibility() {
    // Set visibility of save button
    // each element has name: 'id-item', starting with 0
    const order = getOrder()
    // Sort numerically by extracting and comparing the numeric part
    const sorted = [...order].sort((a, b) => {
        const numA = parseInt(a.split('-')[0], 10);
        const numB = parseInt(b.split('-')[0], 10);
        return numA - numB;
    });
    if (JSON.stringify(order) === JSON.stringify(sorted)) {
        document.getElementById('save-order').style.visibility = "hidden";
    } else{
        document.getElementById('save-order').style.visibility = "visible";
    }
}

function confirmNewOrder(project_dir) {
    const order = getOrder()
    const url = new URL('/pipeline/confirm_new_order', window.location.origin);
    url.searchParams.append('project_dir', project_dir);
    url.searchParams.append('order', order);
    fetch(url, {
        method: 'POST',
    })
    .then(async response => {
        await window.handleRedirectNotification(response);
        window.location.href = `/pipeline/?project_dir=${project_dir}`;
    })
}

document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.dragndrop')
    const swapy = Swapy.createSwapy(container, {
        animation: 'dynamic',
    })
    swapy.enable(true)

    swapy.onSwap((event) => {
        saveNewOrderVisibility()
    })
});


window.editPipelineActionOpenModal = editPipelineActionOpenModal;
window.confirmNewOrder = confirmNewOrder;
