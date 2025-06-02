// Main JavaScript for Mengtumbas Online Store

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    initializeCartFunctionality();
    initializeSearchFunctionality();
    initializeFormValidation();
    initializeImageGallery();
    initializeNotifications();
    initializeWishlistFunctionality();
}

// Get CSRF token from cookies or from the hidden input
function getCsrfToken() {
    // First try to get from the hidden input
    const tokenElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (tokenElement) {
        return tokenElement.value;
    }
    
    // Fall back to cookie
    return getCookie('csrftoken');
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Cart Functionality
function initializeCartFunctionality() {
    // Initialize cart notification popup event listeners
    if (document.getElementById('cartNotificationPopup')) {
        // Add event listener to the close button
        document.getElementById('closeCartPopup').addEventListener('click', function() {
            document.getElementById('cartNotificationPopup').classList.add('hidden');
        });
        
        // Close when clicking on the overlay
        document.getElementById('popupOverlay').addEventListener('click', function() {
            document.getElementById('cartNotificationPopup').classList.add('hidden');
        });
        
        // Close on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !document.getElementById('cartNotificationPopup').classList.contains('hidden')) {
                document.getElementById('cartNotificationPopup').classList.add('hidden');
            }
        });
    }

    // Add to cart with animation
    window.addToCart = function(productId, quantity = 1) {
        const csrfToken = getCsrfToken();
        
        if (!csrfToken) {
            console.error('CSRF token not found');
            showNotification('Error: CSRF token not found', 'error');
            return;
        }
        
        // Show loading state
        const loadingNotification = showNotification('Menambahkan produk ke keranjang...', 'info', 100000);
        
        fetch(`/add-to-cart/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'quantity': quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading notification
            if (loadingNotification && loadingNotification.parentNode) {
                loadingNotification.remove();
            }
            
            if (data.success) {
                // Update cart count if available
                if (document.getElementById('cart-count')) {
                    document.getElementById('cart-count').textContent = data.cart_count;
                }
                
                // Show success message
                showNotification('Produk berhasil ditambahkan ke keranjang', 'success');
                
                // Animate cart icon
                animateCartIcon();
            } else {
                showNotification(data.message || 'Gagal menambahkan produk ke keranjang', 'error');
            }
        })
        .catch(error => {
            // Remove loading notification
            if (loadingNotification && loadingNotification.parentNode) {
                loadingNotification.remove();
            }
            
            console.error('Error:', error);
            showNotification('Terjadi kesalahan. Silakan coba lagi.', 'error');
        });
    };
    
    // Update cart item quantity
    window.updateCartQuantity = function(itemId, quantity) {
        const csrfToken = getCsrfToken();
        
        if (!csrfToken) {
            console.error('CSRF token not found');
            showNotification('Error: CSRF token not found', 'error');
            return;
        }
        
        fetch(`/update-cart-item/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'quantity': quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                showNotification(data.error || 'Error updating cart', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('An error occurred. Please try again.', 'error');
        });
    };
}

// Wishlist Functionality
function initializeWishlistFunctionality() {
    // Toggle wishlist function
    window.toggleWishlist = function(productId, buttonElement) {
        const csrfToken = getCsrfToken();
        
        if (!csrfToken) {
            console.error('CSRF token not found');
            showNotification('Error: CSRF token not found', 'error');
            return;
        }
        
        // Show visual feedback immediately
        const icon = buttonElement.querySelector('.wishlist-icon');
        const isInWishlist = buttonElement.getAttribute('data-in-wishlist') === 'true';
        
        // Optimistic UI update
        if (isInWishlist) {
            icon.classList.replace('fas', 'far');
        } else {
            icon.classList.replace('far', 'fas');
        }
        
        // Show loading state
        const loadingNotification = showNotification('Memperbarui wishlist...', 'info', 100000);
        
        const url = isInWishlist ? 
            `/remove-from-wishlist/${productId}/` : 
            `/add-to-wishlist/${productId}/`;
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading notification
            if (loadingNotification && loadingNotification.parentNode) {
                loadingNotification.remove();
            }
            
            if (data.success) {
                // Update button state
                if (isInWishlist) {
                    buttonElement.setAttribute('data-in-wishlist', 'false');
                    showNotification('Produk dihapus dari wishlist', 'success');
                } else {
                    buttonElement.setAttribute('data-in-wishlist', 'true');
                    showNotification('Produk ditambahkan ke wishlist', 'success');
                }
                
                // Update wishlist count if exists
                if (document.getElementById('wishlist-count')) {
                    document.getElementById('wishlist-count').textContent = data.wishlist_count;
                }
            } else {
                // Revert the icon if there was an error
                if (isInWishlist) {
                    icon.classList.replace('far', 'fas');
                } else {
                    icon.classList.replace('fas', 'far');
                }
                
                showNotification(data.message || 'Gagal memperbarui wishlist', 'error');
            }
        })
        .catch(error => {
            // Remove loading notification
            if (loadingNotification && loadingNotification.parentNode) {
                loadingNotification.remove();
            }
            
            // Revert the icon if there was an error
            if (isInWishlist) {
                icon.classList.replace('far', 'fas');
            } else {
                icon.classList.replace('fas', 'far');
            }
            
            console.error('Error:', error);
            showNotification('Terjadi kesalahan. Silakan coba lagi.', 'error');
        });
    };
}

