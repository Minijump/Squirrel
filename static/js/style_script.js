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

function closeForm(id) {
    document.getElementById(id).style.width = "0";
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
