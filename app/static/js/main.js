const menuBtn = document.getElementById('menuBtn');
const mobileNav = document.getElementById('mobileNav');
if (menuBtn) menuBtn.addEventListener('click', () => mobileNav.classList.toggle('open'));
document.querySelectorAll('.toast-message').forEach((toast) => setTimeout(() => toast.classList.add('hide'), 3500));
