function openModal() {
    document.getElementById('pic-modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('pic-modal').style.display = 'none';
}

function changeProfilePic(imagePath) {
    document.getElementById("profile-pic").src = "{{ url_for('static', filename='') }}" + imagePath;
    closeModal();
}


window.onclick = function(event) {
    if (event.target === document.getElementById('pic-modal')) {
        closeModal();
    }
};

function changeProfilePic(selectedPic) {
    const profilePicElement = document.getElementById('profile-pic');
    fetch('/update-profile-pic', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ profile_pic: selectedPic })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Profile picture updated successfully!') {
            profilePicElement.src = `/static/${selectedPic}`;
        }
    })
    .catch(error => {
        console.log('Error:', error);
    });
}


