// Sidebar toggle
const sidebar = document.querySelector('.sidebar');
const toggleBtn = document.querySelector('.sidebar-toggle');
toggleBtn.addEventListener('click', () => sidebar.classList.toggle('collapsed'));

// Theme toggle
document.querySelector('.theme-toggle').addEventListener('click', () => {
    document.body.classList.toggle('dark');
});

// Profile photo upload preview
const photoInput = document.getElementById('photoUpload');
const profileImg = document.getElementById('profileImg');
photoInput.addEventListener('change', e => {
    const file = e.target.files[0];
    if(file) profileImg.src = URL.createObjectURL(file);
});

// Save profile
document.getElementById('playerForm').addEventListener('submit', e => {
    e.preventDefault();
    alert('Profile Saved!');
});

// Delete profile
document.querySelector('.delete-btn').addEventListener('click', () => {
    if(confirm('Are you sure you want to delete your profile?')) {
        alert('Profile Deleted!');
        // Reset form for demo
        document.getElementById('playerForm').reset();
        profileImg.src = 'https://via.placeholder.com/150';

    }

    // Sidebar toggle
const sidebar = document.querySelector('.sidebar');
const toggleBtn = document.querySelector('.sidebar-toggle');
toggleBtn.addEventListener('click', () => sidebar.classList.toggle('collapsed'));

// Theme toggle
document.querySelector('.theme-toggle').addEventListener('click', () => {
    document.body.classList.toggle('dark');
});

// Profile photo upload preview (main)
const photoInput = document.getElementById('photoUpload');
const profileImg = document.getElementById('profileImg');
photoInput.addEventListener('change', e => {
    const file = e.target.files[0];
    if(file) profileImg.src = URL.createObjectURL(file);
});

// Profile photo upload preview (topbar)
const photoInputDropdown = document.getElementById('photoUploadDropdown');
const topProfileImg = document.getElementById('topProfileImg');
photoInputDropdown.addEventListener('change', e => {
    const file = e.target.files[0];
    if(file) topProfileImg.src = URL.createObjectURL(file);
});

// Save profile
document.getElementById('playerForm').addEventListener('submit', e => {
    e.preventDefault();
    alert('Profile Saved!');
});

// Delete profile
document.querySelector('.delete-btn').addEventListener('click', () => {
    if(confirm('Are you sure you want to delete your profile?')) {
        alert('Profile Deleted!');
        document.getElementById('playerForm').reset();
        profileImg.src = 'https://via.placeholder.com/150';
        topProfileImg.src = 'https://via.placeholder.com/50';
    }
});

// Dropdown toggle
const profileMenu = document.querySelector('.profile-menu');
profileMenu.addEventListener('click', () => {
    profileMenu.classList.toggle('active');
});

// Delete account from dropdown
document.querySelector('.delete-account').addEventListener('click', () => {
    if(confirm('Are you sure you want to delete your account?')) {
        alert('Account Deleted!');
        // Reset demo data
        profileImg.src = 'https://via.placeholder.com/150';
        topProfileImg.src = 'https://via.placeholder.com/50';
        document.getElementById('playerForm').reset();
    }
});

// Logout buttons
document.querySelectorAll('.logout-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        alert('Logged Out!');
        // Redirect or reload
        location.reload();
    });
});

});