// Search Functionality
function initializeSearchFunctionality() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    fetchSearchSuggestions(query);
                }, 300);
            } else {
                hideSearchSuggestions();
            }
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.search-container')) {
                hideSearchSuggestions();
            }
        });
    }
}

function fetchSearchSuggestions(query) {
    fetch(`/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.suggestions && data.suggestions.length > 0) {
                showSearchSuggestions(data.suggestions);
            } else {
                hideSearchSuggestions();
            }
        })
        .catch(error => {
            console.error('Search error:', error);
            hideSearchSuggestions();
        });
}

function showSearchSuggestions(suggestions) {
    let suggestionsContainer = document.getElementById('search-suggestions');
    if (!suggestionsContainer) {
        suggestionsContainer = document.createElement('div');
        suggestionsContainer.id = 'search-suggestions';
        suggestionsContainer.className = 'search-suggestions';
        document.querySelector('.search-container').appendChild(suggestionsContainer);
    }
    
    suggestionsContainer.innerHTML = suggestions.map(item => `
        <div class="search-suggestion-item" onclick="selectSuggestion('${item.name}')">
            <div class="flex items-center space-x-3">
                <img src="${item.image || '/static/images/no-image.png'}" alt="${item.name}" class="w-8 h-8 rounded">
                <div>
                    <div class="font-medium">${item.name}</div>
                    <div class="text-sm text-gray-700">$${item.price}</div>
                </div>
            </div>
        </div>
    `).join('');
    
    suggestionsContainer.style.display = 'block';
}

function hideSearchSuggestions() {
    const suggestionsContainer = document.getElementById('search-suggestions');
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
    }
}

function selectSuggestion(productName) {
    document.getElementById('search-input').value = productName;
    hideSearchSuggestions();
    document.getElementById('search-form').submit();
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Email validation
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    field.classList.add('border-red-500');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'text-red-500 text-sm mt-1 field-error';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('border-red-500');
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Image Gallery
function initializeImageGallery() {
    const productImages = document.querySelectorAll('.product-image');
    productImages.forEach(img => {
        img.addEventListener('click', function() {
            openImageModal(this.src, this.alt);
        });
    });
}

function openImageModal(src, alt) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="max-w-4xl max-h-full p-4">
            <img src="${src}" alt="${alt}" class="max-w-full max-h-full object-contain">
            <button onclick="this.parentElement.parentElement.remove()" 
                    class="absolute top-4 right-4 text-white text-2xl">×</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Notifications
function initializeNotifications() {
    // Create notification container if it doesn't exist
    if (!document.getElementById('notification-container')) {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'fixed top-4 right-4 z-50 space-y-2';
        document.body.appendChild(container);
    }
}

function showNotification(message, type = 'info', duration = 3000) {
    // Make sure container exists
    if (!document.getElementById('notification-container')) {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'fixed top-4 right-4 z-50 space-y-2';
        document.body.appendChild(container);
    }
    
    const container = document.getElementById('notification-container');
    const notification = document.createElement('div');
    
    const typeClasses = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        warning: 'bg-yellow-500 text-black',
        info: 'bg-blue-500 text-white'
    };
    
    notification.className = `px-6 py-3 rounded-lg shadow-lg ${typeClasses[type]} fade-in`;
    notification.style.cssText = 'opacity: 1; transition: opacity 0.3s ease;';
    notification.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex items-center">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle'} mr-2"></i>
                <span>${message}</span>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-lg">&times;</button>
        </div>
    `;
    
    container.appendChild(notification);
    
    // Auto remove after duration (if not a loading notification)
    if (duration !== 100000) {
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.opacity = '0';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        }, duration);
    }
    
    return notification;
}

// Cart Animation
function animateCartIcon() {
    const cartIcon = document.querySelector('.cart-icon');
    if (cartIcon) {
        cartIcon.classList.add('animate-bounce');
        setTimeout(() => {
            cartIcon.classList.remove('animate-bounce');
        }, 600);
    }
}

function updateCartBadge(count) {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        badge.textContent = count;
        if (count > 0) {
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Utility Functions
function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(price);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Loading States
function showLoading(element) {
    const originalContent = element.innerHTML;
    element.innerHTML = '<div class="loading-spinner"></div>';
    element.dataset.originalContent = originalContent;
    element.disabled = true;
}

function hideLoading(element) {
    if (element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        delete element.dataset.originalContent;
    }
    element.disabled = false;
}

// Smooth Scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Mobile menu handling moved to mobile.js
