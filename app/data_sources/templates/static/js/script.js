import { openCreateSourcetModal} from './create_source_modal.js';


async function onSourceCardClick(card) {
     if (card.classList.contains('card-new')) {
        openCreateSourcetModal();
        return;
    }
    const projectDir = card.getAttribute('data-project-dir');
    const sourceDir = card.getAttribute('data-source-dir');
    window.location.href = `/source/settings/?project_dir=${encodeURIComponent(projectDir)}&source_dir=${encodeURIComponent(sourceDir)}`;
}

function syncSource(sourceDir, projectDir, syncIconId) {
    return new Promise((resolve, reject) => {
        console.log(`Starting sync for source: ${sourceDir}`);
        const url = new URL('/source/sync', window.location.origin);
        const formData = new FormData();
        formData.append('project_dir', projectDir);
        formData.append('source_dir', sourceDir);

        const syncIcon = document.getElementById(syncIconId);
        syncIcon.classList.remove('fa-sync-alt');
        syncIcon.classList.add('fa-spinner', 'fa-spin');

        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                syncIcon.classList.remove('fa-spinner', 'fa-spin');
                syncIcon.classList.add('fa-check');
                console.log(`Completed sync for source: ${sourceDir}`);
                resolve();
                location.reload();
            } else {
                syncIcon.classList.remove('fa-spinner', 'fa-spin');
                syncIcon.classList.add('fa-times');
                reject(`Error syncing source: ${response.status} ${response.statusText}`);
            }
        })
        .catch(error => {
            syncIcon.classList.remove('fa-spinner', 'fa-spin');
            syncIcon.classList.add('fa-times');
            reject(error);
        });
    });
}

function syncAllSources(projectDir) {
    const syncAllButton = document.getElementById('syncAllSourcesButton');
    syncAllButton.disabled = true;
    syncAllButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Syncing...';

    const sourceCards = document.querySelectorAll('.card');
    const syncPromises = [];

    sourceCards.forEach(card => {
        const sourceDir = card.getAttribute('data-source-dir');
        const syncButton = card.querySelector('.card-sync-btn');
        if (syncButton) {
            syncAllButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Syncing...';
            const syncIconId = syncButton.id;
            syncPromises.push(syncSource(sourceDir, projectDir, syncIconId));
        }
    });

    Promise.all(syncPromises)
        .then(() => {
            syncAllButton.disabled = false;
            syncAllButton.innerHTML = 'Sync All Sources';
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error syncing all sources');
            syncAllButton.disabled = false;
            syncAllButton.innerHTML = 'Sync All Sources';
        });
}


window.onSourceCardClick = onSourceCardClick;
window.syncSource = syncSource;
window.syncAllSources = syncAllSources;
