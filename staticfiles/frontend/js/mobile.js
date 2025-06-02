document.addEventListener('DOMContentLoaded', () => {
    // Mobile menu elements
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const closeMobileMenu = document.getElementById('closeMobileMenu');
    const mobileMenuContent = mobileMenu.querySelector('div:first-child');
    
    // Show mobile menu
    mobileMenuToggle.addEventListener('click', () => {
        document.body.style.overflow = 'hidden';
        mobileMenu.classList.remove('hidden');
        requestAnimationFrame(() => {
            mobileMenuContent.style.transform = 'translateX(0)';
        });
    });
    
    // Hide mobile menu
    function closeMobileMenuHandler() {
        mobileMenuContent.style.transform = 'translateX(-100%)';
        document.body.style.overflow = '';
        setTimeout(() => {
            mobileMenu.classList.add('hidden');
        }, 300);
    }
    
    closeMobileMenu.addEventListener('click', closeMobileMenuHandler);
    
    // Close menu when clicking outside
    mobileMenu.addEventListener('click', (e) => {
        if (e.target === mobileMenu) {
            closeMobileMenuHandler();
        }
    });

    // Close menu on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !mobileMenu.classList.contains('hidden')) {
            closeMobileMenuHandler();
        }
    });
});