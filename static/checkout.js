document.addEventListener("DOMContentLoaded", () => {
    const cartItemsContainer = document.getElementById("cart-items");
    const subtotalElement = document.getElementById("subtotal");
    const taxElement = document.getElementById("tax");
    const tipAmountElement = document.getElementById("tip-amount");
    const tipAmountElement2 = document.getElementById("tip-amount2");
    const totalElement = document.getElementById("total");
    const finalTotalInput = document.getElementById("final-total");
    const tipOptions = document.querySelectorAll(".tip-option");
    let subtotal = parseFloat(subtotalElement.textContent.replace("$", "")) || 0;
    subtotal = parseFloat(subtotal.toFixed(2));
    const taxRate = 0.08;
    let selectedTip = 0;

    // Modal Functionality
    const deliveryModal = document.getElementById("delivery-modal");
    const deliveryButton = document.querySelector(".edit-button");
    const closeDeliveryModal = document.querySelector(".close-btn");
    const saveButton = document.querySelector(".save-button");

    const toggleDelivery = document.getElementById("toggle-delivery");
    const togglePickup = document.getElementById("toggle-pickup");
    const deliverySection = document.getElementById("delivery-section");
    const pickupSection = document.getElementById("pickup-section");
    const pickupSchedule = document.getElementById("pickup-schedule");
    const addressInput = document.getElementById("address-input");

    let selectedOption = localStorage.getItem("selectedOption") || "Delivery";
    let selectedPickupTime = localStorage.getItem("selectedPickupTime") || "ASAP (15-30 minutes)";
    let deliveryAddress = localStorage.getItem("deliveryAddress") || "";

    function populatePickupTimes() {
        const startHour = 9;
        const endHour = 21;

        for (let hour = startHour; hour <= endHour; hour++) {
            for (let minute = 0; minute < 60; minute += 30) {
                const time = new Date();
                time.setHours(hour);
                time.setMinutes(minute);

                const timeOption = document.createElement("option");
                timeOption.value = time.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
                timeOption.textContent = time.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

                pickupSchedule.appendChild(timeOption);
            }
        }
    }

    populatePickupTimes();

    if (selectedOption === "Pickup") {
        togglePickup.click();
        pickupSchedule.value = selectedPickupTime;
    } else if (selectedOption === "Delivery") {
        toggleDelivery.click();
        addressInput.value = deliveryAddress;
    }

    deliveryButton.addEventListener("click", () => {
        deliveryModal.style.display = "block";

        if (selectedOption === "Delivery") {
            toggleDelivery.click();
            addressInput.value = deliveryAddress;
        } else if (selectedOption === "Pickup") {
            togglePickup.click();
            pickupSchedule.value = selectedPickupTime;
        }
    });

    closeDeliveryModal.onclick = () => (deliveryModal.style.display = "none");

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
        const detailsTime = document.querySelector(".details-item p strong");
        const detailsAddress = document.querySelector(".details-item p:nth-child(2)");

        if (selectedOption === "Pickup") {
            selectedPickupTime = pickupSchedule.value;
            detailsTime.textContent = `Pick Up - ${selectedPickupTime}`;
            detailsAddress.textContent = "4518 Baltimore Ave, Philadelphia, PA 19143";

            localStorage.setItem("selectedOption", "Pickup");
            localStorage.setItem("selectedPickupTime", selectedPickupTime);

            fetch("/set-pickup-time", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ pickup_time: selectedPickupTime }),
            }).catch((error) => console.error("Error saving pickup time:", error));
        } else if (selectedOption === "Delivery") {
            const newDeliveryAddress = addressInput.value.trim();

            if (newDeliveryAddress) {
                deliveryAddress = newDeliveryAddress;
                detailsTime.textContent = "Delivery";
                detailsAddress.textContent = deliveryAddress;

                localStorage.setItem("selectedOption", "Delivery");
                localStorage.setItem("deliveryAddress", deliveryAddress);

                fetch("/set-pickup-time", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ pickup_time: "Delivery", address: deliveryAddress }),
                }).catch((error) => console.error("Error saving delivery address:", error));
            } else {
                alert("Please enter a valid delivery address.");
                return;
            }
        }

        deliveryModal.style.display = "none";
    };
    function setTipOnServer(tipAmount) {
        fetch("/set-tip", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tip: tipAmount }),
        }).catch((error) => console.error("Error setting tip:", error));
    }
    
    tipOptions.forEach((option) => {
        option.addEventListener("click", () => {
            tipOptions.forEach((btn) => btn.classList.remove("active"));
            option.classList.add("active");
    
            if (option.dataset.tip === "other") {
                let customTip = prompt("Enter flat tip amount:", "0");
                if (customTip !== null && customTip.trim() !== "") {
                    customTip = parseFloat(customTip);
                    if (!isNaN(customTip) && customTip >= 0) {
                        selectedTip = customTip;
                    } else {
                        alert("Please enter a valid positive number for the tip.");
                        selectedTip = 0;
                    }
                } else {
                    selectedTip = 0;
                }
            } else {
                selectedTip = (subtotal * parseFloat(option.dataset.tip) / 100);
            }
    
            calculateTotal();
            setTipOnServer(selectedTip); // Update the server
        });
    });

    function calculateTotal() {
        const taxAmount = (subtotal * taxRate).toFixed(2);
        const tipAmount = selectedTip.toFixed(2);
        const total = (subtotal + parseFloat(taxAmount) + parseFloat(tipAmount)).toFixed(2);

        taxElement.textContent = `$${taxAmount}`;
        tipAmountElement.textContent = `$${tipAmount}`;
        tipAmountElement2.textContent = `$${tipAmount}`;
        totalElement.textContent = `$${total}`;
        finalTotalInput.value = total;
    }

    calculateTotal();

    const cartContainer = document.querySelector(".cart-summary");

    cartItemsContainer.querySelectorAll(".cart-item").forEach((item) => {
        item.setAttribute("draggable", "true");

        item.addEventListener("dragstart", (e) => {
            e.dataTransfer.setData("text/plain", item.dataset.itemId);
            item.classList.add("dragging");
        });

        item.addEventListener("dragend", (e) => {
            item.classList.remove("dragging");

            const cartRect = cartContainer.getBoundingClientRect();
            const isInsideCart =
                e.clientX >= cartRect.left &&
                e.clientX <= cartRect.right &&
                e.clientY >= cartRect.top &&
                e.clientY <= cartRect.bottom;

            if (!isInsideCart) {
                const itemId = item.dataset.itemId;
                fetch("/api/cart", {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ id: itemId }),
                })
                    .then((response) => response.json())
                    .then((data) => {
                        console.log("Item removed from cart:", data);
                        location.reload();
                    })
                    .catch((error) => {
                        console.error("Error removing item:", error);
                    });
            }
        });
    });

    document.addEventListener("dragover", (e) => {
        e.preventDefault();
    });

    document.addEventListener("drop", (e) => {
        e.preventDefault();
    });

    const redeemButtons = document.querySelectorAll(".redeem-button");

    redeemButtons.forEach(button => {
        button.addEventListener("click", () => {
            const rewardCard = button.closest(".reward-card");
            const itemId = rewardCard.dataset.itemId;
            const itemName = rewardCard.dataset.itemName;
            const itemPoints = parseInt(rewardCard.dataset.itemPoints);
            const itemPrice = parseFloat(rewardCard.dataset.itemPrice);
            const itemSize = rewardCard.dataset.itemSize;

            fetch("/redeem_rewards", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    id: itemId,
                    name: itemName,
                    points: itemPoints,
                    price: itemPrice,
                    size: itemSize,
                    quantity: 1,
                    category: "Rewards"
                }),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === "success") {
                        alert(`You have successfully redeemed ${itemName}!`);
                        location.reload();
                    } else {
                        alert(data.message || "Failed to redeem the reward.");
                    }
                })
                .catch(error => {
                    console.error("Error redeeming reward:", error);
                    alert("An error occurred while redeeming the reward.");
                });
        });
    });
});