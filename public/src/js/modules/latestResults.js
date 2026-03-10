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

    try {
        const response = await fetch(`/api/student/recent-results?offset=${offset}&limit=${pageSize}`);
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

    const keywords = item.keywords && item.keywords.length
        ? `<div class="flex flex-wrap gap-1 mt-1">${item.keywords.map(kw => `<span class="badge badge-info">${kw}</span>`).join('')}</div>`
        : '';

    const scoreHtml = item.has_data
        ? `<div class="flex items-center gap-2"><span class="badge ${badgeClass}">${item.score}</span><span class="text-sm" style="color: var(--color-text-muted);">${item.score_numeric}%</span></div>`
        : '<span class="text-sm" style="color: var(--color-text-muted);">Geen data</span>';

    return `<div class="flex items-center justify-between rounded-lg px-4 py-3" style="border: 1px solid var(--color-border);">
        <div>
            <p class="font-semibold">${item.title}</p>
            <div class="flex items-center gap-2 mt-1">
                <span class="text-sm" style="color: var(--color-text-muted);">${item.subject}</span>
                <span class="text-sm" style="color: var(--color-text-muted);">&middot;</span>
                <span class="text-sm" style="color: var(--color-text-muted);">${item.date || ''}</span>
            </div>
            ${keywords}
        </div>
        ${scoreHtml}
    </div>`;
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
