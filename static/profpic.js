function openModal() {
    document.getElementById('pic-modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('pic-modal').style.display = 'none';
}

function changeProfilePic(pic) {
    document.getElementById("profile-pic").src = pic;
    closeModal();  
}

window.onclick = function(event) {
    if (event.target === document.getElementById('pic-modal')) {
        closeModal();
    }
};