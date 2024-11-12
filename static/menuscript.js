document.querySelectorAll('.scroll-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const scrollWrapper = document.querySelector('.scroll-wrapper');
        const direction = e.target.classList.contains('left') ? -1 : 1;
        const scrollAmount = 500;
        scrollWrapper.scrollBy({
            left: direction * scrollAmount,
            behavior: 'smooth'
        });
    });
});

document.addEventListener("DOMContentLoaded", () => {
    // Item Modal Logic
    const itemModal = document.getElementById("item-modal");
    const itemName = document.getElementById("item-name");
    const sizeOptionsContainer = document.getElementById("size-options-container");
    const quantityDisplay = document.getElementById("quantity-display");
    const decreaseQtyButton = document.getElementById("decrease-qty");
    const increaseQtyButton = document.getElementById("increase-qty");
    const addToCartButton = document.getElementById("add-to-cart-button");
    const closeItemModal = document.querySelector(".close");
    const toppingOptions = document.querySelectorAll('input[name="topping"]');
    const totalPriceDisplay = document.getElementById("total-price");

    let currentItem = {};
    let basePrice = 0;
    let quantity = 1;
    let toppingsPrice = 0;

    // Function to open modal dynamically
    function openModal(itemData) {
        const { name, price } = itemData;

        currentItem = {
            name,
            price: parseFloat(price),
            quantity: 1
        };

        itemName.textContent = `Customize Your ${name}`;
        basePrice = parseFloat(price);
        toppingsPrice = 0;
        quantity = 1;
        quantityDisplay.textContent = quantity;

        // Populate size options dynamically
        sizeOptionsContainer.innerHTML = `
            <label>
                <input type="radio" name="size" value="${name}" data-price="${price}" checked>
                ${name} ($${basePrice.toFixed(2)})
            </label>
        `;

        calculateTotal();
        itemModal.style.display = "block";
    }

    // Add event listeners to both menu-item-card and order-button
    function setupModalTriggers() {
        document.querySelectorAll(".menu-item-card, .item-card").forEach(card => {
            card.addEventListener("click", (e) => {
                const itemData = {
                    name: card.dataset.itemName || card.querySelector(".menu-item-title").textContent,
                    price: card.dataset.itemPrice || card.querySelector(".original-price").textContent.replace('$', '')
                };
                openModal(itemData);
            });
        });

        document.querySelectorAll(".order-button").forEach(button => {
            button.addEventListener("click", (e) => {
                const itemCard = e.target.closest(".item-card");
                const itemData = {
                    name: itemCard.dataset.itemName || itemCard.querySelector("h3").textContent,
                    price: itemCard.dataset.itemPrice || itemCard.querySelector(".price span").textContent.replace('$', '')
                };
                openModal(itemData);
            });
        });
    }

    setupModalTriggers();

    closeItemModal.addEventListener("click", () => {
        itemModal.style.display = "none";
    });

    window.addEventListener("click", (event) => {
        if (event.target === itemModal) {
            itemModal.style.display = "none";
        }
    });

    toppingOptions.forEach(option => {
        option.addEventListener("change", (e) => {
            const toppingPrice = parseFloat(e.target.dataset.price);
            if (e.target.checked) {
                toppingsPrice += toppingPrice;
            } else {
                toppingsPrice -= toppingPrice;
            }
            calculateTotal();
        });
    });

    decreaseQtyButton.addEventListener("click", () => {
        if (quantity > 1) {
            quantity--;
            quantityDisplay.textContent = quantity;
            calculateTotal();
        }
    });

    increaseQtyButton.addEventListener("click", () => {
        quantity++;
        quantityDisplay.textContent = quantity;
        calculateTotal();
    });

    addToCartButton.addEventListener("click", () => {
        const cartItemsContainer = document.querySelector(".cart-items");
        const emptyCartMessage = document.querySelector(".empty-cart");
        const emptyCartImg = document.querySelector(".empty-cart-img");

        if (emptyCartMessage && emptyCartImg) {
            emptyCartMessage.style.display = "none";
            emptyCartImg.style.display = "none";
        }

        const cartItem = document.createElement("div");
        cartItem.classList.add("cart-item");
        cartItem.innerHTML = `
            <p>${quantity}x ${currentItem.name}</p>
            <p>$${((basePrice + toppingsPrice) * quantity).toFixed(2)}</p>
        `;
        cartItemsContainer.appendChild(cartItem);

        updateTotalCost();

        itemModal.style.display = "none";

        document.dispatchEvent(new CustomEvent("cartUpdated"));
    });

    function calculateTotal() {
        const totalPrice = (basePrice + toppingsPrice) * quantity;
        totalPriceDisplay.textContent = totalPrice.toFixed(2);
        addToCartButton.innerHTML = `ADD TO ORDER - $${totalPrice.toFixed(2)}`;
    }

    function updateTotalCost() {
        const totalCostDisplay = document.querySelector(".total-cost");
        const cartItems = document.querySelectorAll(".cart-item p:nth-child(2)");
        let total = 0;

        cartItems.forEach(item => {
            total += parseFloat(item.textContent.replace('$', ''));
        });

        subtotal = total; // Store for tip calculation
        totalCostDisplay.textContent = `Total: $${(subtotal + calculateTip()).toFixed(2)}`;
    }

    // Delivery Modal Logic (Unchanged)
    const deliveryModal = document.getElementById("delivery-modal");
    const deliveryButton = document.getElementById("delivery-button");
    const closeDeliveryModal = document.querySelector(".close-btn");
    const saveButton = document.querySelector(".save-button");

    const toggleDelivery = document.getElementById("toggle-delivery");
    const togglePickup = document.getElementById("toggle-pickup");
    const deliverySection = document.getElementById("delivery-section");
    const pickupSection = document.getElementById("pickup-section");
    const pickupSchedule = document.getElementById("pickup-schedule");

    let selectedOption = "Delivery";
    let selectedPickupTime = "ASAP";

    function populatePickupTimes() {
        const startHour = 9;
        const endHour = 21;

        for (let hour = startHour; hour <= endHour; hour++) {
            for (let minute = 0; minute < 60; minute += 30) {
                const time = new Date();
                time.setHours(hour);
                time.setMinutes(minute);

                const timeOption = document.createElement("option");
                timeOption.value = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                timeOption.textContent = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

                pickupSchedule.appendChild(timeOption);
            }
        }
    }

    populatePickupTimes();

    deliveryButton.addEventListener("click", () => {
        deliveryModal.style.display = "block";
    });

    closeDeliveryModal.onclick = () => deliveryModal.style.display = "none";

    window.onclick = (event) => {
        if (event.target === deliveryModal) {
            deliveryModal.style.display = "none";
        }
    };

    toggleDelivery.addEventListener("click", () => {
        toggleDelivery.classList.add("active");
        togglePickup.classList.remove("active");
        deliverySection.classList.remove("hidden");
        pickupSection.classList.add("hidden");
        selectedOption = "Delivery";
    });

    togglePickup.addEventListener("click", () => {
        togglePickup.classList.add("active");
        toggleDelivery.classList.remove("active");
        pickupSection.classList.remove("hidden");
        deliverySection.classList.add("hidden");
        selectedOption = "Pickup";
    });

    saveButton.onclick = () => {
        if (selectedOption === "Pickup") {
            selectedPickupTime = pickupSchedule.value;
            deliveryButton.textContent = `Pickup at ${selectedPickupTime}`;
        } else {
            deliveryButton.textContent = "Delivery";
        }
        deliveryModal.style.display = "none";
    };

    // Tip Feature Logic (Unchanged)
    const tipOptions = document.querySelectorAll(".tip-option");
    const tipAmountDisplay = document.getElementById("tip-amount");
    const totalCostDisplay = document.querySelector(".total-cost");
    let subtotal = 0;
    let selectedTip = 0;

    function calculateTip() {
        let tipAmount = 0;
        if (selectedTip === "other") {
            tipAmount = parseFloat(prompt("Enter custom tip amount:") || "0");
        } else {
            tipAmount = (subtotal * selectedTip) / 100;
        }
        tipAmountDisplay.textContent = `$${tipAmount.toFixed(2)}`;
        return tipAmount; // Ensure tip amount is used in grand total
    }

    tipOptions.forEach(option => {
        option.addEventListener("click", () => {
            tipOptions.forEach(btn => btn.classList.remove("active"));
            option.classList.add("active");
            selectedTip = option.getAttribute("data-tip") === "other" ? "other" : parseInt(option.getAttribute("data-tip"));
            updateTotalCost(); // Recalculate with tip
        });
    });

    document.addEventListener("cartUpdated", updateTotalCost);
});
