const orderButtons = document.querySelectorAll(".order-button");

orderButtons.forEach(button => {
    button.addEventListener("click", () => {
        const itemCard = button.closest(".item-card");
        const itemData = {
            id: itemCard.dataset.itemId,
            name: itemCard.dataset.itemName,
            category: itemCard.dataset.itemCategory,
            price: parseFloat(itemCard.dataset.itemPrice) || 0,
            points: parseFloat(itemCard.dataset.itemPoints) || 0,
            size: itemCard.dataset.itemSize
        };

        console.log("Item Data:", itemData);  // Log to check item data

        fetch('/redeem_rewards', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(itemData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Response:', data);
            // Handle response if necessary
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
