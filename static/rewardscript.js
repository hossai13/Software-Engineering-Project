document.addEventListener("DOMContentLoaded", () => {
    // Scroll buttons functionality
    document.querySelectorAll('.scroll-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const scrollWrapper = document.querySelector('.scroll-wrapper');
            const direction = e.target.classList.contains('left') ? -1 : 1;
            const scrollAmount = 455;
            scrollWrapper.scrollBy({
                left: direction * scrollAmount,
                behavior: 'smooth'
            });
        });
    });

    // Navigation buttons functionality
    const menuNavButtons = document.querySelectorAll(".nav-btn");
    const navBarHeight = 80;

    menuNavButtons.forEach(button => {
        button.addEventListener("click", () => {
            const targetId = button.getAttribute("data-target");
            const targetSection = document.getElementById(targetId);

            if (targetSection) {
                const scrollPosition = targetSection.offsetTop - navBarHeight;
                window.scrollTo({
                    top: scrollPosition,
                    behavior: "smooth"
                });
            }
        });
    });

    // Admin Tools Modal
    const adminToolsBtn = document.getElementById("admin-tools-btn");
    const adminToolsModal = document.getElementById("admin-tools-modal");
    const closeAdminModal = document.querySelector(".close-btn");

    if (adminToolsBtn) {
        adminToolsBtn.addEventListener("click", () => {
            adminToolsModal.style.display = "block";
        });
    }

    if (closeAdminModal) {
        closeAdminModal.addEventListener("click", () => {
            adminToolsModal.style.display = "none";
        });

        window.addEventListener("click", (event) => {
            if (event.target === adminToolsModal) {
                adminToolsModal.style.display = "none";
            }
        });
    }

    // Item Modal Logic
    const itemModal = document.getElementById("item-modal");
    const itemName = document.getElementById("item-name");
    const sizeOptionsContainer = document.getElementById("size-options-container");
    const toppingsOptionsContainer = document.getElementById("toppings-options-container");
    const totalPriceDisplay = document.getElementById("total-price");
    const quantityDisplay = document.getElementById("quantity-display");
    const decreaseQtyButton = document.getElementById("decrease-qty");
    const increaseQtyButton = document.getElementById("increase-qty");
    const addToCartButton = document.getElementById("add-to-cart-button");
    const closeItemModal = document.querySelector(".close");

    let currentItem = {};
    let basePrice = 0;
    let basePoints = 0;
    let toppingsPrice = 0;
    let quantity = 1;

   
    function loadSizes(itemId, itemName, itemPrice) {
        sizeOptionsContainer.innerHTML = '';

        fetch(`/api/item_sizes/${itemId}`)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.error || 'Failed to load sizes');
                    });
                }
                return response.json();
            })
            .then(sizes => {
                if (sizes.length === 0) {
                    
                    sizeOptionsContainer.innerHTML = `
                        <label>
                            <input type="radio" name="size" value="${itemName}" data-price="${itemPrice}" checked>
                            ${itemName} ($${parseFloat(itemPrice).toFixed(2)})
                        </label>
                    `;
                    basePrice = parseFloat(itemPrice);
                    calculateTotal();
                    return;
                }

                sizes.sort((a, b) => {
                    const order = { Small: 0, Large: 1, Giant: 2 };
                    return order[a.size] - order[b.size];
                });

                sizes.forEach(size => {
                    const sizePrice = parseFloat(size.price);
                    const sizeOption = document.createElement('label');
                    sizeOption.innerHTML = `
                        <input type="radio" name="size" value="${size.size}" data-price="${sizePrice}">
                        ${size.size} (+$${sizePrice.toFixed(2)})
                    `;
                    sizeOptionsContainer.appendChild(sizeOption);
                });

                const defaultSize = sizeOptionsContainer.querySelector('input[name="size"]');
                if (defaultSize) {
                    defaultSize.checked = true;
                    basePrice = parseFloat(defaultSize.dataset.price);
                }

                sizeOptionsContainer.querySelectorAll('input[name="size"]').forEach(input => {
                    input.addEventListener('change', () => {
                        basePrice = parseFloat(input.dataset.price);
                        calculateTotal();
                    });
                });

                calculateTotal();
            })
            .catch(error => {
                console.error(error);
                sizeOptionsContainer.innerHTML = `<p>${error.message}</p>`;
            });
    }

    function loadToppings(itemId, isPointBased) {
        toppingsOptionsContainer.innerHTML = '';
    
        if (isPointBased) {
            toppingsOptionsContainer.innerHTML = '<p>Toppings are not available for point-based items.</p>';
            return;
        }
    
        fetch(`/api/item_toppings/${itemId}`)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.error || 'Failed to load toppings');
                    });
                }
                return response.json();
            })
            .then(toppings => {
                if (toppings.length === 0) {
                    toppingsOptionsContainer.innerHTML = '<p>No toppings available for this item.</p>';
                    return;
                }
    
                toppings.forEach(topping => {
                    const toppingElement = document.createElement('div');
                    toppingElement.classList.add('topping-item');
                    toppingElement.innerHTML = `
                        <label>
                            <input type="checkbox" name="topping" value="${topping.toppingName}" data-price="${topping.price}">
                            ${topping.toppingName} (+$${topping.price.toFixed(2)})
                        </label>
                    `;
                    toppingsOptionsContainer.appendChild(toppingElement);
    
                    toppingElement.querySelector('input').addEventListener('change', (e) => {
                        const toppingPrice = parseFloat(e.target.dataset.price);
                        if (e.target.checked) {
                            toppingsPrice += toppingPrice;
                        } else {
                            toppingsPrice -= toppingPrice;
                        }
                        calculateTotal();
                    });
                });
            })
            .catch(error => {
                console.error(`Error loading toppings for item ${itemId}:`, error);
                toppingsOptionsContainer.innerHTML = `<p>${error.message}</p>`;
            });
    }

    function calculateTotal() {
            const totalPrice = (basePrice + toppingsPrice) * quantity;
            const totalPoints = basePoints * quantity;
        
            if (basePrice) {
                totalPriceDisplay.textContent = `$${totalPrice.toFixed(2)}`;
                addToCartButton.innerHTML = `ADD TO ORDER - $${totalPrice.toFixed(2)}`;
            } else if (basePoints) {
                totalPriceDisplay.textContent = `${totalPoints} Points`;
                addToCartButton.innerHTML = `ADD TO ORDER - ${totalPoints} Points`;
            } 
    }

    const featuredItems = document.querySelectorAll(".item-card");

    featuredItems.forEach(item => {
        const orderButton = item.querySelector(".order-button");
    
        orderButton.addEventListener("click", () => {
            const itemData = {
                id: item.dataset.itemId,
                name: item.dataset.itemName,
                price: parseFloat(item.dataset.itemPrice) || null,
                points: parseFloat(item.dataset.itemPoints) || null,
                category: item.dataset.itemCategory,
                img: item.dataset.itemImg
            };
            
            console.log("Item Data:", itemData);
            openModal(itemData);
        });
    });
    
    function openModal(itemData) {
        const { id, name, price, points, category, img } = itemData;
        
        currentItem = { id, name, price: parseFloat(price), points: parseFloat(points), category, img };
        itemName.textContent = name;
        basePrice = parseFloat(price) || 0;
        basePoints = parseFloat(points) || 0;  // Initialize basePoints
        toppingsPrice = 0;
        quantity = 1;
        quantityDisplay.textContent = quantity;
        
        // Update modal image if provided
        const modalImage = document.getElementById("modal-image");
        if (modalImage && img) {
            modalImage.src = img;
            modalImage.alt = name;
        }
    
        // Update modal price display if provided
        const modalPrice = document.getElementById("modal-price");
        if (modalPrice) {
            if (basePrice) {
                modalPrice.textContent = `$${basePrice.toFixed(2)}`;
            } else if (basePoints) {
                modalPrice.textContent = `${basePoints} points`;
            }
        }    
    
        if (category === "Pizza" && itemData.hasSizes) {
            document.querySelector('.toppings-options').style.display = 'block';
            loadSizes(id, name, price);
            loadToppings(id);
        } else {
            document.querySelector('.toppings-options').style.display = 'none';

            sizeOptionsContainer.innerHTML = `
                <label>
                    <input type="radio" name="size" value="${category}" data-price="${price}" checked>
                    ${category} (${parseFloat(price).toFixed(0)})
                </label>
            `;
            basePrice = parseFloat(price);
            calculateTotal();
        }
    
        itemModal.style.display = 'block';
    }
    
    function setupModalTriggers() {
        document.querySelectorAll(".menu-item-card, .item-card").forEach(card => {
            card.addEventListener("click", () => {
                const itemData = {
                    id: card.dataset.itemId,
                    name: card.dataset.itemName,
                    price: card.dataset.itemPrice,
                    category: card.dataset.itemCategory,
                    img: card.dataset.itemImg,
                    hasSizes: card.dataset.hasSizes === "true"
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
        const selectedSize = document.querySelector('input[name="size"]:checked');
        const size = selectedSize ? selectedSize.value : null;
    
        const selectedToppings = Array.from(document.querySelectorAll('input[name="topping"]:checked')).map(
            topping => ({
                name: topping.value,
                price: parseFloat(topping.dataset.price)
            })
        );
    
        const toppingTotalPrice = selectedToppings.reduce((total, topping) => total + topping.price, 0);
        const itemTotalPrice = (basePrice + toppingTotalPrice) * quantity;
    
        // Check if the item has points instead of price
        const points = parseInt(currentItem.points) || null;
    
        const data = {
            id: currentItem.id,
            name: currentItem.name,
            price: basePrice,
            quantity: quantity,
            size: size,
            category: currentItem.category,
            toppings: selectedToppings,
            total_price: itemTotalPrice,
            points: points
        };
    
        fetch('/api/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(cart => {
                console.log('Cart updated:', cart);
                updateCartUI(cart);
                itemModal.style.display = 'none';
            })
            .catch(error => {
                console.error('Error adding to cart:', error);
            });
    });
    
    function loadCart() {
        fetch('/api/cart')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load cart');
                }
                return response.json();
            })
            .then(cart => {
                console.log('Cart loaded:', cart);
                updateCartUI(cart);
            })
            .catch(error => {
                console.error('Error loading cart:', error);
            });
    }
    
    function updateCartUI(cart) {
        const cartItemsContainer = document.querySelector(".cart-items");
        cartItemsContainer.innerHTML = '';
    
        if (cart.items.length === 0) {
            cartItemsContainer.innerHTML = `
                <p class="empty-cart">Your cart is empty</p>
                <img src="/static/Images_Videos/pizza-oven2.png" alt="Pizza Stove" class="empty-cart-img">
            `;
        } else {
            cart.items.forEach(item => {
                const toppingsDisplay = item.toppings.map(topping => topping.name).join(', ');
                const sizeOrCategory = item.size ? `(${item.size})` : `(${item.category})`;
                const cartItem = document.createElement("div");
                cartItem.classList.add("cart-item");
                cartItem.innerHTML = `
                    <p>${item.quantity}x ${item.name} ${sizeOrCategory}</p>
                    ${toppingsDisplay ? `<small>Toppings: ${toppingsDisplay}</small>` : ''}
                    <p>${item.price ? `$${item.total_price.toFixed(2)}` : `${item.total_points} points`}</p>
                    <button class="remove-item" data-id="${item.id}">Remove</button>
                `;
                cartItemsContainer.appendChild(cartItem);
    
                cartItem.querySelector('.remove-item').addEventListener('click', () => {
                    removeFromCart(item.id);
                });
            });
        }
    
        const subtotal = cart.total;
        const totalPoints = cart.total_points || 0;
        totalCostDisplay.dataset.subtotal = subtotal;
        totalCostDisplay.textContent = `TOTAL: $${subtotal.toFixed(2)} (Total Points: ${totalPoints})`;
    
        calculateTip();
    }    

    function removeFromCart(itemId) {
        fetch('/api/cart', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: itemId })
        })
            .then(response => response.json())
            .then(cart => {
                console.log('Item removed:', cart);
                updateCartUI(cart);
            })
            .catch(error => {
                console.error('Error removing item:', error);
            });
    }

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

    const tipOptions = document.querySelectorAll(".tip-option");
    const tipAmountDisplay = document.getElementById("tip-amount");
    const totalCostDisplay = document.querySelector(".total-cost");
    
    let subtotal = 0;
    let selectedTip = 0;

    function calculateTip() {

        const cartSubtotal = parseFloat(totalCostDisplay.dataset.subtotal || 0);
    
        let tipAmount = 0;
    
        if (selectedTip === "other") {
            const customTip = parseFloat(prompt("Enter custom tip amount:", "0")) || 0;
            tipAmount = customTip;
        } else {
            tipAmount = (cartSubtotal * selectedTip) / 100;
        }

        tipAmountDisplay.textContent = `$${tipAmount.toFixed(2)}`;

        const totalWithTip = cartSubtotal + tipAmount;
        totalCostDisplay.textContent = `TOTAL: $${totalWithTip.toFixed(2)}`;
    }

    tipOptions.forEach(option => {
        option.addEventListener("click", () => {
            tipOptions.forEach(btn => btn.classList.remove("active")); 
            option.classList.add("active");
    
            selectedTip = option.getAttribute("data-tip") === "other" ? "other" : parseInt(option.getAttribute("data-tip"));

            calculateTip();
        });
    });
});
