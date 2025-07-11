document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('wrapper').classList.toggle('toggled');
        });
    }
});