document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.clickable').forEach(function(li) {
        li.addEventListener('click', function() {
            window.location.href = li.querySelector('a').href;
        });
    });
});

function openForm(id) {
    document.getElementById(id).style.width = "250px";
}
function openActionForm(id, name) {
    var form = document.getElementById(id);
    form.style.width = "250px";
    form.querySelector('input[name="table_name"]').value = name;
}
function closeForm(id) {
    document.getElementById(id).style.width = "0";
}

function openModal(formId) {
    document.getElementById(formId).style.display = "block";
}

function closeModal(formId) {
    document.getElementById(formId).style.display = "none";
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

function editPipelineActionOpenModal(action_id, action_name, action_code, project_dir) {
    const modal = document.getElementById('EditActionModal');
    modal.style.display = "block";
    document.getElementById('modal-action-name').textContent = action_name;
    modal.querySelector('input[name="action_id"]').value = action_id;
    modal.querySelector('textarea[name="action_code"]').value = action_code;
    modal.querySelector('input[name="project_dir"]').value = project_dir;
}
