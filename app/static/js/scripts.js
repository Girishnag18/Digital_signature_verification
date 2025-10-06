// Show confirmation before logout
document.addEventListener("DOMContentLoaded", function () {
    const logoutLinks = document.querySelectorAll('a[href*="logout"]');
    logoutLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            if (!confirm("Are you sure you want to log out?")) {
                e.preventDefault();
            }
        });
    });
});

// Auto-hide flash messages after 5 seconds
setTimeout(function () {
    let alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
        alert.classList.add("fade");
        setTimeout(() => alert.remove(), 500);
    });
}, 5000);

// Optional: Preview uploaded file name
const fileInputs = document.querySelectorAll('input[type="file"]');
fileInputs.forEach(input => {
    input.addEventListener("change", function () {
        let fileName = this.files[0]?.name;
        if (fileName) {
            alert("Selected file: " + fileName);
        }
    });
});