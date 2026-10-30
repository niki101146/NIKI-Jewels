(() => {
 const menu = document.getElementById('adminSidebar');
 const open = document.getElementById('adminMenuOpen');
 const close = document.getElementById('adminMenuClose');
 const backdrop = document.getElementById('adminMenuBackdrop');
 const mobile = window.matchMedia('(max-width: 767px)');
 function setOpen(value, restore = true) {
  document.body.classList.toggle('admin-menu-open', value);
  open.setAttribute('aria-expanded', String(value));
  backdrop.hidden = !value;
  menu.inert = mobile.matches && !value;
  if (value) close.focus();
  else if (restore) open.focus();
 }
 open.addEventListener('click', () => setOpen(true));
 close.addEventListener('click', () => setOpen(false));
 backdrop.addEventListener('click', () => setOpen(false));
 menu.addEventListener('click', event => { if (event.target.closest('a') && mobile.matches) setOpen(false); });
 document.addEventListener('keydown', event => {
  if (!document.body.classList.contains('admin-menu-open')) return;
  if (event.key === 'Escape') setOpen(false);
  if (event.key === 'Tab') {
   const links = [...menu.querySelectorAll('a[href], button')].filter(el => el.getClientRects().length);
   const first = links[0], last = links[links.length - 1];
   if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
   else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  }
 });
 mobile.addEventListener('change', () => setOpen(false, false));
 setOpen(false, false);
})();
