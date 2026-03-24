from __future__ import annotations

import html
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from .daemon import CourseQualityDaemon


HTML = """<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Amanoba Control Center</title>
  <style>
    :root {
      --bg: #efe6d7;
      --panel: #fffaf2;
      --ink: #1e1d1a;
      --muted: #6f6556;
      --line: #d3c3ae;
      --accent: #145c52;
      --accent-soft: #e2efe7;
      --warn: #9e631e;
      --bad: #9b2f2f;
      --good: #27603d;
      --shadow: 0 14px 32px rgba(64, 46, 20, 0.09);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, #fff8de 0, var(--bg) 45%, #eadfcd 100%);
    }
    .shell {
      display: grid;
      grid-template-columns: 320px 1fr;
      min-height: 100vh;
    }
    .rail {
      position: sticky;
      top: 0;
      height: 100vh;
      padding: 24px;
      border-right: 1px solid var(--line);
      background: rgba(255,250,242,0.93);
      backdrop-filter: blur(12px);
      overflow: auto;
    }
    .brand { font-size: 29px; font-weight: 800; letter-spacing: 0.02em; }
    .sub { margin-top: 8px; color: var(--muted); line-height: 1.5; }
    .section { margin-top: 22px; }
    .section h2 { margin: 0 0 10px; font-size: 15px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }
    .actions, .power-grid { display: grid; gap: 10px; }
    button {
      border: 0;
      border-radius: 14px;
      padding: 12px 14px;
      font-weight: 700;
      cursor: pointer;
      background: var(--accent);
      color: #fff;
    }
    button.secondary { background: #e6d8c4; color: var(--ink); }
    button.ghost { background: #f2e7d8; color: var(--ink); }
    button.danger { background: var(--bad); color: #fff; }
    button.small { padding: 9px 11px; font-size: 12px; border-radius: 10px; }
    .main { padding: 24px; overflow-x: auto; overflow-y: auto; }
    .hero { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 18px; }
    .hero h1 { margin: 0; font-size: 34px; }
    .hero p { margin: 6px 0 0; color: var(--muted); }
    .metrics { display: grid; grid-template-columns: repeat(5, minmax(180px,1fr)); gap: 12px; margin-bottom: 18px; }
    .metric-card, .rail-card, .column, .modal-card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: var(--shadow);
    }
    .metric-card { padding: 16px; }
    .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }
    .metric { margin-top: 8px; font-size: 28px; font-weight: 800; }
    .rail-card { padding: 14px; margin-top: 10px; }
    .runtime-item { padding: 10px 0; border-top: 1px solid var(--line); }
    .runtime-item:first-child { border-top: 0; padding-top: 0; }
    .status.good { color: var(--good); }
    .status.warn { color: var(--warn); }
    .status.bad { color: var(--bad); }
    .kanban {
      display: grid;
      grid-template-columns: repeat(5, minmax(280px, 1fr));
      gap: 14px;
      align-items: start;
      min-width: 1480px;
    }
    .column { padding: 14px; min-height: 420px; min-width: 0; overflow: hidden; }
    .column-head { display: flex; justify-content: space-between; gap: 8px; align-items: baseline; margin-bottom: 10px; }
    .column-head h2 { margin: 0; font-size: 18px; }
    .column-count { color: var(--muted); font-size: 12px; }
    .cards { display: grid; gap: 10px; }
    .job-card {
      border: 1px solid var(--line);
      border-radius: 14px;
      background: linear-gradient(180deg, #fffdf8 0%, #fbf4e9 100%);
      padding: 12px;
      cursor: pointer;
      min-width: 0;
      overflow: hidden;
    }
    .job-card:hover { border-color: var(--accent); transform: translateY(-1px); }
    .job-title {
      font-weight: 800;
      line-height: 1.35;
      overflow-wrap: anywhere;
      word-break: break-word;
    }
    .job-meta, .tiny {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
      overflow-wrap: anywhere;
      word-break: break-word;
    }
    .search-box {
      display: grid;
      gap: 8px;
      margin-bottom: 10px;
    }
    input, textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px 12px;
      font: inherit;
      background: #fffdfa;
      color: var(--ink);
    }
    textarea { min-height: 90px; resize: vertical; }
    pre {
      white-space: pre-wrap;
      word-break: break-word;
      background: #f7efe3;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px;
      font-size: 12px;
      max-height: 240px;
      overflow: auto;
    }
    .human-card {
      background: #fffdf8;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 14px;
      display: grid;
      gap: 10px;
    }
    .human-question {
      font-size: 18px;
      font-weight: 700;
      line-height: 1.45;
    }
    .choice-list {
      display: grid;
      gap: 8px;
    }
    .choice-item {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px 12px;
      background: #fbf4e9;
      line-height: 1.45;
    }
    .choice-item.correct {
      border-color: var(--good);
      background: #e9f5ec;
    }
    .human-meta {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }
    .change-list {
      display: grid;
      gap: 8px;
    }
    .change-item {
      border-left: 3px solid var(--accent);
      padding-left: 10px;
      line-height: 1.45;
    }
    .empty { color: var(--muted); font-size: 13px; padding: 8px 0; }
    .modal {
      position: fixed;
      inset: 0;
      background: rgba(30, 24, 18, 0.5);
      display: none;
      align-items: center;
      justify-content: center;
      padding: 18px;
      z-index: 30;
    }
    .modal.open { display: flex; }
    .modal-card {
      width: min(1100px, 100%);
      max-height: 92vh;
      overflow: auto;
      padding: 18px;
    }
    .modal-top {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
      margin-bottom: 16px;
    }
    .detail-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0,1fr));
      gap: 14px;
    }
    .detail-grid.single { grid-template-columns: 1fr; }
    .stack { display: grid; gap: 10px; }
    .row-actions { display: flex; gap: 8px; flex-wrap: wrap; }
    @media (max-width: 1280px) {
      .metrics { grid-template-columns: repeat(2, minmax(180px,1fr)); }
    }
    @media (max-width: 960px) {
      .shell { grid-template-columns: 1fr; }
      .rail { position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--line); }
      .metrics { grid-template-columns: repeat(2, minmax(150px,1fr)); }
      .kanban { grid-template-columns: repeat(5, minmax(260px, 1fr)); min-width: 1320px; }
      .detail-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class='shell'>
    <aside class='rail'>
      <div class='brand'>Amanoba</div>
      <div class='sub'>Quality-first local control center. One question or lesson at a time, continuously, with human challenge and archive review.</div>

      <div class='section'>
        <h2>Actions</h2>
        <div class='actions'>
          <button onclick='postAction("/api/scan")'>Scan Workspace</button>
          <button onclick='postAction("/api/run-once?maxItems=1")'>Process One Job</button>
          <button class='secondary' onclick='refreshAll()'>Refresh Feed</button>
        </div>
      </div>

      <div class='section'>
        <h2>Power Mode</h2>
        <div class='power-grid'>
          <button class='ghost' onclick='setPowerMode("gentle")'>Gentle</button>
          <button class='ghost' onclick='setPowerMode("balanced")'>Balanced</button>
          <button class='ghost' onclick='setPowerMode("fast")'>Fast</button>
        </div>
        <div class='rail-card tiny' id='powerSummary'>__POWER_SUMMARY__</div>
      </div>

      <div class='section'>
        <h2>Runtime Providers</h2>
        <div class='rail-card' id='runtimeProviders'>__RUNTIME_HTML__</div>
      </div>

      <div class='section'>
        <h2>Last Action</h2>
        <div class='rail-card'><pre id='lastAction'>__LAST_ACTION__</pre></div>
      </div>
    </aside>

    <main class='main'>
      <div class='hero'>
        <div>
          <h1>Course Quality Control Center</h1>
          <p id='generatedAt'>__GENERATED_AT__</p>
        </div>
        <div class='tiny' id='workspace'>__WORKSPACE__</div>
      </div>

      <div class='metrics'>
        <div class='metric-card'><div class='label'>Coming Up</div><div class='metric' id='queuedCount'>__QUEUED_COUNT__</div></div>
        <div class='metric-card'><div class='label'>Active Now</div><div class='metric' id='runningCount'>__RUNNING_COUNT__</div></div>
        <div class='metric-card'><div class='label'>Done</div><div class='metric' id='completedCount'>__COMPLETED_COUNT__</div></div>
        <div class='metric-card'><div class='label'>Failed</div><div class='metric' id='failedCount'>__FAILED_COUNT__</div></div>
        <div class='metric-card'><div class='label'>Archived</div><div class='metric' id='archivedCount'>__ARCHIVED_COUNT__</div></div>
      </div>

      <div class='kanban'>
        <section class='column'>
          <div class='column-head'><h2>Coming Up</h2><div class='column-count'>next items</div></div>
          <div class='cards' id='queuedJobs'>__QUEUED_HTML__</div>
        </section>
        <section class='column'>
          <div class='column-head'><h2>Active Now</h2><div class='column-count'>currently running</div></div>
          <div class='cards' id='runningJobs'>__RUNNING_HTML__</div>
        </section>
        <section class='column'>
          <div class='column-head'><h2>Done</h2><div class='column-count'>last 10</div></div>
          <div class='cards' id='completedJobs'>__COMPLETED_HTML__</div>
        </section>
        <section class='column'>
          <div class='column-head'><h2>Failed</h2><div class='column-count'>last 10</div></div>
          <div class='cards' id='failedJobs'>__FAILED_HTML__</div>
        </section>
        <section class='column'>
          <div class='column-head'><h2>Archived</h2><div class='column-count'>last 50 done</div></div>
          <div class='search-box'>
            <input id='archiveSearch' placeholder='Search all done jobs in DB'>
            <button class='secondary small' onclick='searchArchive()'>Search Archive</button>
          </div>
          <div class='cards' id='archivedJobs'>__ARCHIVED_HTML__</div>
        </section>
      </div>
    </main>
  </div>

  <div class='modal' id='detailModal'>
    <div class='modal-card'>
      <div class='modal-top'>
        <div>
          <h2 id='modalTitle' style='margin:0;'>Task Detail</h2>
          <div class='tiny' id='modalMeta'></div>
        </div>
        <div class='row-actions'>
          <button class='secondary small' onclick='closeModal()'>Close</button>
        </div>
      </div>
      <div class='stack'>
        <div class='rail-card tiny' id='modalSummary'>Loading...</div>
        <div class='detail-grid' id='modalDiffGrid'>
          <div>
            <div class='label'>Before</div>
            <div class='human-card' id='modalBeforeHuman'></div>
            <pre id='modalBefore'></pre>
          </div>
          <div>
            <div class='label'>After</div>
            <div class='human-card' id='modalAfterHuman'></div>
            <pre id='modalAfter'></pre>
          </div>
        </div>
        <div class='detail-grid single'>
          <div>
            <div class='label'>Change Summary</div>
            <div class='human-card' id='modalChangeSummary'></div>
          </div>
        </div>
        <div class='detail-grid single'>
          <div>
            <div class='label'>Feedback And Challenge</div>
            <pre id='modalFeedbackHistory'>No feedback yet.</pre>
            <textarea id='challengeComment' placeholder='Challenge this result with one comment. Example: The scenario is still too generic and the distractors are weak.'></textarea>
            <div class='row-actions'>
              <button class='danger small' onclick='challengeCurrentTask()'>Challenge And Requeue</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

<script>
const INITIAL_FEED = __INITIAL_FEED__;
const INITIAL_HEALTH = __INITIAL_HEALTH__;
let currentDetailTaskKey = null;

async function fetchJson(path, options = {}) {
  const res = await fetch(path, { cache: 'no-store', ...options });
  const text = await res.text();
  let data = {};
  try {
    data = text ? JSON.parse(text) : {};
  } catch (error) {
    throw new Error(`Invalid JSON from ${path}: ${String(error)}`);
  }
  if (!res.ok) {
    const detail = data && data.error ? data.error : text || `${res.status} ${res.statusText}`;
    throw new Error(`Request failed for ${path}: ${detail}`);
  }
  return data;
}
function clsFor(status) {
  if (status === 'HEALTHY' || status === 'STANDBY' || status === 'completed') return 'good';
  if (status === 'DEGRADED' || status === 'pending' || status === 'running') return 'warn';
  return 'bad';
}
function cardTitle(job) {
  return job.humanTitle || job.questionUuid || job.lessonId || job.taskKey || 'Untitled task';
}
function renderJobs(id, jobs, emptyText) {
  const el = document.getElementById(id);
  if (!jobs || !jobs.length) {
    el.innerHTML = `<div class='empty'>${emptyText}</div>`;
    return;
  }
  el.innerHTML = jobs.map(job => {
    const judgement = job.details && job.details.judgement ? `${job.details.judgement.confidence} ${job.details.judgement.trustTier}` : 'no confidence';
    const changes = job.details && job.details.changedFields ? `changed ${job.details.changedFields.join(', ')}` : '';
    const courseName = job.humanCourseName || job.courseId || 'Unknown course';
    const dayLabel = job.humanDayLabel || job.lessonId || '-';
    const lessonTitle = job.humanLessonTitle || job.lessonId || '-';
    const displayStatus = job.displayStatus || job.status;
    const updated = job.humanUpdatedAt ? `updated ${job.humanUpdatedAt}` : '';
    const error = job.lastError ? `<div class='job-meta status bad'>${job.lastError}</div>` : '';
    const lessonLine = job.kind === 'question' ? `<div class='job-meta'>${escapeHtml(lessonTitle)}</div>` : '';
    return `<div class='job-card' data-task-key='${escapeHtml(job.taskKey)}' tabindex='0' role='button' onclick='openTaskDetail(this.getAttribute("data-task-key")); return false;' onkeydown='if(event.key==="Enter"||event.key===" "){ event.preventDefault(); openTaskDetail(this.getAttribute("data-task-key")); return false; }'>
      <div class='job-title'>${escapeHtml(cardTitle(job)).replaceAll('\\n', '<br>')}</div>
      <div class='job-meta'>${escapeHtml(courseName)}</div>
      <div class='job-meta'>${escapeHtml(dayLabel)}</div>
      ${lessonLine}
      <div class='job-meta'>${escapeHtml(job.kind)} | ${escapeHtml(displayStatus)} | attempts ${job.attempts}</div>
      <div class='job-meta'>confidence ${escapeHtml(judgement)}</div>
      <div class='job-meta'>${escapeHtml(changes || updated || ('updated ' + (job.updatedAt || '-')))}</div>
      ${changes && updated ? `<div class='job-meta'>${escapeHtml(updated)}</div>` : ''}
      ${error}
    </div>`;
  }).join('');
}
function renderRuntime(runtime) {
  const host = document.getElementById('runtimeProviders');
  const providers = Array.isArray(runtime && runtime.providers) ? runtime.providers : [];
  if (!providers.length) {
    host.innerHTML = "<div class='runtime-item'><div><strong>No runtime data</strong> <span class='status bad'>ERROR</span></div></div>";
    return;
  }
  host.innerHTML = providers.map(item => `
    <div class='runtime-item'>
      <div><strong>${escapeHtml(item.provider)}</strong> <span class='status ${clsFor(item.status)}'>${escapeHtml(item.status)}</span></div>
      <div class='tiny'>${escapeHtml(item.detail)}</div>
      <div class='tiny'>model: ${escapeHtml(item.resolvedModel || item.configuredModel || '-')}</div>
      <div class='tiny'>endpoint: ${escapeHtml(item.endpoint || '-')}</div>
    </div>
  `).join('');
}
function renderPower(power) {
  const profiles = power && power.profiles ? power.profiles : {};
  const profile = profiles[power.mode] || {};
  document.getElementById('powerSummary').innerHTML = `Mode: <strong>${escapeHtml(power.mode)}</strong><br>threads ${escapeHtml(String(profile.num_thread ?? '-'))} | tokens ${escapeHtml(String(profile.num_predict ?? '-'))} | ctx ${escapeHtml(String(profile.num_ctx ?? '-'))}`;
}
function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}
function htmlToReadableText(value) {
  const raw = String(value ?? '');
  if (!raw) return '';
  return raw
    .replace(/<\\s*br\\s*\\/?>/gi, '\\n')
    .replace(/<\\s*\\/p\\s*>/gi, '\\n\\n')
    .replace(/<\\s*\\/h[1-6]\\s*>/gi, '\\n\\n')
    .replace(/<\\s*li[^>]*>/gi, '\\n- ')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\\n{3,}/g, '\\n\\n')
    .trim();
}
function formatReadableBlock(value) {
  return escapeHtml(String(value ?? '').trim() || '-').replaceAll('\\n', '<br>');
}
function renderHumanContent(targetId, content, kind) {
  const el = document.getElementById(targetId);
  if (!content) {
    el.innerHTML = `<div class='empty'>${kind === 'lesson' ? 'No readable lesson view.' : 'No readable question view.'}</div>`;
    return;
  }
  if (kind === 'lesson') {
    const title = content.title || '';
    const body = content.content || '';
    const emailSubject = content.emailSubject || '';
    const emailBody = content.emailBody || '';
    const readableBody = htmlToReadableText(body) || body;
    const readableEmailBody = htmlToReadableText(emailBody) || emailBody;
    if (!title && !body && !emailSubject && !emailBody) {
      el.innerHTML = `<div class='empty'>No readable lesson view.</div>`;
      return;
    }
    el.innerHTML = `
      <div class='human-question'>${escapeHtml(title || 'Untitled lesson')}</div>
      <div class='human-meta'>${escapeHtml(emailSubject ? `Email subject: ${emailSubject}` : 'No email subject.')}</div>
      <div class='choice-item'>${formatReadableBlock(readableBody || 'No lesson content.')}</div>
      <div class='human-meta'>Email body:</div>
      <div class='choice-item'>${formatReadableBlock(readableEmailBody || 'No email body.')}</div>
    `;
    return;
  }
  const question = content;
  const options = Array.isArray(question.options) ? question.options : [];
  const correctIndex = Number.isInteger(question.correctIndex) ? question.correctIndex : -1;
  if (!question.question) {
    el.innerHTML = `<div class='empty'>No readable question view.</div>`;
    return;
  }
  el.innerHTML = `
    <div class='human-question'>${escapeHtml(question.question)}</div>
    <div class='choice-list'>
      ${options.map((option, index) => `
        <div class='choice-item ${index === correctIndex ? 'correct' : ''}'>
          <strong>${String.fromCharCode(65 + index)}.</strong> ${escapeHtml(option)}
        </div>
      `).join('')}
    </div>
    <div class='human-meta'>
      type ${escapeHtml(question.questionType || '-')} | difficulty ${escapeHtml(question.difficulty || '-')} | category ${escapeHtml(question.category || '-')}
    </div>
  `;
}
function renderChangeSummary(task) {
  const el = document.getElementById('modalChangeSummary');
  const before = task.details && task.details.before ? task.details.before : {};
  const after = task.details && task.details.after ? task.details.after : {};
  const changedFields = task.details && task.details.changedFields ? task.details.changedFields : [];
  if (!changedFields.length) {
    el.innerHTML = `<div class='empty'>No material change summary.</div>`;
    return;
  }
  const lines = [];
  if (changedFields.includes('question')) {
    lines.push(`<div class='change-item'><strong>Question:</strong><br>Before: ${escapeHtml(before.question || '-')}<br>After: ${escapeHtml(after.question || '-')}</div>`);
  }
  if (changedFields.includes('options')) {
    const beforeCount = Array.isArray(before.options) ? before.options.length : 0;
    const afterCount = Array.isArray(after.options) ? after.options.length : 0;
    lines.push(`<div class='change-item'><strong>Options:</strong><br>Before: ${beforeCount} option(s)<br>After: ${afterCount} option(s)</div>`);
  }
  for (const field of changedFields) {
    if (field === 'question' || field === 'options') continue;
    lines.push(`<div class='change-item'><strong>${escapeHtml(field)}:</strong><br>Before: ${escapeHtml(JSON.stringify(before[field] ?? '-'))}<br>After: ${escapeHtml(JSON.stringify(after[field] ?? '-'))}</div>`);
  }
  el.innerHTML = `<div class='change-list'>${lines.join('')}</div>`;
}
function applySnapshot(feed, health, lastActionText = 'Feed refreshed.') {
  document.getElementById('generatedAt').textContent = `Updated ${feed.generatedAt}`;
  document.getElementById('workspace').textContent = health.workspaceRoot || '';
  document.getElementById('queuedCount').textContent = feed.counts.pending || 0;
  document.getElementById('runningCount').textContent = feed.counts.running || 0;
  document.getElementById('completedCount').textContent = feed.counts.completed || 0;
  document.getElementById('failedCount').textContent = feed.failedCount || feed.counts.failed || 0;
  document.getElementById('archivedCount').textContent = feed.archivedCount || 0;
  renderJobs('queuedJobs', feed.queued, 'No queued jobs.');
  renderJobs('runningJobs', feed.running, 'No running jobs.');
  renderJobs('completedJobs', feed.completed, 'No completed jobs yet.');
  renderJobs('failedJobs', feed.failed, 'No failed jobs.');
  renderJobs('archivedJobs', feed.archived, 'No archived jobs.');
  renderRuntime(health.runtime || {});
  renderPower(health.power || { mode: '-', profiles: {} });
  document.getElementById('lastAction').textContent = lastActionText;
}
async function refreshAll() {
  try {
    const [feed, health] = await Promise.all([fetchJson('/api/feed'), fetchJson('/api/health')]);
    applySnapshot(feed, health, 'Feed refreshed.');
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    document.getElementById('generatedAt').textContent = 'Refresh failed';
    document.getElementById('lastAction').textContent = message;
    document.getElementById('runtimeProviders').innerHTML = `<div class='runtime-item'><div><strong>Dashboard error</strong> <span class='status bad'>ERROR</span></div><div class='tiny'>${escapeHtml(message)}</div></div>`;
  }
}
async function postAction(path, body = null) {
  const options = { method: 'POST' };
  if (body !== null) {
    options.headers = { 'Content-Type': 'application/json' };
    options.body = JSON.stringify(body);
  }
  const data = await fetchJson(path, options);
  document.getElementById('lastAction').textContent = JSON.stringify(data, null, 2);
  await refreshAll();
  return data;
}
async function setPowerMode(mode) {
  await postAction(`/api/power-mode?mode=${encodeURIComponent(mode)}`);
}
async function searchArchive() {
  const query = document.getElementById('archiveSearch').value.trim();
  if (!query) {
    await refreshAll();
    return;
  }
  const result = await fetchJson(`/api/search-completed?q=${encodeURIComponent(query)}`);
  renderJobs('archivedJobs', result.results || [], 'No archived matches.');
  document.getElementById('lastAction').textContent = JSON.stringify(result, null, 2);
}
async function openTaskDetail(taskKey) {
  currentDetailTaskKey = taskKey;
  document.getElementById('detailModal').classList.add('open');
  document.getElementById('modalTitle').textContent = 'Task Detail';
  document.getElementById('modalMeta').textContent = taskKey;
  document.getElementById('modalSummary').textContent = 'Loading...';
  document.getElementById('modalBeforeHuman').innerHTML = `<div class='empty'>Loading...</div>`;
  document.getElementById('modalAfterHuman').innerHTML = `<div class='empty'>Loading...</div>`;
  document.getElementById('modalChangeSummary').innerHTML = `<div class='empty'>Loading...</div>`;
  try {
    const result = await fetchJson(`/api/task?taskKey=${encodeURIComponent(taskKey)}`);
    const task = result.task;
    if (!task) {
      document.getElementById('modalSummary').textContent = 'Task not found.';
      return;
    }
    document.getElementById('modalTitle').textContent = task.humanTitle || cardTitle(task);
    document.getElementById('modalMeta').textContent = `${task.kind} | ${task.displayStatus || task.status} | attempts ${task.attempts}`;
    const changedFields = task.details && task.details.changedFields ? task.details.changedFields.join(', ') : '-';
    const warnings = task.details && task.details.warnings ? task.details.warnings.join('; ') : 'none';
    const rca = task.details && task.details.rca ? task.details.rca : null;
    const quarantine = task.details && task.details.quarantine ? task.details.quarantine : null;
    const summaryLines = [
      `Changed fields: ${changedFields}`,
      `Warnings: ${warnings}`,
      `Backup: ${task.details && task.details.backup ? task.details.backup : '-'}`,
    ];
    if (rca) summaryLines.push(`RCA: ${rca.type || '-'} | ${rca.summary || '-'}`);
    if (quarantine) summaryLines.push(`Quarantine: ${quarantine.status || 'active'} | attempts ${quarantine.attempts || task.attempts}`);
    document.getElementById('modalSummary').textContent = summaryLines.join('\\n');
    renderHumanContent('modalBeforeHuman', task.details && task.details.before ? task.details.before : null, task.kind);
    renderHumanContent('modalAfterHuman', task.details && task.details.after ? task.details.after : null, task.kind);
    renderChangeSummary(task);
    document.getElementById('modalBefore').textContent = JSON.stringify(task.details && task.details.before ? task.details.before : {}, null, 2);
    document.getElementById('modalAfter').textContent = JSON.stringify(task.details && task.details.after ? task.details.after : {}, null, 2);
    const feedback = (task.feedback || []).map(item => `${item.createdAt}: ${item.comment}`).join('\\n\\n');
    document.getElementById('modalFeedbackHistory').textContent = feedback || 'No feedback yet.';
    document.getElementById('challengeComment').value = '';
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    document.getElementById('modalSummary').textContent = `Failed to load task detail.\n${message}`;
    document.getElementById('modalBeforeHuman').innerHTML = `<div class='empty'>Failed to load detail.</div>`;
    document.getElementById('modalAfterHuman').innerHTML = `<div class='empty'>Failed to load detail.</div>`;
    document.getElementById('modalChangeSummary').innerHTML = `<div class='empty'>Failed to load detail.</div>`;
    document.getElementById('modalBefore').textContent = '';
    document.getElementById('modalAfter').textContent = '';
    document.getElementById('modalFeedbackHistory').textContent = '';
  }
}
function closeModal() {
  currentDetailTaskKey = null;
  document.getElementById('detailModal').classList.remove('open');
}
async function challengeCurrentTask() {
  if (!currentDetailTaskKey) return;
  const comment = document.getElementById('challengeComment').value.trim();
  if (!comment) {
    window.alert('Challenge comment is required.');
    return;
  }
  await postAction('/api/challenge', { taskKey: currentDetailTaskKey, comment });
  closeModal();
}
document.getElementById('detailModal').addEventListener('click', (event) => {
  if (event.target.id === 'detailModal') closeModal();
});
document.addEventListener('click', (event) => {
  const card = event.target instanceof Element ? event.target.closest('.job-card[data-task-key]') : null;
  if (!card) return;
  const taskKey = card.getAttribute('data-task-key');
  if (taskKey) openTaskDetail(taskKey);
});
document.addEventListener('keydown', (event) => {
  if (event.key !== 'Enter' && event.key !== ' ') return;
  const card = event.target instanceof Element ? event.target.closest('.job-card[data-task-key]') : null;
  if (!card) return;
  event.preventDefault();
  const taskKey = card.getAttribute('data-task-key');
  if (taskKey) openTaskDetail(taskKey);
});
applySnapshot(INITIAL_FEED, INITIAL_HEALTH, 'Live snapshot loaded.');
refreshAll();
setInterval(refreshAll, 5000);
</script>
</body>
</html>
"""


