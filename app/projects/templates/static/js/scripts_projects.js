import { Modal } from '/static/base/js/components/modal.js';


document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('click', function() {
        if (card.classList.contains('card-new')) {
            const modal = new Modal({
                title: 'Create New Project',
                content: document.querySelector('#createProjectModalForm').outerHTML,
            });

            modal.open();
            return;
        }
        const projectDir = this.getAttribute('data-project-dir');
        window.location.href = `/projects/open/?project_dir=${encodeURIComponent(projectDir)}`;
    });
});
