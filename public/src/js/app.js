import { useApiHandler } from './modules/apiHandler.js';

async function loadFragment(targetSelector, url) {
  const target = document.querySelector(targetSelector);
  if (!target) return;

  target.innerHTML = '<div class="flex justify-center p-4"><div class="animate-spin h-6 w-6 border-2 rounded-full" style="border-color: var(--color-accent); border-top-color: transparent;"></div></div>';

  const request = useApiHandler(url)
  const { data, error } = await request.Get()

  if (error) target.innerHTML = `<p style="color: var(--color-danger);">${error.message}</p>`;
  else if (data) target.innerHTML = data;

}

document.addEventListener('click', function(e) {
  const button = e.target.closest('[data-refresh]');
  if (button) {
    const target = button.getAttribute('data-refresh');
    const url = button.getAttribute('data-url');
    if (target && url) {
      loadFragment(target, url);
    }
  }
});

// Toast auto-dismiss after 3 seconds
document.addEventListener('DOMContentLoaded', function() {
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach(toast => {
    setTimeout(() => {
      toast.style.transition = 'opacity 0.3s ease-out';
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  });
});

