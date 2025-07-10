// Auto-detect if we're on a project page and add the collapsible class (excepted in test mode)
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're in test mode
    const isTestMode = window.isTestMode || 
                      window.navigator.webdriver || 
                      document.documentElement.getAttribute('webdriver') !== null ||
                      window.location.search.includes('test_mode=true');
    // Skip foldable navbar if in test mode
    if (isTestMode) return;
    
    const urlParams = new URLSearchParams(window.location.search);
    const isProjectPage = urlParams.has('project_dir') || window.location.pathname.includes('/project/');
    if (isProjectPage) document.body.classList.add('project-page');
});
