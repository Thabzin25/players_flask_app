document.addEventListener("DOMContentLoaded", () => {

    // ===== Theme Toggle =====
    const themeToggle = document.getElementById("themeToggle");
    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            document.body.classList.toggle("dark");
            document.body.classList.toggle("light");
            const icon = themeToggle.querySelector("i");
            icon.classList.toggle("fa-moon");
            icon.classList.toggle("fa-sun");
        });
    }

    // ===== Sidebar Toggle =====
    const sidebarToggle = document.getElementById("toggleSidebar");
    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", () => {
            const sidebar = document.getElementById("sidebar");
            const main = document.querySelector(".main");
            if (sidebar && main) {
                sidebar.classList.toggle("collapsed");
                main.classList.toggle("collapsed");
            }

        });

    }
    document.getElementById("toggleSidebar").addEventListener("click", () => {
    document.getElementById("sidebar").classList.toggle("collapsed");
    document.querySelector(".main").classList.toggle("collapsed");
});


    // ===== Profile Menu Toggle =====
    const profilePic = document.getElementById("profilePic");
    if (profilePic) {
        profilePic.addEventListener("click", () => {
            const profileMenu = document.querySelector(".profile-menu");
            if (profileMenu) profileMenu.classList.toggle("active");
        });
    }

    // ===== Upload Profile Picture =====
    const uploadPic = document.getElementById("uploadPic");
    if (uploadPic) {
        uploadPic.addEventListener("change", function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    if(profilePic) profilePic.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // ===== Logout =====
    const logoutBtn = document.getElementById("logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            alert("You have been logged out.");
        });
    }

    // ===== Notifications =====
    const notifBtn = document.querySelector(".notif");
    if (notifBtn) {
        notifBtn.addEventListener("click", () => {
            alert("You have 3 new notifications.");
        });
    }

    // ===== Active Sidebar Menu Highlight =====
    const sidebarItems = document.querySelectorAll(".sidebar ul li");
    sidebarItems.forEach(item => {
        item.addEventListener("click", () => {
            sidebarItems.forEach(li => li.classList.remove("active"));
            item.classList.add("active");
        });
    });

    // ===== Dashboard Toggle Buttons =====
    const toggleBtns = document.querySelectorAll(".toggle-btn");
    toggleBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            toggleBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            // Example: placeholder for filtering logic
            alert(`Showing: ${btn.dataset.filter} reports`);
        });
    });

});
