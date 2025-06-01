import { openCreateProjectModal } from './create_project_modal.js';

async function onProjectCardClick(card) {
     if (card.classList.contains('card-new')) {
        openCreateProjectModal();
        return;
    }
    const projectDir = card.getAttribute('data-project-dir');
    window.location.href = `/projects/open/?project_dir=${encodeURIComponent(projectDir)}`;
}

window.onProjectCardClick = onProjectCardClick;
