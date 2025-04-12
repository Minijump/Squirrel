function editPipelineActionOpenModal(action_id, action_name, action_code, project_dir) {
    const modal = document.getElementById('editActionModal');
    modal.style.display = "flex";
    document.getElementById('modal-action-name').textContent = action_name;
    modal.querySelector('input[name="project_dir"]').value = project_dir;
    modal.querySelector('input[name="action_id"]').value = action_id;
    modal.querySelector('textarea[name="action_code"]').value = action_code;

    const cancelButton = modal.querySelector('#cancelButton');
    cancelButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });
}

function deletePipelineAction(action_id, project_dir) {
    const url = new URL('/pipeline/delete_action', window.location.origin);
    url.searchParams.append('project_dir', project_dir);
    url.searchParams.append('delete_action_id', action_id);
    fetch(url, {
        method: 'POST',
    })
    .then(response => {
        if (response.ok) {
            window.location.href = `/pipeline/?project_dir=${project_dir}`;
        } else {
            console.error('Error:', response.statusText);
        }
    })
    .catch((error) => {
        console.error('Error', error);
    });
}

function getOrder() {
    // Get and returns the order of the items
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
    console.log("order", order)
    console.log("sorted", sorted)
    if (JSON.stringify(order) === JSON.stringify(sorted)) {
        document.getElementById('save-order').style.visibility = "hidden";
    } else{
        document.getElementById('save-order').style.visibility = "visible";
    }
}

function confirmNewOrder(project_dir) {
    // Call endpoint to edit pipeline with the new order
    const order = getOrder()
    const url = new URL('/pipeline/confirm_new_order', window.location.origin);
    url.searchParams.append('project_dir', project_dir);
    url.searchParams.append('order', order);
    fetch(url, {
        method: 'POST',
    })
    .then(response => {
        if (response.ok) {
            window.location.href = `/pipeline/?project_dir=${project_dir}`;
        } else {
            console.error('Error:', response.statusText);
        }
    })
}

document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.dragndrop')
    const swapy = Swapy.createSwapy(container, {
        animation: 'dynamic',
    })
    swapy.enable(true)

    swapy.onSwap((event) => {
        console.log("event", event)
        saveNewOrderVisibility()
        })
});
