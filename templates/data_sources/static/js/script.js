// Create source Modal
const createSourceModal = document.getElementById('createSourceModal');
const cancelButton = document.getElementById('cancelButton');

document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('click', function() {
        if (card.classList.contains('card-new')) {
            createSourceModal.style.display = 'flex';
            return;
        }
        // TODO: setting of the source
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