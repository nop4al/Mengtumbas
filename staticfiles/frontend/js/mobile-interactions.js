// Mobile Menu Interactions
document.addEventListener('DOMContentLoaded', () => {
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const closeMobileMenu = document.getElementById('closeMobileMenu');
    const menuContent = mobileMenu?.querySelector('div');

    // Handle menu opening
    mobileMenuToggle?.addEventListener('click', () => {
        mobileMenu.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        
        // Animate menu sliding in
        requestAnimationFrame(() => {
            menuContent.style.transform = 'translateX(0)';
        });
    });

    // Handle menu closing
    const closeMenu = () => {
        menuContent.style.transform = 'translateX(-100%)';
        document.body.style.overflow = '';
        
        setTimeout(() => {
            mobileMenu.classList.add('hidden');
        }, 300);
    };

    closeMobileMenu?.addEventListener('click', closeMenu);
    mobileMenu?.addEventListener('click', (e) => {
        if (e.target === mobileMenu) {
            closeMenu();
        }
    });

    // Close menu on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !mobileMenu.classList.contains('hidden')) {
            closeMenu();
        }
    });

    // Handle smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                // Close mobile menu if open
                if (!mobileMenu.classList.contains('hidden')) {
                    closeMenu();
                }
            }
        });
    });

    // Enhanced touch feedback
    const touchElements = document.querySelectorAll('.touch-feedback');
    touchElements.forEach(element => {
        element.addEventListener('touchstart', () => {
            element.style.transform = 'scale(0.97)';
        });
        
        element.addEventListener('touchend', () => {
            element.style.transform = 'scale(1)';
        });
    });

    // Handle fixed header on scroll
    const header = document.querySelector('header');
    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll <= 0) {
            header.classList.remove('scroll-up');
            return;
        }
        
        if (currentScroll > lastScroll && !header.classList.contains('scroll-down')) {
            // Scrolling down
            header.classList.remove('scroll-up');
            header.classList.add('scroll-down');
        } else if (currentScroll < lastScroll && header.classList.contains('scroll-down')) {
            // Scrolling up
            header.classList.remove('scroll-down');
            header.classList.add('scroll-up');
        }
        
        lastScroll = currentScroll;
    });

    // Handle bottom navigation active states
    const navItems = document.querySelectorAll('.nav-item');
    const currentPath = window.location.pathname;

    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            item.classList.add('active');
        }
    });

    // Add pull-to-refresh functionality
    let touchStart = 0;
    let touchMove = 0;
    
    document.addEventListener('touchstart', (e) => {
        touchStart = e.touches[0].clientY;
    }, { passive: true });
    
    document.addEventListener('touchmove', (e) => {
        touchMove = e.touches[0].clientY;
        
        if (document.scrollingElement.scrollTop === 0 && touchMove > touchStart && (touchMove - touchStart) > 100) {
            // Show refresh indicator
            // Implement your refresh logic here
        }
    }, { passive: true });
});
