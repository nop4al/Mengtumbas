document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-input');
    const searchResults = document.querySelector('.search-results');
    let searchTimeout;

    if (searchInput && searchResults) {
        // Mobile search optimization
        searchInput.addEventListener('touchstart', function(e) {
            // Prevent zoom on iOS
            e.target.style.fontSize = '16px';
        });

        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();

            // Add loading state
            if (query.length > 0) {
                searchResults.innerHTML = `
                    <div class="p-4">
                        <div class="skeleton-loading h-12 mb-2"></div>
                        <div class="skeleton-loading h-12 mb-2"></div>
                        <div class="skeleton-loading h-12"></div>
                    </div>
                `;
            }

            // Debounce search to improve performance
            searchTimeout = setTimeout(() => {
                if (query.length > 0) {
                    fetch(`/search/?q=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            searchResults.innerHTML = '';
                            if (data.length > 0) {
                                data.forEach(product => {
                                    const productCard = document.createElement('div');
                                    productCard.className = 'search-result-item p-4 hover:bg-gray-50 flex items-center gap-4';
                                    productCard.innerHTML = `
                                        <img src="${product.image}" alt="${product.name}" 
                                             class="w-16 h-16 object-cover rounded-lg">
                                        <div class="flex-1 min-w-0">
                                            <h3 class="text-sm font-medium text-gray-900 truncate">
                                                ${product.name}
                                            </h3>
                                            <p class="text-sm text-green-600 font-semibold">
                                                Rp ${product.price}
                                            </p>
                                        </div>
                                    `;
                                    productCard.addEventListener('click', () => {
                                        window.location.href = product.url;
                                    });
                                    searchResults.appendChild(productCard);
                                });
                            } else {
                                searchResults.innerHTML = `                                    <div class="p-4 text-center text-gray-700">
                                        No products found
                                    </div>
                                `;
                            }
                        })
                        .catch(error => {
                            console.error('Search error:', error);
                            searchResults.innerHTML = `
                                <div class="p-4 text-center text-red-500">
                                    An error occurred while searching
                                </div>
                            `;
                        });
                } else {
                    searchResults.innerHTML = '';
                }
            }, 300);
        });

        // Close search results when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.innerHTML = '';
            }
        });

        // Handle touch events
        searchResults.addEventListener('touchstart', function(e) {
            if (e.target.closest('.search-result-item')) {
                e.target.closest('.search-result-item').style.backgroundColor = '#f3f4f6';
            }
        });

        searchResults.addEventListener('touchend', function(e) {
            if (e.target.closest('.search-result-item')) {
                e.target.closest('.search-result-item').style.backgroundColor = '';
            }
        });
    }
});