def render_dashboard_html(daemon: CourseQualityDaemon) -> str:
    feed = daemon.feed_snapshot()
    health = daemon.health_snapshot()
    def esc(value: Any) -> str:
        return html.escape(str(value or ""))

    def card_html(job: dict[str, Any]) -> str:
        judgement = (((job.get("details") or {}).get("judgement")) or {})
        confidence = f"{judgement.get('confidence')} {judgement.get('trustTier')}" if judgement else "no confidence"
        changes = ((job.get("details") or {}).get("changedFields")) or []
        changes_text = f"changed {', '.join(str(item) for item in changes)}" if changes else ""
        course_name = job.get("humanCourseName") or job.get("courseId") or "Unknown course"
        day_label = job.get("humanDayLabel") or job.get("lessonId") or "-"
        lesson_title = job.get("humanLessonTitle") or job.get("lessonId") or "-"
        display_status = job.get("displayStatus") or job.get("status") or "-"
        updated = f"updated {job.get('humanUpdatedAt') or job.get('updatedAt') or '-'}"
        error = job.get("lastError")
        rca = ((job.get("details") or {}).get("rca") or {}).get("summary")
        quarantine = ((job.get("details") or {}).get("quarantine") or {}).get("status")
        lesson_line = f"<div class='job-meta'>{esc(lesson_title)}</div>" if job.get("kind") == "question" else ""
        error_line = f"<div class='job-meta status bad'>{esc(error)}</div>" if error else ""
        rca_line = f"<div class='job-meta'>{esc('RCA: ' + str(rca))}</div>" if rca else ""
        quarantine_line = f"<div class='job-meta status bad'>{esc('Human review required: ' + str(quarantine))}</div>" if quarantine else ""
        final_meta = changes_text or updated
        extra_meta = f"<div class='job-meta'>{esc(updated)}</div>" if changes_text else ""
        return (
            f"<div class='job-card' data-task-key='{esc(job.get('taskKey') or '')}' tabindex='0' role='button' onclick='openTaskDetail(this.getAttribute(\"data-task-key\")); return false;' onkeydown='if(event.key===\"Enter\"||event.key===\" \"){{ event.preventDefault(); openTaskDetail(this.getAttribute(\"data-task-key\")); return false; }}'>"
            f"<div class='job-title'>{esc(job.get('humanTitle') or job.get('taskKey') or 'Untitled task')}</div>"
            f"<div class='job-meta'>{esc(course_name)}</div>"
            f"<div class='job-meta'>{esc(day_label)}</div>"
            f"{lesson_line}"
            f"<div class='job-meta'>{esc(job.get('kind') or '-')} | {esc(display_status)} | attempts {esc(job.get('attempts') or 0)}</div>"
            f"<div class='job-meta'>confidence {esc(confidence)}</div>"
            f"<div class='job-meta'>{esc(final_meta)}</div>"
            f"{extra_meta}"
            f"{rca_line}"
            f"{quarantine_line}"
            f"{error_line}"
            f"</div>"
        )

    def cards_html(rows: list[dict[str, Any]], empty_text: str) -> str:
        if not rows:
            return f"<div class='empty'>{esc(empty_text)}</div>"
        return "".join(card_html(row) for row in rows)

    def runtime_html(runtime: dict[str, Any]) -> str:
        rows = []
        for item in runtime.get("providers") or []:
            status = str(item.get("status") or "")
            cls = "good" if status in {"HEALTHY", "STANDBY", "completed"} else ("warn" if status in {"DEGRADED", "pending", "running"} else "bad")
            rows.append(
                "<div class='runtime-item'>"
                f"<div><strong>{esc(item.get('provider') or '-')}</strong> <span class='status {cls}'>{esc(status)}</span></div>"
                f"<div class='tiny'>{esc(item.get('detail') or '')}</div>"
                f"<div class='tiny'>model: {esc(item.get('resolvedModel') or item.get('configuredModel') or '-')}</div>"
                f"<div class='tiny'>endpoint: {esc(item.get('endpoint') or '-')}</div>"
                "</div>"
            )
        if not rows:
            return "<div class='runtime-item'><div><strong>No runtime data</strong> <span class='status bad'>ERROR</span></div></div>"
        return "".join(rows)

    power = health.get("power") or {}
    profiles = power.get("profiles") or {}
    profile = profiles.get(power.get("mode")) or {}
    power_summary = (
        f"Mode: <strong>{esc(power.get('mode') or '-')}</strong><br>"
        f"threads {esc(profile.get('num_thread') if profile.get('num_thread') is not None else '-')} | "
        f"tokens {esc(profile.get('num_predict') if profile.get('num_predict') is not None else '-')} | "
        f"ctx {esc(profile.get('num_ctx') if profile.get('num_ctx') is not None else '-')}"
    )

    html_doc = (
        HTML.replace("__INITIAL_FEED__", json.dumps(feed, ensure_ascii=False).replace("</", "<\\/"))
        .replace("__INITIAL_HEALTH__", json.dumps(health, ensure_ascii=False).replace("</", "<\\/"))
        .replace("__GENERATED_AT__", esc(f"Updated {feed.get('generatedAt') or '-'}"))
        .replace("__WORKSPACE__", esc(health.get("workspaceRoot") or ""))
        .replace("__QUEUED_COUNT__", esc((feed.get("counts") or {}).get("pending") or 0))
        .replace("__RUNNING_COUNT__", esc((feed.get("counts") or {}).get("running") or 0))
        .replace("__COMPLETED_COUNT__", esc((feed.get("counts") or {}).get("completed") or 0))
        .replace("__FAILED_COUNT__", esc(feed.get("failedCount") or (feed.get("counts") or {}).get("failed") or 0))
        .replace("__ARCHIVED_COUNT__", esc(feed.get("archivedCount") or 0))
        .replace("__QUEUED_HTML__", cards_html(feed.get("queued") or [], "No queued jobs."))
        .replace("__RUNNING_HTML__", cards_html(feed.get("running") or [], "No running jobs."))
        .replace("__COMPLETED_HTML__", cards_html(feed.get("completed") or [], "No completed jobs yet."))
        .replace("__FAILED_HTML__", cards_html(feed.get("failed") or [], "No failed jobs."))
        .replace("__ARCHIVED_HTML__", cards_html(feed.get("archived") or [], "No archived jobs."))
        .replace("__POWER_SUMMARY__", power_summary)
        .replace("__RUNTIME_HTML__", runtime_html(health.get("runtime") or {}))
        .replace("__LAST_ACTION__", esc("Live snapshot loaded."))
    )
    return html_doc


