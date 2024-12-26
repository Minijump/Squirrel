const projectModal = document.getElementById('projectModal');
const cancelButton = document.getElementById('cancelButton');

document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('click', function() {
        if (card.classList.contains('card-new')) {
            projectModal.style.display = 'flex';
            return;
        }
        const projectDir = this.getAttribute('data-project-dir');
        window.location.href = `/projects/open/?project_dir=${encodeURIComponent(projectDir)}`;
    });
});

cancelButton.addEventListener('click', () => {
    projectModal.style.display = 'none';
});
