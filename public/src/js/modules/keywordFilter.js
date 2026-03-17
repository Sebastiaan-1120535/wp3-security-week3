import { loadFragment } from './fragmentLoader.js';

function initKeywordFilter(container) {
    const filter = container.querySelector('#keyword-filter');
    const sort = container.querySelector('#keyword-sort');
    const list = container.querySelector('#keyword-list');
    if (!filter || !sort || !list) return;

    function apply() {
        const cards = Array.from(list.querySelectorAll('.keyword-card'));
        const filterVal = filter.value;
        const sortVal = sort.value;

        cards.forEach(c => {
            if (filterVal === 'all' || c.dataset.score === filterVal) {
                c.style.display = '';
            } else {
                c.style.display = 'none';
            }
        });

        cards.sort((a, b) => {
            if (sortVal === 'alpha') return a.dataset.topic.localeCompare(b.dataset.topic);
            const aNum = parseFloat(a.dataset.numeric);
            const bNum = parseFloat(b.dataset.numeric);
            return sortVal === 'score-asc' ? aNum - bNum : bNum - aNum;
        }).forEach(c => list.appendChild(c));
    }

    filter.addEventListener('change', apply);
    sort.addEventListener('change', apply);
}

export async function loadStudentGoals(targetSelector, url) {
    const result = await loadFragment(targetSelector, url);
    if (result && result.target) {
        initKeywordFilter(result.target);
    }
}
