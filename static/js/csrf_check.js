// CSRF token check
document.addEventListener('DOMContentLoaded', function() {
    console.log('CSRF token check script loaded');
    
    // Function to get CSRF token
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
    
    const csrfToken = getCookie('csrftoken');
    console.log('CSRF token:', csrfToken);
    
    // Check if the addToCart function exists
    if (typeof window.addToCart === 'function') {
        console.log('addToCart function exists');
    } else {
        console.log('addToCart function does not exist');
    }
    
    // Check if the toggleWishlist function exists
    if (typeof window.toggleWishlist === 'function') {
        console.log('toggleWishlist function exists');
    } else {
        console.log('toggleWishlist function does not exist');
    }
}); 