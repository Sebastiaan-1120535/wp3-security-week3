import { loadFragment } from './modules/fragmentLoader.js';
import { loadLatestResults } from './modules/latestResults.js';
import { loadStudentProgress, loadStudentaverage } from './modules/chartdisplay.js';

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
    url: `${API_BASE_URL}/student-progress`,
    selectUrl: `/api/student/progress/subject`,
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
  },
  {
    callback: 'loadStudentaverage',
    target: '#class-goals-progress',
    refreshId: 'refresh-class-goals-progress',
    url: `${API_BASE_URL}/${new URL(window.location.href).pathname}/goals-progress`,
    selectUrl: `/api/${new URL(window.location.href).pathname}/goal`,
  },
]

const callbacks = new Map([
  ['loadLatestResults', loadLatestResults],
  ['loadStudentProgress', loadStudentProgress],
  ['loadStudentaverage', loadStudentaverage],
  ['fragment', loadFragment]
])

document.addEventListener('DOMContentLoaded', function () {

  widgets.forEach(widget => {
    const { callback, target, url, refreshId, selectUrl } = widget;
    callbacks.get(callback)(target, url, selectUrl);

    const button = document.getElementById(refreshId);
    if (button) button.addEventListener('click', () => callbacks.get(callback)(target, url, selectUrl));
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

