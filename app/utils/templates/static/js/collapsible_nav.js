// Auto-detect if we're on a project page and add the collapsible class
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const isProjectPage = urlParams.has('project_dir') || window.location.pathname.includes('/project/');
    if (isProjectPage) document.body.classList.add('project-page');
});
