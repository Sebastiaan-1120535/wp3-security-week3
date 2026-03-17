import { loadFragment } from './fragmentLoader.js';

const ITEM_HEIGHT = 72;
let pageSize = 10;
let offset = 0;
let loading = false;
let hasMore = true;

export async function loadLatestResults(targetSelector, url = '/api/partial/latest-results') {
    await loadFragment(targetSelector, url, async ({ target, data }) => {
        if (!data) return;

        offset = 0;
        hasMore = true;
        loading = false;

        const list = target.querySelector('#results-list');
        if (list) {
            const visibleHeight = list.clientHeight;
            const fitCount = Math.max(3, Math.floor(visibleHeight / ITEM_HEIGHT));
            pageSize = fitCount * 2;
        }

        await fetchResults(target);
        initScrollListener(target);
    });
}

async function fetchResults(container) {
    if (loading || !hasMore) return;
    loading = true;

    const list = container.querySelector('#results-list');
    const loader = container.querySelector('#results-loader');
    const empty = container.querySelector('#results-empty');

    const isInitial = offset === 0;
    if (isInitial && loader) loader.classList.remove('hidden');

    const student_id = Number(new URL(window.location.href).pathname.split('/').pop());
    const baseurl = !isNaN(student_id) ? `/api/student/${student_id}/recent-results` : '/api/student/recent-results';

    try {
        const response = await fetch(`${baseurl}?offset=${offset}&limit=${pageSize}`);
        if (!response.ok) {
            loading = false;
            return;
        }
        const data = await response.json();

        if (isInitial && loader) loader.classList.add('hidden');
        loading = false;

        if (!data) return;

        hasMore = data.has_more;
        const results = data.results;

        if (offset === 0 && results.length === 0) {
            if (empty) empty.classList.remove('hidden');
            return;
        }

        results.forEach(item => {
            list.insertAdjacentHTML('beforeend', renderResultItem(item));
        });

        offset += results.length;
    } catch {
        if (isInitial && loader) loader.classList.add('hidden');
        loading = false;
    }
}

function renderResultItem(item) {
    let badgeClass = '';
    if (item.score === 'Sterk') badgeClass = 'badge-success';
    else if (item.score === 'Voldoende') badgeClass = 'badge-warning';
    else badgeClass = 'badge-danger';

    const scoreHtml = item.has_data
        ? `<div class="flex items-center gap-2"><span class="badge ${badgeClass}">${item.score}</span><span class="text-sm" style="color: var(--color-text-muted);">${item.score_numeric}%</span></div>`
        : '<span class="text-sm" style="color: var(--color-text-muted);">Geen data</span>';

    return `
    <article class="rounded-lg border bg-gray-50 px-4 py-3" style="border-color: var(--color-border);">
        <h2 class="font-bold leading-tight mb-1">${item.title}</h2>
        <p class="truncate font-semibold mb-1">${item.subject}</p>
        <div class="flex items-start justify-between gap-4">
            <div class="min-w-0">
                <div class="mt-1 flex items-center gap-2 text-sm" style="color: var(--color-text-muted);">
                    <span>${item.date || ''}</span>
                </div>
            </div>
            <div class="shrink-0">
                ${scoreHtml}
            </div>
        </div>
    </article>
    `;
}

function initScrollListener(container) {
    const list = container.querySelector('#results-list');
    if (!list) return;

    list.addEventListener('scroll', () => {
        const halfContent = list.scrollHeight / 2;
        if (list.scrollTop + list.clientHeight >= halfContent) {
            fetchResults(container);
        }
    });
}
