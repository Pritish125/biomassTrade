// Main JavaScript file for Biomass Pellet Trading Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete-confirm');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Confirm offer response actions
    const offerResponseButtons = document.querySelectorAll('.btn-offer-response');
    offerResponseButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const action = this.getAttribute('data-action');
            const message = action === 'accept' 
                ? 'Are you sure you want to accept this offer? This will create an order automatically.' 
                : 'Are you sure you want to reject this offer?';
                
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Confirm order cancellation
    const cancelOrderButtons = document.querySelectorAll('.btn-cancel-order');
    cancelOrderButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to cancel this order?')) {
                e.preventDefault();
            }
        });
    });
    
    // Filter listings by biomass type
    const biomassTypeFilter = document.getElementById('biomassTypeFilter');
    if (biomassTypeFilter) {
        biomassTypeFilter.addEventListener('change', function() {
            const selectedType = this.value;
            const listingCards = document.querySelectorAll('.listing-card');
            
            listingCards.forEach(card => {
                const cardType = card.getAttribute('data-biomass-type');
                if (selectedType === 'all' || cardType === selectedType) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // Real-time calculation for total price in order forms
    const quantityInput = document.getElementById('quantity');
    const totalPriceDisplay = document.getElementById('totalPriceDisplay');
    const pricePerTonField = document.getElementById('pricePerTon');
    
    if (quantityInput && totalPriceDisplay && pricePerTonField) {
        // Function to update total price
        const updateTotalPrice = () => {
            const quantity = parseFloat(quantityInput.value) || 0;
            const pricePerTon = parseFloat(pricePerTonField.value) || 0;
            const totalPrice = (quantity * pricePerTon).toFixed(2);
            totalPriceDisplay.textContent = `$${totalPrice}`;
        };
        
        // Add event listeners for input changes
        quantityInput.addEventListener('input', updateTotalPrice);
        pricePerTonField.addEventListener('input', updateTotalPrice);
        
        // Initial calculation
        updateTotalPrice();
    }
});
