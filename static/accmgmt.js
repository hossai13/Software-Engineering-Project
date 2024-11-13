document.getElementById('admin-panel-link').addEventListener('click', function(event) {
    event.preventDefault();
    document.querySelector('.profile-container').style.display = 'none';
    document.querySelector('.admin-container').style.display = 'block';
});

document.getElementById('back-to-profile').addEventListener('click', function(event) {
    event.preventDefault();
    document.querySelector('.admin-container').style.display = 'none';
    document.querySelector('.profile-container').style.display = 'flex';
});