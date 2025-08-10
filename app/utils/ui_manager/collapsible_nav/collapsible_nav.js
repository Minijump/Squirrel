function isTestMode() {
    const isTestMode = window.isTestMode || 
                      window.navigator.webdriver || 
                      document.documentElement.getAttribute('webdriver') !== null ||
                      window.location.search.includes('test_mode=true');
    return isTestMode;
}

function isProjectPage() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.has('project_dir') || window.location.pathname.includes('/project/');
}

// 'project-page' class is added via script tags inside template, to avoid glitches

// Add click handlers on navigation links to close sidebar before redirect
document.addEventListener('DOMContentLoaded', function() {
    if (isTestMode()) return;
    if (!isProjectPage()) return;
    
    const navLinks = document.querySelectorAll('.project-page aside nav ul li a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.href;
            
            const aside = document.querySelector('.project-page aside');
            if (aside) {
                aside.style.pointerEvents = 'none';
                aside.style.width = 'var(--nav-collapsed-width)';
                aside.style.padding = '2px';
                aside.style.paddingTop = '20px';
                aside.style.paddingLeft = '10px';
                aside.style.paddingRight = '10px';
                
                setTimeout(() => {
                    window.location.href = href;
                }, 300);
            } else {
                window.location.href = href;
            }
        });
    });
});
