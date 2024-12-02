function clearCart() {
    fetch('/clear_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update the cart UI to reflect the cleared cart
            updateCartUI({ items: [], total: 0.0 });
        } else {
            console.error('Failed to clear cart');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}