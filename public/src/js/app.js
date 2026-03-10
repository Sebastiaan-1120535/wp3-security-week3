import { loadFragment } from './modules/fragmentLoader.js';
import { loadLatestResults } from './modules/latestResults.js';
import { loadStudentProgress } from './modules/studentProgress.js';

const API_BASE_URL = '/api/partial';
const widgets = [
  {
    callback: 'loadLatestResults',
    target: '#latest-results',
    refreshId: 'refresh-latest-results',
    url: `${API_BASE_URL}/latest-results`
  },
  {
    callback: 'loadStudentProgress',
    target: '#student-progress',
    refreshId: 'refresh-student-progress',
    url: `${API_BASE_URL}/student-progress`
  },
  {
    callback: 'fragment',
    target: '#student-goals',
    refreshId: 'refresh-student-goals',
    url: `${API_BASE_URL}/student-goals`
  },
  {
    callback: 'fragment',
    target: '#students-list',
    refreshId: 'refresh-students-list',
    url: `${API_BASE_URL}/students`
  },
  {
    callback: 'fragment',
    target: '#teachers-list',
    refreshId: 'refresh-teachers-list',
    url: `${API_BASE_URL}/teachers`
  },
  {
    callback: 'fragment',
    target: '#classes-list',
    refreshId: 'refresh-classes-list',
    url: `${API_BASE_URL}/classes`
  }, 
  {
    callback: 'fragment',
    target: '#class-students-list',
    refreshId: 'refresh-class-students-list',
    url: `${API_BASE_URL}/${new URL(window.location.href).pathname}/students`
  },
  {
    callback: 'fragment',
    target: '#class-student-goals',
    refreshId: 'refresh-class-student-goals',
    url: `${API_BASE_URL}/${new URL(window.location.href).pathname}/goals`
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

