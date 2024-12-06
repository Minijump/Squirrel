// Create source Modal
const createSourceModal = document.getElementById('createSourceModal');
const cancelButton = document.getElementById('cancelButton');

document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('click', function() {
        if (card.classList.contains('card-new')) {
            createSourceModal.style.display = 'flex';
            return;
        }
        const projectDir = this.getAttribute('data-project-dir');
        const sourceDir = this.getAttribute('data-source-dir');
        window.location.href = `/source/settings/?project_dir=${encodeURIComponent(projectDir)}&source_dir=${encodeURIComponent(sourceDir)}`;
    });
});
cancelButton.addEventListener('click', () => {
    createSourceModal.style.display = 'none';
});

// Filter files type for file selection
function updateFileAccept() {
    const sourceType = document.getElementById('sourceType');
    const sourceFile = document.getElementById('sourceFile');
    const selectedType = sourceType.value;
    sourceFile.accept = `.${selectedType}`;
}
document.addEventListener('DOMContentLoaded', updateFileAccept);
document.getElementById('sourceType').addEventListener('change', updateFileAccept);

function syncSource(sourceDir, projectDir) {
    const url = new URL('/source/sync', window.location.origin);
    const formData = new FormData();
    formData.append('project_dir', projectDir);
    formData.append('source_dir', sourceDir);

    fetch(url, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            alert('Source synced successfully');
            location.reload();
        } else {
            alert('Error syncing source');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error syncing source');
    });
}
