import { loadFragment } from './modules/fragmentLoader.js';
import { loadLatestResults } from './modules/latestResults.js';
import { loadStudentProgress } from './modules/studentProgress.js';

const widgets = [
  {
    callback: 'loadLatestResults',
    target: '#latest-results',
    refreshId: 'refresh-latest-results',
    url: '/api/partial/latest-results'
  },
  {
    callback: 'loadStudentProgress',
    target: '#student-progress',
    refreshId: 'refresh-student-progress',
    url: '/api/partial/student-progress'
  },
  {
    callback: 'fragment',
    target: '#student-goals',
    refreshId: 'refresh-student-goals',
    url: '/api/partial/student-goals'
  },
  {
    callback: 'fragment',
    target: '#students-list',
    refreshId: 'refresh-students-list',
    url: '/api/partial/students'
  },
  {
    callback: 'fragment',
    target: '#teachers-list',
    refreshId: 'refresh-teachers-list',
    url: '/api/partial/teachers'
  },
  {
    callback: 'fragment',
    target: '#classes-list',
    refreshId: 'refresh-classes-list',
    url: '/api/partial/classes'
  }
]

const callbacks = new Map([
  ['loadLatestResults', loadLatestResults],
  ['loadStudentProgress', loadStudentProgress],
  ['fragment', loadFragment]
])

document.addEventListener('DOMContentLoaded', function () {

  widgets.forEach(widget => {
    const { callback, target, url, refreshId } = widget;
    callbacks.get(callback)(target, url);

    const button = document.getElementById(refreshId);
    if (button) button.addEventListener('click', () => callbacks.get(callback)(target, url));
  });

  const toasts = document.querySelectorAll('.toast');
  toasts.forEach(toast => {
    setTimeout(() => {
      toast.style.transition = 'opacity 0.3s ease-out';
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  });
});