class DashboardHandler(BaseHTTPRequestHandler):
    daemon: CourseQualityDaemon

    def _send_json(self, payload: dict[str, Any], status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        data = self.rfile.read(length)
        if not data:
            return {}
        return json.loads(data.decode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_html(render_dashboard_html(self.daemon))
            return
        if parsed.path == "/api/feed":
            params = parse_qs(parsed.query)
            limit = int(params.get("limit", [self.daemon.config.feed_limit])[0])
            self._send_json(self.daemon.feed_snapshot(limit=limit))
            return
        if parsed.path == "/api/health":
            self._send_json(self.daemon.health_snapshot())
            return
        if parsed.path == "/api/status":
            self._send_json(self.daemon.state.counts())
            return
        if parsed.path == "/api/task":
            params = parse_qs(parsed.query)
            task_key = str(params.get("taskKey", [""])[0])
            self._send_json({"task": self.daemon.task_detail(task_key)})
            return
        if parsed.path == "/api/search-completed":
            params = parse_qs(parsed.query)
            query = str(params.get("q", [""])[0])
            self._send_json({"query": query, "results": self.daemon.state.search_completed(query)})
            return
        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/scan":
            self._send_json({"ok": True, "result": self.daemon.scan()})
            return
        if parsed.path == "/api/run-once":
            params = parse_qs(parsed.query)
            max_items = int(params.get("maxItems", ["1"])[0])
            result = self.daemon.trigger_processing(max_items=max_items)
            self._send_json({"ok": True, "result": result}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/power-mode":
            params = parse_qs(parsed.query)
            mode = str(params.get("mode", ["balanced"])[0])
            try:
                result = self.daemon.set_power_mode(mode)
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "result": result}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/challenge":
            body = self._read_json_body()
            try:
                result = self.daemon.state.challenge_task(str(body.get("taskKey") or ""), str(body.get("comment") or ""))
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "result": result}, status=HTTPStatus.ACCEPTED)
            return
        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)


def run_dashboard(daemon: CourseQualityDaemon, host: str, port: int) -> None:
    handler = type("AmanobaDashboardHandler", (DashboardHandler,), {})
    handler.daemon = daemon
    server = ThreadingHTTPServer((host, port), handler)
    print(json.dumps({"dashboard": f"http://{host}:{port}", "status": "started"}, ensure_ascii=False))
    server.serve_forever()
