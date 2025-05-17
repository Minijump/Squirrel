// Project card click (open selected project)
const createProjectModal = document.getElementById('createProjectModal');
document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('click', function() {
        if (card.classList.contains('card-new')) {
            createProjectModal.style.display = 'flex';
            return;
        }
        const projectDir = this.getAttribute('data-project-dir');
        window.location.href = `/projects/open/?project_dir=${encodeURIComponent(projectDir)}`;
    });
});

// Close the create project modal
const cancelButton = document.getElementById('cancelButton');
cancelButton.addEventListener('click', () => {
    createProjectModal.style.display = 'none';
});
