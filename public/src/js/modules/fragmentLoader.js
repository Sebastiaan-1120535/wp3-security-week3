import { useApiHandler } from './apiHandler.js';

export async function loadFragment(targetSelector, url, onSuccess) {
    const target = document.querySelector(targetSelector);
    if (!target) return null;

    target.innerHTML = '<div class="flex justify-center p-4"><div class="animate-spin h-6 w-6 border-2 rounded-full" style="border-color: var(--color-accent); border-top-color: transparent;"></div></div>';

    const request = useApiHandler(url);
    const { data, error } = await request.Get();

    if (error) {
        target.innerHTML = `<p style="color: var(--color-danger);">${error.message}</p>`;
        return { target, data: null, error };
    }

    if (data) {
        target.innerHTML = data;
        if (typeof onSuccess === 'function') {
            await onSuccess({ target, data, url });
        }
    }

    return { target, data, error: null };
}