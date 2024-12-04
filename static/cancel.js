const orderDate = new Date("{{ orders[0].date_ordered }}").getTime();
const cancelButton = document.querySelector('.cancel-order-button');
const cancelPeriod = 300000; 
function updateCancelButton() {
    const currentTime = new Date().getTime();
    const timeElapsed = currentTime - orderDate;
    if (timeElapsed > cancelPeriod) {
        cancelButton.disabled = true;
        cancelButton.textContent = "Cancellation period has passed";
    }
}

setInterval(updateCancelButton, 1000);
function openModal(orderId) {
    document.getElementById('cancelOrderId').value = orderId;
    document.getElementById('cancelModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('cancelModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('cancelModal');
    if (event.target === modal) {
        closeModal();
    }
};
