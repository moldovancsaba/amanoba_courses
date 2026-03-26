from __future__ import annotations

import html
import json
from pathlib import Path
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
    .nav-grid { display: grid; gap: 10px; }
    button {
      border: 0;
      border-radius: 14px;
      padding: 12px 14px;
      font-weight: 700;
      cursor: pointer;
      background: var(--accent);
      color: #fff;
      transition: transform 140ms ease, box-shadow 140ms ease, filter 140ms ease, opacity 140ms ease;
      box-shadow: 0 8px 18px rgba(20, 92, 82, 0.14);
    }
    button.secondary { background: #e6d8c4; color: var(--ink); }
    button.ghost { background: #f2e7d8; color: var(--ink); }
    button.danger { background: var(--bad); color: #fff; }
    button.small { padding: 9px 11px; font-size: 12px; border-radius: 10px; }
    button.nav-active { background: var(--accent); color: #fff; }
    button:hover:not(:disabled) {
      transform: translateY(-1px);
      filter: brightness(1.03);
      box-shadow: 0 10px 22px rgba(20, 92, 82, 0.18);
    }
    button:active:not(:disabled) {
      transform: translateY(1px) scale(0.985);
      box-shadow: 0 4px 10px rgba(20, 92, 82, 0.14);
    }
    button:disabled { cursor: not-allowed; opacity: 0.5; filter: saturate(0.6); }
    button.is-busy {
      position: relative;
      transform: translateY(1px);
      box-shadow: inset 0 0 0 999px rgba(255,255,255,0.08);
    }
    button.is-busy::after {
      content: "";
      width: 10px;
      height: 10px;
      margin-left: 8px;
      display: inline-block;
      border-radius: 999px;
      border: 2px solid rgba(255,255,255,0.55);
      border-top-color: rgba(255,255,255,1);
      animation: button-spin 0.9s linear infinite;
      vertical-align: -1px;
    }
    @keyframes button-spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .main { padding: 24px; overflow-x: auto; overflow-y: auto; }
    .hero { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 18px; }
    .hero h1 { margin: 0; font-size: 34px; }
    .hero p { margin: 6px 0 0; color: var(--muted); }
    .page { display: none; }
    .page.active { display: block; }
    .metrics {
      display: grid;
      grid-template-columns: repeat(9, minmax(160px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
      min-width: 1560px;
    }
    .creator-grid {
      display: grid;
      grid-template-columns: minmax(320px, 520px);
      gap: 14px;
      margin-bottom: 18px;
      min-width: 540px;
    }
    .creator-toolbar {
      display: flex;
      justify-content: flex-start;
      align-items: center;
      gap: 12px;
      margin-bottom: 18px;
    }
    .creator-kanban {
      display: grid;
      grid-template-columns: repeat(7, minmax(260px, 1fr));
      gap: 14px;
      align-items: start;
      min-width: 1880px;
    }
    .creator-column {
      padding: 14px;
      min-height: 320px;
      min-width: 0;
      overflow: hidden;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: var(--shadow);
    }
    .creator-column .cards {
      display: grid;
      gap: 10px;
    }
    .creator-panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: var(--shadow);
      padding: 16px;
    }
    .creator-head {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: baseline;
      margin-bottom: 12px;
    }
    .creator-head h2 {
      margin: 0;
      font-size: 20px;
    }
    .creator-form,
    .creator-runs {
      display: grid;
      gap: 10px;
    }
    .creator-run-card {
      border: 1px solid var(--line);
      border-radius: 14px;
      background: linear-gradient(180deg, #fffdf8 0%, #fbf4e9 100%);
      padding: 12px;
      cursor: pointer;
      display: grid;
      gap: 8px;
    }
    .creator-run-card:hover { border-color: var(--accent); transform: translateY(-1px); }
    .creator-run-card.idle {
      border-color: #d3c3ae;
      background: linear-gradient(180deg, #fffdf8 0%, #f5ede0 100%);
    }
    .creator-run-card.waiting {
      border-color: #e6c28d;
      background: linear-gradient(180deg, #fff7ea 0%, #fff0d8 100%);
    }
    .creator-run-card.working {
      border-color: #9cc2e9;
      background: linear-gradient(180deg, #f3f8fd 0%, #e8f1fb 100%);
    }
    .creator-run-card.blocked {
      border-color: #e2b2b2;
      background: linear-gradient(180deg, #fff3f3 0%, #fde7e7 100%);
    }
    .creator-run-card.completed {
      border-color: #b9d2c3;
      background: linear-gradient(180deg, #f3fbf5 0%, #e7f4eb 100%);
    }
    .creator-status-line {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      font-weight: 700;
      color: var(--muted);
    }
    .creator-status-dot {
      width: 10px;
      height: 10px;
      border-radius: 999px;
      display: inline-block;
      flex: 0 0 auto;
      background: #b8aa95;
    }
    .creator-run-card.idle .creator-status-dot { background: #b8aa95; }
    .creator-run-card.waiting .creator-status-dot { background: #d98a15; }
    .creator-run-card.working .creator-status-dot { background: #2d79c7; }
    .creator-run-card.blocked .creator-status-dot { background: #b84242; }
    .creator-run-card.completed .creator-status-dot { background: #2d8a4d; }
    .creator-title {
      font-size: 19px;
      font-weight: 800;
      line-height: 1.35;
    }
    .badge-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 6px;
    }
    .pill-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.04em;
      border: 1px solid var(--line);
      background: #f2e7d8;
      color: var(--muted);
      text-transform: uppercase;
    }
    .pill-badge.good { background: #e9f5ec; color: var(--good); border-color: #b9d2c3; }
    .pill-badge.warn { background: #fff1df; color: var(--warn); border-color: #e6c28d; }
    .pill-badge.bad { background: #f8e1e1; color: var(--bad); border-color: #e2b2b2; }
    .pill-badge.neutral { background: #f2e7d8; color: var(--muted); border-color: var(--line); }
    .creator-stage-list {
      display: grid;
      gap: 8px;
      margin-top: 10px;
    }
    .creator-event-list {
      display: grid;
      gap: 8px;
    }
    .creator-event-item {
      border-left: 3px solid var(--accent);
      padding-left: 10px;
      line-height: 1.45;
    }
    .creator-summary-grid {
      display: grid;
      gap: 8px;
    }
    .creator-summary-item {
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px 12px;
      background: #fffdf8;
      line-height: 1.45;
    }
    .creator-stage-row {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px 12px;
      background: #fffdf8;
    }
    .creator-stage-row.active-stage { border-color: #b9d2c3; background: #f5fbf7; }
    .creator-stage-row.completed-stage { border-color: #c6d7c8; }
    .creator-stage-row.blocked-stage { opacity: 0.82; }
    .stage-chip {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 4px 10px;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      border: 1px solid var(--line);
      background: #f2e7d8;
      color: var(--muted);
    }
    .stage-chip.active { background: #e2efe7; color: var(--good); border-color: #b9d2c3; }
    .stage-chip.completed { background: #e9f5ec; color: var(--good); border-color: #b9d2c3; }
    .stage-chip.needs-update { background: #fff1df; color: var(--warn); border-color: #e6c28d; }
    .stage-chip.blocked { background: #f2e7d8; color: var(--muted); }
    .stage-chip.cancelled,
    .stage-chip.deleted { background: #f8e1e1; color: var(--bad); border-color: #e2b2b2; }
    .stage-chip.ready-for-live { background: #e9f5ec; color: var(--good); border-color: #b9d2c3; }
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
    .live-strip {
      display: grid;
      gap: 4px;
      margin: 0 0 18px;
      padding: 14px 16px;
    }
    .kanban {
      display: grid;
      grid-template-columns: repeat(6, minmax(280px, 1fr));
      gap: 14px;
      align-items: start;
      min-width: 1780px;
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
    .rendered-content {
      line-height: 1.65;
      font-size: 16px;
    }
    .rendered-content h1,
    .rendered-content h2,
    .rendered-content h3,
    .rendered-content h4 {
      margin: 0 0 10px;
      line-height: 1.25;
    }
    .rendered-content h1 { font-size: 28px; }
    .rendered-content h2 { font-size: 24px; }
    .rendered-content h3 { font-size: 20px; }
    .rendered-content h4 { font-size: 18px; }
    .rendered-content p {
      margin: 0 0 12px;
    }
    .rendered-content ul,
    .rendered-content ol {
      margin: 0 0 14px 22px;
      padding: 0;
    }
    .rendered-content li {
      margin: 0 0 8px;
    }
    .rendered-content strong {
      font-weight: 800;
    }
    .rendered-content em {
      font-style: italic;
    }
    .rendered-content a {
      color: var(--accent);
      text-decoration: none;
      font-weight: 700;
    }
    .rendered-content hr {
      border: 0;
      border-top: 1px solid var(--line);
      margin: 14px 0;
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
    .action-board { display: grid; gap: 12px; }
    .action-group {
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px;
      background: #fffdf8;
      display: grid;
      gap: 10px;
    }
    .action-group h3 {
      margin: 0;
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }
    .action-help { color: var(--muted); font-size: 12px; line-height: 1.5; }
    .checklist { display: grid; gap: 8px; }
    .check-item {
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px 12px;
      background: #fffdf8;
      line-height: 1.45;
    }
    .check-item.good { border-color: #b9d2c3; background: #f3fbf5; }
    .check-item.warn { border-color: #e6c28d; background: #fff7ea; }
    .check-item.bad { border-color: #e2b2b2; background: #fff0f0; }
    .check-title { font-weight: 700; margin-bottom: 4px; }
    .workflow-banner {
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px;
      background: linear-gradient(180deg, #fffdf8 0%, #fbf4e9 100%);
      line-height: 1.5;
    }
    .workflow-banner strong { display: block; margin-bottom: 4px; }
    .workflow-banner.good { border-color: #b9d2c3; background: #f3fbf5; }
    .workflow-banner.warn { border-color: #e6c28d; background: #fff7ea; }
    .workflow-banner.bad { border-color: #e2b2b2; background: #fff0f0; }
    .workflow-banner.info { border-color: #b8c8d8; background: #f3f8fd; }
    .context-callout {
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px;
      line-height: 1.55;
      background: #fffdf8;
    }
    .context-callout.good { border-color: #b9d2c3; background: #f3fbf5; }
    .context-callout.warn { border-color: #e6c28d; background: #fff7ea; }
    .context-callout.bad { border-color: #e2b2b2; background: #fff0f0; }
    .context-callout strong { display: block; margin-bottom: 4px; }
    .inline-feedback {
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px 12px;
      background: #fffdf8;
      color: var(--muted);
      line-height: 1.5;
    }
    .inline-feedback.good { border-color: #b9d2c3; background: #f3fbf5; color: var(--good); }
    .inline-feedback.warn { border-color: #e6c28d; background: #fff7ea; color: #8f5a00; }
    .inline-feedback.bad { border-color: #e2b2b2; background: #fff0f0; color: var(--bad); }
    .inline-feedback.info { border-color: #b8c8d8; background: #f3f8fd; color: #23507a; }
    .hidden-panel { display: none; }
    .stage-focus-card {
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
      background: #fffdf8;
      display: grid;
      gap: 12px;
    }
    .stage-focus-meta {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }
    @media (max-width: 1280px) {
      .metrics { grid-template-columns: repeat(9, minmax(160px, 1fr)); min-width: 1560px; }
      .creator-grid { grid-template-columns: 1fr; min-width: 0; }
    }
    @media (max-width: 960px) {
      .shell { grid-template-columns: 1fr; }
      .rail { position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--line); }
      .metrics { grid-template-columns: repeat(9, minmax(160px, 1fr)); min-width: 1560px; }
      .creator-grid { min-width: 0; }
      .creator-kanban { grid-template-columns: repeat(7, minmax(240px, 1fr)); min-width: 1720px; }
      .kanban { grid-template-columns: repeat(6, minmax(260px, 1fr)); min-width: 1580px; }
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
        <h2>Workspace</h2>
        <div class='nav-grid'>
          <button id='navCourseCreator' class='ghost' onclick='switchPage("course-creator")'>Course Creator</button>
          <button id='navQualityControl' class='ghost' onclick='switchPage("quality-control")'>Quality Control</button>
        </div>
      </div>

      <div class='section'>
        <h2>Actions</h2>
        <div class='actions'>
          <button onclick='postAction("/api/scan")'>Scan Workspace</button>
          <button disabled title='QC runs as one continuous worker process.'>Single Worker Active</button>
          <button class='secondary' onclick='refreshAll()'>Refresh Feed</button>
        </div>
      </div>

      <div class='section'>
        <h2>Power Mode</h2>
        <div class='power-grid'>
          <button id='powerModeGentle' class='ghost' onclick='setPowerMode("gentle")'>Gentle</button>
          <button id='powerModeBalanced' class='ghost' onclick='setPowerMode("balanced")'>Balanced</button>
          <button id='powerModeFast' class='ghost' onclick='setPowerMode("fast")'>Fast</button>
        </div>
        <div class='rail-card tiny' id='powerSummary'>__POWER_SUMMARY__</div>
      </div>

      <div class='section'>
        <h2>Model Roster</h2>
        <div class='rail-card' id='runtimeProviders'>__RUNTIME_HTML__</div>
      </div>

      <div class='section'>
        <h2>Last Action</h2>
        <div class='rail-card'><pre id='lastAction'>__LAST_ACTION__</pre></div>
      </div>
    </aside>

    <main class='main'>
      <section class='page' id='pageCourseCreator'>
        <div class='hero'>
          <div>
            <h1>Sovereign Course Creator</h1>
            <p>Local staged draft workflow with checkpoints before QC and before live promotion.</p>
          </div>
        </div>

        <div class='creator-toolbar'>
          <button onclick='openCreateCourseModal()'>Create New Course</button>
          <button class='secondary small' onclick='refreshCreatorRuns()'>Refresh Runs</button>
        </div>
        <div class='creator-kanban'>
          <section class='creator-column'>
            <div class='column-head'><h2>Research</h2><div class='column-count' id='creatorResearchCount'>0</div></div>
            <div class='cards' id='creatorResearchRuns'><div class='empty'>No runs here.</div></div>
          </section>
          <section class='creator-column'>
            <div class='column-head'><h2>Blueprint</h2><div class='column-count' id='creatorBlueprintCount'>0</div></div>
            <div class='cards' id='creatorBlueprintRuns'><div class='empty'>No runs here.</div></div>
          </section>
          <section class='creator-column'>
            <div class='column-head'><h2>Lessons</h2><div class='column-count' id='creatorLessonCount'>0</div></div>
            <div class='cards' id='creatorLessonRuns'><div class='empty'>No runs here.</div></div>
          </section>
          <section class='creator-column'>
            <div class='column-head'><h2>Quizzes</h2><div class='column-count' id='creatorQuizCount'>0</div></div>
            <div class='cards' id='creatorQuizRuns'><div class='empty'>No runs here.</div></div>
          </section>
          <section class='creator-column'>
            <div class='column-head'><h2>QC Review</h2><div class='column-count' id='creatorQcCount'>0</div></div>
            <div class='cards' id='creatorQcRuns'><div class='empty'>No runs here.</div></div>
          </section>
          <section class='creator-column'>
            <div class='column-head'><h2>Draft To Live</h2><div class='column-count' id='creatorDraftCount'>0</div></div>
            <div class='cards' id='creatorDraftRuns'><div class='empty'>No runs here.</div></div>
          </section>
          <section class='creator-column'>
            <div class='column-head'><h2>Done</h2><div class='column-count' id='creatorDoneCount'>0</div></div>
            <div class='cards' id='creatorDoneRuns'><div class='empty'>No completed runs yet.</div></div>
          </section>
        </div>
      </section>

      <section class='page' id='pageQualityControl'>
        <div class='hero'>
          <div>
            <h1>Course Quality Control Center</h1>
            <p id='generatedAt'>__GENERATED_AT__</p>
          </div>
        </div>

        <div class='rail-card live-strip' id='workerStatus'>__WORKER_STATUS__</div>

        <div class='metrics'>
          <div class='metric-card'><div class='label'>Questions</div><div class='metric' id='questionCount'>__QUESTION_COUNT__</div></div>
          <div class='metric-card'><div class='label'>Lessons</div><div class='metric' id='lessonCount'>__LESSON_COUNT__</div></div>
          <div class='metric-card'><div class='label'>Courses</div><div class='metric' id='courseCount'>__COURSE_COUNT__</div></div>
          <div class='metric-card'><div class='label'>Coming Up</div><div class='metric' id='queuedCount'>__QUEUED_COUNT__</div></div>
          <div class='metric-card'><div class='label'>Active Now</div><div class='metric' id='runningCount'>__RUNNING_COUNT__</div></div>
          <div class='metric-card'><div class='label'>Done</div><div class='metric' id='completedCount'>__COMPLETED_COUNT__</div></div>
          <div class='metric-card'><div class='label'>Failed</div><div class='metric' id='failedCount'>__FAILED_COUNT__</div></div>
          <div class='metric-card'><div class='label'>Quarantined</div><div class='metric' id='quarantinedCount'>__QUARANTINED_COUNT__</div></div>
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
            <div class='column-head'><h2>Quarantined</h2><div class='column-count'>held for human decision</div></div>
            <div class='cards' id='quarantinedJobs'>__QUARANTINED_HTML__</div>
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
      </section>
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
          </div>
          <div>
            <div class='label'>After</div>
            <div class='human-card' id='modalAfterHuman'></div>
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
            <div class='inline-feedback info' id='detailActionFeedback'>No action yet.</div>
            <pre id='modalFeedbackHistory'>No feedback yet.</pre>
            <textarea id='challengeComment' placeholder='Challenge this result with one comment. Example: The scenario is still too generic and the distractors are weak.'></textarea>
            <div class='row-actions'>
              <button class='danger small' id='challengeTaskButton' onclick='challengeCurrentTask()'>Challenge And Requeue</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class='modal' id='creatorModal'>
    <div class='modal-card'>
      <div class='modal-top'>
        <div>
          <h2 id='creatorModalTitle' style='margin:0;'>Creator Run</h2>
          <div class='tiny' id='creatorModalMeta'></div>
        </div>
        <div class='row-actions'>
          <button class='secondary small' onclick='closeCreatorModal()'>Close</button>
        </div>
      </div>
      <div class='stack'>
        <div class='rail-card tiny' id='creatorModalSummary'>Loading...</div>
        <div id='creatorDraftSummarySection'>
          <div class='label'>Draft Summary</div>
          <div class='creator-summary-grid' id='creatorDraftSummary'></div>
        </div>
        <div id='creatorArtifactSummarySection'>
          <div class='label'>Artifact Summary</div>
          <div class='creator-summary-grid' id='creatorArtifactSummary'></div>
        </div>
        <div id='creatorChecklistSection'>
          <div class='label'>Lifecycle Checklist</div>
          <div class='checklist' id='creatorChecklist'></div>
        </div>
        <div id='creatorWorkflowBannerSection'>
        <div class='label' id='creatorWorkflowBannerLabel'>Current State</div>
          <div class='workflow-banner' id='creatorWorkflowBanner'>Loading...</div>
        </div>
        <div id='creatorStageWarningSection'>
          <div class='label'>Stage Warning</div>
          <div class='context-callout warn' id='creatorStageWarning'>Loading...</div>
        </div>
        <div id='creatorStageFocusSection'>
          <div class='label' id='creatorStageFocusLabel'>Current Review Item</div>
          <div class='stage-focus-card'>
            <div class='row-actions' id='creatorStageFocusNav'></div>
            <div class='stage-focus-meta' id='creatorStageFocusMeta'>Loading...</div>
            <div class='human-card' id='creatorStageFocusBody'></div>
          </div>
        </div>
        <div id='creatorSourcePackSection'>
          <div class='label'>Source Pack</div>
          <div class='row-actions' style='margin-bottom:10px;'>
            <button class='small' id='creatorRefreshSourcesButton' onclick='refreshCreatorSources(this)'>Refresh Source Pack</button>
            <button class='secondary small' onclick='resetCreatorSourceForm()'>New Source</button>
          </div>
          <div class='creator-summary-grid' style='margin-bottom:10px;'>
            <input id='creatorSourceTitle' placeholder='Source title'>
            <input id='creatorSourceUrl' placeholder='Source URL'>
            <input id='creatorSourceType' placeholder='Source type, example: web-search, wikipedia, manual' value='manual'>
            <input id='creatorSourceScore' placeholder='Score 0-100' value='50'>
            <textarea id='creatorSourceSnippet' placeholder='Source note or snippet'></textarea>
          </div>
          <div class='row-actions' style='margin-bottom:10px;'>
            <button class='small' id='creatorSaveSourceButton' onclick='saveCreatorSource(this)'>Save Source</button>
            <button class='secondary small' onclick='resetCreatorSourceForm()'>Reset Source Form</button>
          </div>
          <div class='tiny' id='creatorSourceEditorMeta'>No source selected.</div>
          <div class='creator-event-list' id='creatorSourcePack'></div>
        </div>
        <div id='creatorArtifactPreviewSection'>
          <div class='label'>Current Stage Artifact</div>
          <div class='human-card' id='creatorArtifactPreview'></div>
        </div>
        <div id='creatorArtifactEditorSection'>
          <div class='label' id='creatorArtifactEditorLabel'>Manual Edit</div>
          <textarea id='creatorArtifactEditor' placeholder='Stage artifact content will appear here.'></textarea>
          <div class='row-actions'>
            <button class='small' onclick='generateCreatorArtifact()'>Generate Stage Draft</button>
            <button class='secondary small' onclick='saveCreatorArtifact()'>Save Artifact</button>
          </div>
        </div>
        <div id='creatorNotesSection'>
          <div class='label'>Run Notes</div>
          <div class='creator-event-list' id='creatorNotes'></div>
        </div>
        <div id='creatorEventsSection'>
          <div class='label'>Event History</div>
          <div class='creator-event-list' id='creatorEvents'></div>
        </div>
        <div>
          <div class='label' id='creatorProcessControlsLabel'>Process Controls</div>
          <div class='inline-feedback info' id='creatorActionFeedback'>No action yet.</div>
          <textarea id='creatorComment' placeholder='Write what to change. If you click Make New Draft, the system will use this note.'></textarea>
          <div class='action-board'>
            <div class='action-group' id='creatorStageActionGroup'>
              <h3 id='creatorStageActionGroupTitle'>Stage Workflow</h3>
              <div class='action-help' id='creatorStageActionHelp'>Loading...</div>
              <div class='row-actions'>
                <button class='secondary small' id='creatorToggleEditButton' onclick='toggleCreatorEditMode()'>Edit This Stage</button>
                <button class='small' id='creatorGenerateButton' onclick='generateCreatorArtifact()'>Make New Draft</button>
                <button class='secondary small' id='creatorSaveButton' onclick='saveCreatorArtifact()'>Save Manual Edit</button>
                <button class='small' id='creatorAcceptButton' onclick='submitCreatorAction("accept")'>Approve And Continue</button>
                <button class='secondary small' id='creatorUpdateButton' onclick='submitCreatorAction("update")'>Send Back With My Note</button>
                <button class='danger small' id='creatorDeleteButton' onclick='submitCreatorAction("delete")'>Delete This Run</button>
              </div>
            </div>
            <div class='action-group' id='creatorReleaseActionGroup'>
              <h3>Downstream Release</h3>
              <div class='action-help' id='creatorReleaseActionHelp'>Loading...</div>
              <div class='row-actions'>
                <button class='small' id='creatorPromoteButton' onclick='promoteCreatorDraft()'>Promote Draft Package</button>
                <button class='small' id='creatorImportButton' onclick='importCreatorDraft()'>Import Draft To Amanoba</button>
                <button class='small' id='creatorPublishButton' onclick='publishCreatorDraft()'>Publish In Amanoba</button>
              </div>
            </div>
            <div class='action-group' id='creatorRecoveryActionGroup'>
              <h3>Recovery Controls</h3>
              <div class='action-help' id='creatorRecoveryActionHelp'>Loading...</div>
              <div class='row-actions'>
                <button class='secondary small' id='creatorRollbackButton' onclick='rollbackCreatorPublish()'>Rollback Live Publish</button>
                <button class='danger small' id='creatorDeleteImportButton' onclick='deleteCreatorImport()'>Delete Amanoba Draft</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class='modal' id='createCourseModal'>
    <div class='dialog' style='max-width:720px;'>
      <div class='dialog-head'>
        <div>
          <h2 style='margin:0;'>Create New Course</h2>
          <div class='tiny'>Start a new sovereign course creation run.</div>
        </div>
        <button class='secondary' onclick='closeCreateCourseModal()'>Close</button>
      </div>
      <div class='dialog-body'>
        <div class='creator-form'>
          <input id='creatorTopic' placeholder='Course topic or title'>
          <input id='creatorLanguage' placeholder='Target language code, example: en, pl, vi' value='en'>
          <input id='creatorResearchMode' placeholder='Research mode: optional, required, or offline' value='optional'>
          <div class='rail-card tiny' id='createCourseFeedback'>No action yet.</div>
          <div class='row-actions'>
            <button id='createCourseSubmitButton' onclick='createCreatorRun()'>Create New Course</button>
          </div>
        </div>
      </div>
    </div>
  </div>

<script>
const INITIAL_FEED = __INITIAL_FEED__;
const INITIAL_HEALTH = __INITIAL_HEALTH__;
const INITIAL_CREATOR = __INITIAL_CREATOR__;
let currentDetailTaskKey = null;
let currentCreatorRunId = null;
let currentCreatorStageKey = null;
let currentCreatorSourceId = null;
let currentCreatorRunData = null;
let currentCreatorReviewIndex = 0;
let currentCreatorEditMode = false;
let currentPage = 'quality-control';
let creatorFeedbackState = null;
const BUILD_STAMP = '__BUILD_STAMP__';

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
function creatorStageLabel(stage) {
  return String(stage || '')
    .replaceAll('_', ' ')
    .replace(/\\b\\w/g, (char) => char.toUpperCase());
}
function creatorReviewLabel(stage) {
  const value = String(stage || '');
  if (value === 'research') return 'Research Brief';
  if (value === 'blueprint') return 'Outline Day';
  if (value === 'lesson_generation') return 'Lesson Review';
  if (value === 'quiz_generation') return 'Quiz Question Review';
  if (value === 'qc_review') return 'QC Review Status';
  if (value === 'draft_to_live') return 'Release Review';
  if (value === 'cover_image') return 'Cover Image';
  return 'Current Review Item';
}
function creatorEditorLabel(stage) {
  const value = String(stage || '');
  if (value === 'research') return 'Manual Edit: Research Brief';
  if (value === 'blueprint') return 'Manual Edit: Outline';
  if (value === 'lesson_generation') return 'Manual Edit: Lessons';
  if (value === 'quiz_generation') return 'Manual Edit: Quiz';
  return 'Manual Edit';
}
function creatorStageSupportsEditor(stage) {
  return ['research', 'blueprint', 'lesson_generation', 'quiz_generation'].includes(String(stage || ''));
}
function updateCreatorEditModeButton() {
  const button = document.getElementById('creatorToggleEditButton');
  if (!button) return;
  const supported = creatorStageSupportsEditor(currentCreatorStageKey);
  button.disabled = !supported;
  button.title = supported ? '' : 'Editing is not available for this lifecycle stage.';
  button.textContent = currentCreatorEditMode ? 'Hide Manual Edit' : 'Edit This Stage';
}
function setCreatorEditMode(enabled) {
  currentCreatorEditMode = !!enabled;
  updateCreatorModalVisibility(currentCreatorStageKey);
  updateCreatorEditModeButton();
}
function toggleCreatorEditMode() {
  setCreatorEditMode(!currentCreatorEditMode);
}
function resetCreatorSourceForm() {
  currentCreatorSourceId = null;
  document.getElementById('creatorSourceTitle').value = '';
  document.getElementById('creatorSourceUrl').value = '';
  document.getElementById('creatorSourceType').value = 'manual';
  document.getElementById('creatorSourceScore').value = '50';
  document.getElementById('creatorSourceSnippet').value = '';
  document.getElementById('creatorSourceEditorMeta').textContent = 'No source selected.';
  document.getElementById('creatorSaveSourceButton').textContent = 'Save Source';
}
function loadCreatorSource(item) {
  currentCreatorSourceId = String(item.sourceId || '');
  document.getElementById('creatorSourceTitle').value = item.title || '';
  document.getElementById('creatorSourceUrl').value = item.url || '';
  document.getElementById('creatorSourceType').value = item.sourceType || 'manual';
  document.getElementById('creatorSourceScore').value = item.score || '50';
  document.getElementById('creatorSourceSnippet').value = item.snippet || '';
  document.getElementById('creatorSourceEditorMeta').textContent = currentCreatorSourceId ? `Editing ${currentCreatorSourceId}` : 'Editing source';
  document.getElementById('creatorSaveSourceButton').textContent = currentCreatorSourceId ? 'Update Source' : 'Save Source';
}
function setSectionVisible(id, visible) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.toggle('hidden-panel', !visible);
}
function editCreatorSourceFromEncoded(encoded) {
  try {
    loadCreatorSource(JSON.parse(decodeURIComponent(encoded)));
  } catch (error) {
    console.error(error);
    window.alert('Failed to load source into the editor.');
  }
}
function parseCreatorBlueprintDays(markdown) {
  const rows = [];
  const regex = /### Day (?<day>\\d{2}) — (?<title>.+?)\\n- Module: (?<module>.+?)\\n- Goal: (?<goal>.+?)\\n- Deliverable: (?<deliverable>.+?)\\n- Quiz focus: (?<quiz_focus>.+?)(?:\\n|$)/gs;
  for (const match of markdown.matchAll(regex)) {
    rows.push(match.groups || {});
  }
  return rows;
}
function parseCreatorLessonRows(markdown) {
  const rows = [];
  const regex = /### Day (?<day>\\d{2}) Lesson Draft\\n- Lesson title: (?<lesson_title>.+?)\\n- Learning goal: (?<goal>.+?)\\n- Deliverable: (?<deliverable>.+?)\\n- Email subject: (?<email_subject>.+?)\\n- Guided exercise focus: (?<guided_focus>.+?)\\n- Independent exercise focus: (?<independent_focus>.+?)\\n- Self-check focus: (?<self_check_focus>.+?)\\n- Quiz focus: (?<quiz_focus>.+?)\\n\\n#### Lesson Body Draft\\n(?<lesson_body>.*?)\\n\\n#### Email Body Draft\\n(?<email_body>.*?)(?=\\n### Day |\\Z)/gs;
  for (const match of markdown.matchAll(regex)) {
    rows.push(match.groups || {});
  }
  return rows;
}
function parseCreatorQuizRows(markdown) {
  const rows = [];
  const dayRegex = /### Day (?<day>\\d{2}) Quiz Draft\\n- Lesson title: (?<lesson_title>.+?)\\n- Quiz focus: (?<quiz_focus>.+?)\\n- Batch target: (?<batch_target>.+?)\\n(?<body>.*?)(?=\\n### Day |\\Z)/gs;
  const questionRegex = /#### Question (?<question_number>\\d+)\\n- Stem focus: (?<stem_focus>.+?)\\n- Correct answer intent: (?<correct_intent>.+?)\\n- Distractor themes: (?<distractor_themes>.+?)\\n- Question type: (?<question_type>.+?)(?:\\n|$)/gs;
  for (const dayMatch of markdown.matchAll(dayRegex)) {
    const base = dayMatch.groups || {};
    const body = base.body || '';
    for (const qMatch of body.matchAll(questionRegex)) {
      rows.push({ ...base, ...(qMatch.groups || {}) });
    }
  }
  return rows;
}
function creatorReviewNav(index, total, prevFn, nextFn, label) {
  return `
    <button class='secondary small' ${index <= 0 ? 'disabled' : ''} onclick='${prevFn}()'>Previous ${label}</button>
    <button class='secondary small' ${index >= total - 1 ? 'disabled' : ''} onclick='${nextFn}()'>Next ${label}</button>
  `;
}
function setCreatorReviewIndex(index) {
  currentCreatorReviewIndex = Math.max(0, index);
  if (currentCreatorRunId) openCreatorRun(currentCreatorRunId);
}
function nextCreatorReviewItem() { setCreatorReviewIndex(currentCreatorReviewIndex + 1); }
function prevCreatorReviewItem() { setCreatorReviewIndex(currentCreatorReviewIndex - 1); }
function stageChip(status) {
  const value = String(status || 'blocked');
  return `<span class='stage-chip ${escapeHtml(value)}'>${escapeHtml(creatorStageLabel(value))}</span>`;
}
function setButtonState(id, enabled, reason) {
  const el = document.getElementById(id);
  if (!el) return;
  el.disabled = !enabled;
  el.title = enabled ? '' : (reason || '');
}
function setElementVisible(id, visible) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.toggle('hidden-panel', !visible);
}
function setInlineFeedback(id, kind, message) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = `inline-feedback ${kind || 'info'}`;
  el.textContent = message || 'No action yet.';
}
function rememberCreatorFeedback(kind, message, runId = null) {
  creatorFeedbackState = {
    kind: kind || 'info',
    message: message || 'No action yet.',
    runId: runId || currentCreatorRunId || null,
  };
}
function applyCreatorFeedback(runId = null) {
  if (creatorFeedbackState && (!runId || !creatorFeedbackState.runId || creatorFeedbackState.runId === runId)) {
    setInlineFeedback('creatorActionFeedback', creatorFeedbackState.kind, creatorFeedbackState.message);
    return;
  }
  setInlineFeedback('creatorActionFeedback', 'info', 'No action yet.');
}
function setButtonBusy(id, busy, busyLabel = 'Working...') {
  const button = document.getElementById(id);
  setButtonBusyElement(button, busy, busyLabel);
}
function setButtonBusyElement(button, busy, busyLabel = 'Working...') {
  if (!button) return;
  if (!button.dataset.defaultLabel) {
    button.dataset.defaultLabel = button.textContent || '';
  }
  button.disabled = !!busy;
  button.classList.toggle('is-busy', !!busy);
  button.textContent = busy ? busyLabel : (button.dataset.defaultLabel || button.textContent || '');
}
async function runActionWithFeedback(options) {
  const { buttonId, buttonEl, busyLabel, feedbackId, startMessage, successMessage, action } = options;
  if (feedbackId) setInlineFeedback(feedbackId, 'info', startMessage || 'Working...');
  if (buttonEl) setButtonBusyElement(buttonEl, true, busyLabel || 'Working...');
  else if (buttonId) setButtonBusy(buttonId, true, busyLabel || 'Working...');
  try {
    const result = await action();
    if (feedbackId) setInlineFeedback(feedbackId, 'good', successMessage || 'Action completed.');
    return result;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    if (feedbackId) setInlineFeedback(feedbackId, 'bad', message);
    throw error;
  } finally {
    if (buttonEl) setButtonBusyElement(buttonEl, false);
    else if (buttonId) setButtonBusy(buttonId, false);
  }
}
function creatorLifecycleState(run) {
  const payload = (run && run.payload) || {};
  const qc = payload.qcStatus || {};
  const promotion = payload.promotion || {};
  const importStatus = payload.importStatus || {};
  const publishStatus = payload.publishStatus || {};
  const rollbackStatus = payload.rollbackStatus || {};
  const deleteStatus = payload.deleteStatus || {};
  const activeStage = String(run && run.activeStage ? run.activeStage : '');
  const runStatus = String(run && run.status ? run.status : '');
  const qcTotal = Number(qc.total || 0);
  const qcCompleted = Number(qc.completed || 0);
  const qcQueued = Number(qc.queued || 0);
  const qcRunning = Number(qc.running || 0);
  const qcFailed = Number(qc.failed || 0);
  const qcQuarantined = Number(qc.quarantined || 0);
  const qcReady = qcTotal > 0 && qcCompleted >= qcTotal && qcFailed === 0 && qcQuarantined === 0;
  const hasPackage = Boolean(promotion.packagePath);
  const isDraftImported = String(importStatus.status || '') === 'draft-imported' && Boolean(importStatus.courseId);
  const isPublished = String(publishStatus.status || '') === 'published-live';
  const isRolledBack = String(rollbackStatus.status || '') === 'rolled-back-to-draft';
  const isImportDeleted = String(deleteStatus.status || '') === 'import-deleted';
  return {
    activeStage,
    runStatus,
    qcTotal,
    qcCompleted,
    qcQueued,
    qcRunning,
    qcFailed,
    qcQuarantined,
    qcReady,
    hasPackage,
    isDraftImported,
    isPublished,
    isRolledBack,
    isImportDeleted,
    canGenerateStage: Boolean(activeStage && runStatus !== 'deleted' && runStatus !== 'completed'),
    canSaveStage: Boolean(activeStage && runStatus !== 'deleted'),
    canAcceptStage:
      Boolean(activeStage)
      && (
        (activeStage !== 'qc_review' && activeStage !== 'draft_to_live')
        || (activeStage === 'qc_review' && qcReady)
        || (activeStage === 'draft_to_live' && hasPackage && isDraftImported && isPublished)
      ),
    canRequestUpdate: Boolean(activeStage && runStatus !== 'deleted'),
    canDeleteRun: runStatus !== 'deleted',
    canPromoteDraft: activeStage === 'draft_to_live' && qcReady,
    canImportDraft: (activeStage === 'draft_to_live' || runStatus === 'completed') && hasPackage && !isDraftImported,
    canPublishDraft: (activeStage === 'draft_to_live' || runStatus === 'completed') && isDraftImported && !isPublished,
    canRollbackPublish: isPublished,
    canDeleteImport: isDraftImported && !isPublished,
  };
}
function creatorStageHasReviewContent(run, stageKey) {
  const payload = (run && run.payload) || {};
  const stageArtifacts = payload.stageArtifacts || {};
  const content = String((((stageArtifacts || {})[stageKey] || {}).content) || '').trim();
  if (!content) return false;
  if (stageKey === 'research') return content.length > 0;
  if (stageKey === 'blueprint') return parseCreatorBlueprintDays(content).length > 0;
  if (stageKey === 'lesson_generation') return parseCreatorLessonRows(content).length > 0;
  if (stageKey === 'quiz_generation') return parseCreatorQuizRows(content).length > 0;
  return content.length > 0;
}
function creatorIsStageSetup(run) {
  const state = creatorLifecycleState(run);
  if (!state.activeStage) return false;
  if (state.activeStage === 'qc_review') return state.qcTotal <= 0;
  if (state.activeStage === 'draft_to_live') return false;
  return !creatorStageHasReviewContent(run, state.activeStage);
}
function creatorRunBadges(run) {
  const state = creatorLifecycleState(run);
  const payload = (run && run.payload) || {};
  const qc = payload.qcStatus || {};
  const badges = [];
  badges.push({ cls: state.runStatus === 'completed' ? 'good' : state.activeStage ? 'warn' : 'bad', text: `Stage ${creatorStageLabel(state.activeStage || run.status || '-')}` });
  if (Number(qc.total || 0) > 0) {
    const qcBad =
      Number(qc.failed || 0) > 0 || Number(qc.quarantined || 0) > 0 ? 'bad'
      : state.qcReady ? 'good'
      : 'warn';
    const qcText = state.qcReady
      ? `QC clean ${qc.completed || 0}/${qc.total || 0}`
      : `QC ${qc.completed || 0}/${qc.total || 0}`;
    badges.push({ cls: qcBad, text: qcText });
  } else if (state.activeStage === 'qc_review' || state.activeStage === 'draft_to_live' || state.runStatus === 'completed') {
    badges.push({ cls: 'warn', text: 'QC handoff missing' });
  }
  if (state.isPublished) {
    badges.push({ cls: 'good', text: 'Live published' });
  } else if (state.isDraftImported) {
    badges.push({ cls: 'warn', text: 'Draft imported' });
  } else if (state.hasPackage) {
    badges.push({ cls: 'warn', text: 'Package ready' });
  }
  if (state.isRolledBack) badges.push({ cls: 'warn', text: 'Rolled back' });
  if (state.isImportDeleted) badges.push({ cls: 'bad', text: 'Draft removed' });
  return badges;
}
function creatorStageWarning(run) {
  const state = creatorLifecycleState(run);
  const payload = (run && run.payload) || {};
  const qc = payload.qcStatus || {};
  const isSetup = creatorIsStageSetup(run);
  if (state.runStatus === 'completed') {
    return {
      cls: 'good',
      title: 'Lifecycle complete',
      detail: 'This run completed the full local creator lifecycle. Use rollback or delete only when you intentionally want to reverse downstream state.',
    };
  }
  if (state.activeStage === 'research') {
    const sources = Array.isArray(payload.sourcePack) ? payload.sourcePack.length : 0;
    if (!sources) {
      return { cls: 'warn', title: 'Research evidence is thin', detail: 'No source pack is attached yet. Approving research without sources increases the chance of generic or stale course architecture.' };
    }
    return { cls: 'good', title: 'Research is grounded', detail: `The run has ${sources} collected sources. Review whether the pack is relevant before approving the blueprint input.` };
  }
  if (state.activeStage === 'blueprint') {
    if (isSetup) {
      return { cls: 'warn', title: 'Blueprint not created yet', detail: 'There is no usable blueprint to review yet. Create a new draft first.' };
    }
    return { cls: 'warn', title: 'Blueprint controls downstream cost', detail: 'Weak day structure here will create weak lessons, weak quizzes, and a larger QC burden later. Validate sequencing before approval.' };
  }
  if (state.activeStage === 'lesson_generation') {
    if (isSetup) {
      return { cls: 'warn', title: 'Lesson drafts not created yet', detail: 'There is nothing to review yet. Create the lesson draft batch before moving forward.' };
    }
    return { cls: 'warn', title: 'Lesson quality drives QC volume', detail: 'Approving weak lesson drafts will expand rewrite load in QC Review. Check tone, structure, and language purity before advancing.' };
  }
  if (state.activeStage === 'quiz_generation') {
    if (isSetup) {
      return { cls: 'warn', title: 'Quiz drafts not created yet', detail: 'There is nothing to review yet. Create the quiz draft batch before moving forward.' };
    }
    return { cls: 'warn', title: 'Quiz quality must stay application-first', detail: 'Do not advance if the batch drifts toward recall questions or mixed-language output. Fix question intent before QC handoff.' };
  }
  if (state.activeStage === 'qc_review') {
    if (state.qcTotal <= 0) {
      return { cls: 'warn', title: 'QC handoff not created', detail: 'Generate QC Review to inject creator QC tasks before this stage can run.' };
    }
    if (Number(qc.failed || 0) > 0 || Number(qc.quarantined || 0) > 0) {
      return { cls: 'bad', title: 'QC still has blocking issues', detail: `Creator QC cannot be approved while failed (${qc.failed || 0}) or quarantined (${qc.quarantined || 0}) tasks remain.` };
    }
    if (state.qcRunning > 0 || state.qcQueued > 0 || state.qcCompleted < state.qcTotal) {
      return { cls: 'warn', title: 'QC is working', detail: `${state.qcCompleted} of ${state.qcTotal} creator QC tasks are complete. ${state.qcRunning} running, ${state.qcQueued} queued.` };
    }
    return { cls: 'good', title: 'QC is clean', detail: 'The creator-owned QC queue is complete and has no blocking failures. You can move into Draft To Live.' };
  }
  if (state.activeStage === 'draft_to_live') {
    if (!state.hasPackage) {
      return { cls: 'warn', title: 'No draft package exists yet', detail: 'Promote the reviewed creator output into a package before any downstream Amanoba action.' };
    }
    if (!state.isDraftImported) {
      return { cls: 'warn', title: 'Downstream checkpoint not created yet', detail: 'Import the package into Amanoba as draft/inactive first. This gives you a reversible review step before live publish.' };
    }
    if (!state.isPublished) {
      return { cls: 'warn', title: 'Still not live', detail: 'The Amanoba draft exists, but the course is not live yet. Publish only after you confirm the downstream draft looks correct.' };
    }
    return { cls: 'good', title: 'Downstream release complete', detail: 'The course is live in Amanoba. Use rollback or delete only as an intentional recovery operation.' };
  }
  return {
    cls: 'warn',
    title: 'Review the current stage carefully',
    detail: 'The next approval changes what the system generates or releases downstream. Validate the artifact before advancing.',
  };
}
function creatorRunState(run) {
  const state = creatorLifecycleState(run);
  const isSetup = creatorIsStageSetup(run);
  if (state.runStatus === 'completed') {
    return {
      cls: 'good',
      title: 'Completed',
      detail: 'This creator run finished the full lifecycle.',
      next: 'No action required unless you want to roll back or remove the downstream course.',
    };
  }
  if (state.activeStage === 'qc_review') {
    if (state.qcTotal <= 0) {
      return {
        cls: 'warn',
        title: 'Waiting For You',
        detail: 'QC handoff has not been created yet.',
        next: 'Click Make New Draft to start QC handoff.',
      };
    }
    if (state.qcFailed > 0 || state.qcQuarantined > 0) {
      return {
        cls: 'bad',
        title: 'Blocked',
        detail: `${state.qcFailed} failed and ${state.qcQuarantined} quarantined creator QC tasks need attention.`,
        next: 'Open the matching QC cards, fix or challenge them, then return here.',
      };
    }
    if (state.qcRunning > 0 || state.qcQueued > 0 || state.qcCompleted < state.qcTotal) {
      return {
        cls: 'warn',
        title: 'Working',
        detail: `${state.qcCompleted}/${state.qcTotal} creator QC tasks are complete. ${state.qcRunning} running, ${state.qcQueued} queued.`,
        next: 'Wait for the QC queue to finish. You do not need to approve this stage yet.',
      };
    }
    if (state.qcReady) {
      return {
        cls: 'good',
        title: 'Waiting For You',
        detail: 'Creator QC is complete and clean.',
        next: 'Click Approve And Continue to move to Draft To Live.',
      };
    }
  }
  if (state.activeStage === 'draft_to_live') {
    if (!state.hasPackage) {
      return {
        cls: 'warn',
        title: 'Waiting For You',
        detail: 'The reviewed draft has not been packaged yet.',
        next: 'Click Promote Draft Package.',
      };
    }
    if (!state.isDraftImported) {
      return {
        cls: 'warn',
        title: 'Waiting For You',
        detail: 'The package exists, but no Amanoba draft has been created.',
        next: 'Click Import Draft To Amanoba.',
      };
    }
    if (!state.isPublished) {
      return {
        cls: 'warn',
        title: 'Waiting For You',
        detail: 'The Amanoba draft exists and is still inactive.',
        next: 'Review the draft downstream, then click Publish In Amanoba when ready.',
      };
    }
    return {
      cls: 'good',
      title: 'Waiting For You',
      detail: 'The course is already live in Amanoba.',
      next: 'Click Approve And Continue to close the local creator run.',
    };
  }
  if (isSetup) {
    const label = creatorStageLabel(state.activeStage || 'stage');
    return {
      cls: 'warn',
      title: 'Waiting For You',
      detail: `${label} has not been created yet.`,
      next: `Write a note if needed, then click Make New Draft to create the first ${label.toLowerCase()}.`,
    };
  }
  return {
    cls: 'warn',
    title: 'Waiting For You',
    detail: `Review the current ${creatorStageLabel(state.activeStage || 'stage')} artifact.`,
    next: 'If it is good, click Approve And Continue. If it needs changes, write a note and click Make New Draft or Send Back With My Note.',
  };
}
function configureCreatorStageChrome(run) {
  const state = creatorLifecycleState(run);
  const isQcSetup = state.activeStage === 'qc_review' && state.qcTotal <= 0;
  const isStageSetup = creatorIsStageSetup(run);
  const isDraftStage = state.activeStage === 'draft_to_live';
  const bannerLabel = document.getElementById('creatorWorkflowBannerLabel');
  const processLabel = document.getElementById('creatorProcessControlsLabel');
  const stageGroupTitle = document.getElementById('creatorStageActionGroupTitle');
  if (bannerLabel) bannerLabel.textContent = isQcSetup || isDraftStage || isStageSetup ? 'Current State' : 'What Happens Next';
  if (processLabel) processLabel.textContent = isQcSetup || isStageSetup ? 'Action' : (isDraftStage ? 'Release Actions' : 'Process Controls');
  if (stageGroupTitle) stageGroupTitle.textContent = isQcSetup || isStageSetup ? 'Primary Action' : (isDraftStage ? 'Finalize Run' : 'Stage Workflow');
}
function sourceStatusBadge(status) {
  const value = String(status || 'neutral');
  const cls = value === 'preferred' ? 'good' : value === 'rejected' ? 'bad' : 'neutral';
  return `<span class='pill-badge ${cls}'>${escapeHtml(value)}</span>`;
}
function renderCreatorChecklist(run) {
  const host = document.getElementById('creatorChecklist');
  const payload = (run && run.payload) || {};
  const qc = payload.qcStatus || {};
  const promotion = payload.promotion || {};
  const importStatus = payload.importStatus || {};
  const publishStatus = payload.publishStatus || {};
  const rollbackStatus = payload.rollbackStatus || {};
  const deleteStatus = payload.deleteStatus || {};
  const items = [
    {
      ok: Number(qc.total || 0) > 0,
      title: 'QC handoff exists',
      detail: Number(qc.total || 0) > 0 ? `${qc.total} creator QC tasks were injected.` : 'Generate QC Review first to create creator QC work.',
    },
    {
      ok: Number(qc.total || 0) > 0 && Number(qc.completed || 0) >= Number(qc.total || 0) && Number(qc.failed || 0) === 0 && Number(qc.quarantined || 0) === 0,
      title: 'QC queue is clean',
      detail: `${qc.completed || 0}/${qc.total || 0} completed · failed ${qc.failed || 0} · quarantined ${qc.quarantined || 0}`,
    },
    {
      ok: Boolean(promotion.packagePath),
      title: 'Draft package exported',
      detail: promotion.packagePath || 'Promote Draft Package is still required.',
    },
    {
      ok: String(importStatus.status || '') === 'draft-imported',
      title: 'Amanoba draft imported',
      detail: importStatus.courseId ? `${importStatus.courseId} (${importStatus.status || '-'})` : 'Import Draft To Amanoba is still required.',
    },
    {
      ok: String(publishStatus.status || '') === 'published-live',
      title: 'Amanoba course published',
      detail: publishStatus.courseId ? `${publishStatus.courseId} (${publishStatus.status || '-'})` : 'Publish In Amanoba is still required.',
    },
  ];
  if (rollbackStatus.status) {
    items.push({ ok: false, title: 'Rollback recorded', detail: `${rollbackStatus.status} at ${rollbackStatus.rolledBackAt || '-'}` });
  }
  if (deleteStatus.status) {
    items.push({ ok: false, title: 'Imported draft deleted', detail: `${deleteStatus.status} at ${deleteStatus.deletedAt || '-'}` });
  }
  host.innerHTML = items.map((item) => {
    const cls = item.ok ? 'good' : 'warn';
    return `<div class='check-item ${cls}'><div class='check-title'>${escapeHtml(item.title)}</div><div>${escapeHtml(item.detail)}</div></div>`;
  }).join('');
}
function renderCreatorControls(run) {
  const state = creatorLifecycleState(run);
  const isQcSetup = state.activeStage === 'qc_review' && state.qcTotal <= 0;
  const isStageSetup = creatorIsStageSetup(run);
  const isDraftStage = state.activeStage === 'draft_to_live';
  const stageSupportsEditor = creatorStageSupportsEditor(state.activeStage) && !isStageSetup;
  const stageSupportsGenerate = ['research', 'blueprint', 'lesson_generation', 'quiz_generation', 'qc_review'].includes(String(state.activeStage || ''));
  const stageSupportsManualSave = stageSupportsEditor;
  const showGenerateButton = stageSupportsGenerate && !(state.activeStage === 'qc_review' && state.qcTotal > 0);
  const showAcceptButton = !isQcSetup && !isStageSetup;
  const showUpdateButton = !isQcSetup && !isDraftStage && !isStageSetup;
  const showReleaseGroup = state.activeStage === 'draft_to_live' || state.runStatus === 'completed';
  const showRecoveryGroup = state.canRollbackPublish || state.canDeleteImport;
  const showEditToggle = stageSupportsEditor;
  const showSaveButton = stageSupportsManualSave;
  const showStageActionGroup = !showReleaseGroup || isQcSetup || isStageSetup || state.runStatus === 'completed' || state.isPublished;
  const showCommentBox = !isQcSetup && !isDraftStage;
  setButtonState('creatorGenerateButton', state.canGenerateStage && showGenerateButton, 'Generation is not relevant for the current stage.');
  setButtonState('creatorSaveButton', state.canSaveStage && stageSupportsManualSave, 'Manual editing is only available for artifact-writing stages.');
  setButtonState('creatorAcceptButton', state.canAcceptStage, 'Resolve stage requirements before accepting.');
  setButtonState('creatorUpdateButton', state.canRequestUpdate, 'There is no active stage to send back for update.');
  setButtonState('creatorDeleteButton', state.canDeleteRun, 'This run is already deleted.');
  setButtonState('creatorPromoteButton', state.canPromoteDraft, 'QC must be complete and clean before package promotion.');
  setButtonState('creatorImportButton', state.canImportDraft, 'Export the draft package first, then import it into Amanoba.');
  setButtonState('creatorPublishButton', state.canPublishDraft, 'Import the Amanoba draft first. Publish is only valid after import.');
  setButtonState('creatorRollbackButton', state.canRollbackPublish, 'Rollback is only available after a live publish.');
  setButtonState('creatorDeleteImportButton', state.canDeleteImport, 'Delete is only available for an imported draft that is not currently live.');
  document.getElementById('creatorGenerateButton').textContent = isQcSetup ? 'Start QC Handoff' : 'Make New Draft';
  setElementVisible('creatorToggleEditButton', showEditToggle);
  setElementVisible('creatorGenerateButton', showGenerateButton);
  setElementVisible('creatorSaveButton', showSaveButton);
  setElementVisible('creatorAcceptButton', showAcceptButton);
  setElementVisible('creatorUpdateButton', showUpdateButton);
  setElementVisible('creatorStageActionGroup', showStageActionGroup);
  setElementVisible('creatorReleaseActionGroup', showReleaseGroup);
  setElementVisible('creatorRecoveryActionGroup', showRecoveryGroup);
  setElementVisible('creatorStageWarningSection', !isQcSetup);
  setElementVisible('creatorComment', showCommentBox);
  const runState = creatorRunState(run);
  configureCreatorStageChrome(run);
  document.getElementById('creatorStageActionHelp').textContent = runState.next;
  document.getElementById('creatorReleaseActionHelp').textContent =
    showReleaseGroup
      ? 'Release actions are sequential: package export, Amanoba draft import, then live publish.'
      : 'Release actions unlock when the run reaches Draft To Live.';
  document.getElementById('creatorRecoveryActionHelp').textContent =
    showRecoveryGroup
      ? 'Recovery actions reverse downstream state without losing the local creator run.'
      : 'Recovery stays disabled until an Amanoba draft exists or has been published.';
  let bannerTitle = runState.title;
  let bannerText = runState.detail;
  let bannerCls = runState.cls;
  const banner = document.getElementById('creatorWorkflowBanner');
  banner.className = `workflow-banner ${bannerCls}`;
  banner.innerHTML = `<strong>${escapeHtml(bannerTitle)}</strong>${escapeHtml(bannerText)}`;
  const warning = creatorStageWarning(run);
  const warningHost = document.getElementById('creatorStageWarning');
  warningHost.className = `context-callout ${warning.cls}`;
  warningHost.innerHTML = `<strong>${escapeHtml(warning.title)}</strong>${escapeHtml(warning.detail)}`;
}
function renderCreatorStageFocus(run, activeStageKey, activeArtifact) {
  const bodyHost = document.getElementById('creatorStageFocusBody');
  const metaHost = document.getElementById('creatorStageFocusMeta');
  const navHost = document.getElementById('creatorStageFocusNav');
  const lifecycle = creatorLifecycleState(run);
  document.getElementById('creatorStageFocusLabel').textContent = activeStageKey === 'qc_review' && lifecycle.qcTotal <= 0
    ? 'QC Setup'
    : creatorReviewLabel(activeStageKey);
  document.getElementById('creatorArtifactEditorLabel').textContent = creatorEditorLabel(activeStageKey);
  navHost.innerHTML = '';
  const payload = (run && run.payload) || {};
  const content = String((activeArtifact && activeArtifact.content) || '').trim();
  if (activeStageKey === 'research') {
    metaHost.textContent = 'Review the approved research brief and curate the evidence set before moving to blueprint.';
    bodyHost.innerHTML = content ? renderRichText(content) : "<div class='empty'>No research brief yet.</div>";
    return;
  }
  if (activeStageKey === 'blueprint') {
    const rows = parseCreatorBlueprintDays(content);
    if (!rows.length) {
      document.getElementById('creatorStageFocusLabel').textContent = 'Blueprint Setup';
      metaHost.textContent = 'There is no blueprint outline yet.';
      bodyHost.innerHTML = "<div class='empty'>Write a note if needed, then click Make New Draft to create the first blueprint outline.</div>";
      return;
    }
    const index = Math.min(currentCreatorReviewIndex, rows.length - 1);
    currentCreatorReviewIndex = index;
    const row = rows[index];
    metaHost.textContent = `Reviewing outline day ${row.day || '-'} of ${rows.length}. Approve only if the day goal, deliverable, and quiz focus are coherent.`;
    navHost.innerHTML = creatorReviewNav(index, rows.length, 'prevCreatorReviewItem', 'nextCreatorReviewItem', 'Day');
    bodyHost.innerHTML = `
      <div class='human-question'>Day ${escapeHtml(row.day || '-')} — ${escapeHtml(row.title || '-')}</div>
      <div class='human-meta'>Module: ${escapeHtml(row.module || '-')}</div>
      <div class='choice-item'><strong>Goal</strong><br>${escapeHtml(row.goal || '-')}</div>
      <div class='choice-item'><strong>Deliverable</strong><br>${escapeHtml(row.deliverable || '-')}</div>
      <div class='choice-item'><strong>Quiz focus</strong><br>${escapeHtml(row.quiz_focus || '-')}</div>
    `;
    return;
  }
  if (activeStageKey === 'lesson_generation') {
    const rows = parseCreatorLessonRows(content);
    if (!rows.length) {
      document.getElementById('creatorStageFocusLabel').textContent = 'Lesson Setup';
      metaHost.textContent = 'There are no lesson drafts yet.';
      bodyHost.innerHTML = "<div class='empty'>Write a note if needed, then click Make New Draft to create the lesson draft batch.</div>";
      return;
    }
    const index = Math.min(currentCreatorReviewIndex, rows.length - 1);
    currentCreatorReviewIndex = index;
    const row = rows[index];
    metaHost.textContent = `Reviewing lesson ${index + 1} of ${rows.length}. Check tone, exercise quality, and language purity before advancing.`;
    navHost.innerHTML = creatorReviewNav(index, rows.length, 'prevCreatorReviewItem', 'nextCreatorReviewItem', 'Lesson');
    bodyHost.innerHTML = `
      <div class='human-question'>Day ${escapeHtml(row.day || '-')} — ${escapeHtml(row.lesson_title || '-')}</div>
      <div class='human-meta'>Email subject: ${escapeHtml(row.email_subject || '-')}</div>
      <div class='choice-item'><strong>Learning goal</strong><br>${escapeHtml(row.goal || '-')}</div>
      <div class='choice-item'><strong>Deliverable</strong><br>${escapeHtml(row.deliverable || '-')}</div>
      <div class='choice-item'>${renderRichText(row.lesson_body || '')}</div>
      <div class='human-meta'>Email body</div>
      <div class='choice-item'>${renderRichText(row.email_body || '')}</div>
    `;
    return;
  }
  if (activeStageKey === 'quiz_generation') {
    const rows = parseCreatorQuizRows(content);
    if (!rows.length) {
      document.getElementById('creatorStageFocusLabel').textContent = 'Quiz Setup';
      metaHost.textContent = 'There are no quiz drafts yet.';
      bodyHost.innerHTML = "<div class='empty'>Write a note if needed, then click Make New Draft to create the quiz draft batch.</div>";
      return;
    }
    const index = Math.min(currentCreatorReviewIndex, rows.length - 1);
    currentCreatorReviewIndex = index;
    const row = rows[index];
    metaHost.textContent = `Reviewing quiz question ${index + 1} of ${rows.length}. Check application focus and make sure the stem intent is strong enough before QC handoff.`;
    navHost.innerHTML = creatorReviewNav(index, rows.length, 'prevCreatorReviewItem', 'nextCreatorReviewItem', 'Question');
    bodyHost.innerHTML = `
      <div class='human-question'>Day ${escapeHtml(row.day || '-')} · Question ${escapeHtml(row.question_number || '-')}</div>
      <div class='human-meta'>Lesson: ${escapeHtml(row.lesson_title || '-')}</div>
      <div class='choice-item'><strong>Stem focus</strong><br>${escapeHtml(row.stem_focus || '-')}</div>
      <div class='choice-item'><strong>Correct answer intent</strong><br>${escapeHtml(row.correct_intent || '-')}</div>
      <div class='choice-item'><strong>Distractor themes</strong><br>${escapeHtml(row.distractor_themes || '-')}</div>
      <div class='choice-item'><strong>Question type</strong><br>${escapeHtml(row.question_type || '-')}</div>
    `;
    return;
  }
  if (activeStageKey === 'qc_review') {
    const qc = payload.qcStatus || {};
    if (lifecycle.qcTotal <= 0) {
      metaHost.textContent = 'QC has not started yet. This stage needs a handoff before there is anything to review.';
      bodyHost.innerHTML = `
        <div class='human-question'>QC Setup</div>
        <div class='choice-item'><strong>Status</strong><br>No creator QC tasks exist yet.</div>
        <div class='choice-item'><strong>What to do now</strong><br>Click <strong>Start QC Handoff</strong> to inject the creator lesson and quiz drafts into the QC queue.</div>
        <div class='choice-item'><strong>After that</strong><br>The stage will switch from setup into a live QC progress view.</div>
      `;
      return;
    }
    const stateText = lifecycle.qcFailed > 0 || lifecycle.qcQuarantined > 0
      ? 'QC is blocked by failed or quarantined items.'
      : (lifecycle.qcRunning > 0 || lifecycle.qcQueued > 0 || lifecycle.qcCompleted < lifecycle.qcTotal
        ? 'QC is currently working through the creator queue.'
        : 'QC is complete and waiting for your approval.');
    metaHost.textContent = stateText;
    bodyHost.innerHTML = `
      <div class='human-question'>QC Review</div>
      <div class='choice-item'><strong>Status</strong><br>${escapeHtml(stateText)}</div>
      <div class='choice-item'><strong>Progress</strong><br>${escapeHtml(`${qc.completed || 0}/${qc.total || 0} completed · running ${qc.running || 0} · queued ${qc.queued || 0} · failed ${qc.failed || 0} · quarantined ${qc.quarantined || 0}`)}</div>
      <div class='choice-item'><strong>Recent completed</strong><br>${escapeHtml(((qc.recentCompleted || []).join(' | ')) || 'No completed creator QC tasks yet.')}</div>
      <div class='choice-item'><strong>Recent failed</strong><br>${escapeHtml(((qc.recentFailed || []).join(' | ')) || 'No failed creator QC tasks.')}</div>
    `;
    return;
  }
  if (activeStageKey === 'draft_to_live') {
    const promotion = payload.promotion || {};
    const importStatus = payload.importStatus || {};
    const publishStatus = payload.publishStatus || {};
    const statusText = !lifecycle.hasPackage
      ? 'The reviewed draft is waiting for package export.'
      : !lifecycle.isDraftImported
        ? 'The package is ready and waiting for Amanoba draft import.'
        : !lifecycle.isPublished
          ? 'The Amanoba draft is ready and waiting for live publish.'
          : 'The course is live in Amanoba and waiting for final local closeout.';
    metaHost.textContent = statusText;
    bodyHost.innerHTML = `
      <div class='human-question'>Release State</div>
      <div class='choice-item'><strong>Status</strong><br>${escapeHtml(statusText)}</div>
      <div class='choice-item'><strong>Draft package</strong><br>${escapeHtml((promotion.packagePath) || 'No package yet.')}</div>
      <div class='choice-item'><strong>Amanoba draft import</strong><br>${escapeHtml(`${(importStatus.status) || 'not imported'} · ${(importStatus.courseId) || '-'}`)}</div>
      <div class='choice-item'><strong>Amanoba live publish</strong><br>${escapeHtml(`${(publishStatus.status) || 'not published'} · ${(publishStatus.courseId) || '-'}`)}</div>
    `;
    return;
  }
  if (activeStageKey === 'cover_image') {
    metaHost.textContent = 'Review the cover image only for this stage.';
    bodyHost.innerHTML = `<div class='choice-item'><strong>Cover image</strong><br><input type='file' accept='image/*'></div>`;
    return;
  }
  metaHost.textContent = 'Review the current stage artifact.';
  bodyHost.innerHTML = content ? renderRichText(content) : "<div class='empty'>No stage artifact yet.</div>";
}
function syncPageFromHash() {
  const hash = window.location.hash === '#course-creator' ? 'course-creator' : 'quality-control';
  switchPage(hash, true);
}
function switchPage(page, fromHash = false) {
  currentPage = page === 'course-creator' ? 'course-creator' : 'quality-control';
  document.getElementById('pageCourseCreator').classList.toggle('active', currentPage === 'course-creator');
  document.getElementById('pageQualityControl').classList.toggle('active', currentPage === 'quality-control');
  document.getElementById('navCourseCreator').classList.toggle('nav-active', currentPage === 'course-creator');
  document.getElementById('navCourseCreator').classList.toggle('ghost', currentPage !== 'course-creator');
  document.getElementById('navQualityControl').classList.toggle('nav-active', currentPage === 'quality-control');
  document.getElementById('navQualityControl').classList.toggle('ghost', currentPage !== 'quality-control');
  if (!fromHash) {
    window.location.hash = currentPage === 'course-creator' ? '#course-creator' : '#quality-control';
  }
}
function cardTitle(job) {
  return job.humanTitle || job.questionUuid || job.lessonId || job.taskKey || 'Untitled task';
}
function normalizedTaskKind(kind) {
  const value = String(kind || '');
  if (value === 'creator_question') return 'question';
  if (value === 'creator_lesson') return 'lesson';
  return value || 'task';
}
function creatorPipelineColumn(run) {
  if (String(run && run.status || '') === 'completed') return 'done';
  const stage = String(run && run.activeStage ? run.activeStage : '');
  if (stage === 'research') return 'research';
  if (stage === 'blueprint') return 'blueprint';
  if (stage === 'lesson_generation') return 'lesson';
  if (stage === 'quiz_generation') return 'quiz';
  if (stage === 'qc_review') return 'qc';
  if (stage === 'draft_to_live') return 'draft';
  return 'research';
}
function creatorBoardState(run) {
  const state = creatorRunState(run);
  if (state.title === 'Completed') {
    return { cls: 'completed', label: 'Completed' };
  }
  if (state.cls === 'bad' || state.title === 'Blocked') {
    return { cls: 'blocked', label: 'Blocked' };
  }
  if (state.title === 'Working') {
    return { cls: 'working', label: 'System Working' };
  }
  if (state.title === 'Waiting For You') {
    return { cls: 'waiting', label: 'Your Input Needed' };
  }
  return { cls: 'idle', label: 'Idle' };
}
function creatorLastAction(run) {
  const notes = Array.isArray(run && run.notes) ? run.notes : [];
  const activeStage = String(run && run.activeStage ? run.activeStage : '');
  for (let index = notes.length - 1; index >= 0; index -= 1) {
    const note = notes[index] || {};
    if (activeStage && String(note.stageKey || '') !== activeStage) continue;
    const type = String(note.type || '');
    const createdAt = String(note.createdAt || '');
    if (type === 'stage-generate') {
      return `New draft created ${createdAt || '-'}`;
    }
    if (type === 'human-update') {
      return `Your note was saved ${createdAt || '-'}`;
    }
    if (type === 'artifact-save') {
      return `Manual edit saved ${createdAt || '-'}`;
    }
    if (type === 'system-repair') {
      return `Run was repaired ${createdAt || '-'}`;
    }
  }
  return '';
}
function creatorRunCardMarkup(run) {
  const stage = run.activeStage || '-';
  const updated = run.updatedAt || '-';
  const targetLanguage = run.targetLanguage || '-';
  const researchMode = run.researchMode || '-';
  const artifactSummaries = run.artifactSummaries || {};
  const activeSummary = artifactSummaries[stage] || {};
  const badges = creatorRunBadges(run);
  const nextCheckpoint = (run.draftSummary && run.draftSummary.nextCheckpoint) || '-';
  const boardState = creatorBoardState(run);
  const lastAction = creatorLastAction(run);
  const nextCheckpointText = nextCheckpoint === 'No open checkpoint.' && stage !== '-' ? `${creatorStageLabel(stage)} review` : nextCheckpoint;
  return `<div class='creator-run-card ${escapeHtml(boardState.cls)}' data-run-id='${escapeHtml(run.runId)}' tabindex='0' role='button' onclick='openCreatorRun(this.getAttribute("data-run-id")); return false;' onkeydown='if(event.key==="Enter"||event.key===" "){ event.preventDefault(); openCreatorRun(this.getAttribute("data-run-id")); return false; }'>
    <div class='creator-title'>${escapeHtml(run.topic || run.runId)}</div>
    <div class='creator-status-line'><span class='creator-status-dot'></span>${escapeHtml(boardState.label)}</div>
    <div class='tiny'>language ${escapeHtml(targetLanguage)} | research ${escapeHtml(researchMode)}</div>
    <div class='tiny'>status ${escapeHtml(run.status || '-')} | active stage ${escapeHtml(creatorStageLabel(stage))}</div>
    <div class='badge-row'>${badges.map((badge) => `<span class='pill-badge ${badge.cls}'>${escapeHtml(badge.text)}</span>`).join('')}</div>
    ${activeSummary.headline ? `<div class='tiny'>${escapeHtml(activeSummary.headline)}</div>` : ''}
    ${lastAction ? `<div class='tiny'>${escapeHtml(lastAction)}</div>` : ''}
    <div class='tiny'>next checkpoint ${escapeHtml(nextCheckpointText)}</div>
    <div class='tiny'>updated ${escapeHtml(updated)}</div>
  </div>`;
}
function renderCreatorRuns(snapshot) {
  const runs = Array.isArray(snapshot && snapshot.runs) ? snapshot.runs : [];
  const buckets = {
    research: [],
    blueprint: [],
    lesson: [],
    quiz: [],
    qc: [],
    draft: [],
    done: [],
  };
  if (!runs.length) {
    closeCreatorModal();
    document.getElementById('creatorResearchCount').textContent = '0';
    document.getElementById('creatorBlueprintCount').textContent = '0';
    document.getElementById('creatorLessonCount').textContent = '0';
    document.getElementById('creatorQuizCount').textContent = '0';
    document.getElementById('creatorQcCount').textContent = '0';
    document.getElementById('creatorDraftCount').textContent = '0';
    document.getElementById('creatorDoneCount').textContent = '0';
    document.getElementById('creatorResearchRuns').innerHTML = "<div class='empty'>No runs here.</div>";
    document.getElementById('creatorBlueprintRuns').innerHTML = "<div class='empty'>No runs here.</div>";
    document.getElementById('creatorLessonRuns').innerHTML = "<div class='empty'>No runs here.</div>";
    document.getElementById('creatorQuizRuns').innerHTML = "<div class='empty'>No runs here.</div>";
    document.getElementById('creatorQcRuns').innerHTML = "<div class='empty'>No runs here.</div>";
    document.getElementById('creatorDraftRuns').innerHTML = "<div class='empty'>No runs here.</div>";
    document.getElementById('creatorDoneRuns').innerHTML = "<div class='empty'>No completed runs yet.</div>";
    return;
  }
  runs.forEach((run) => {
    const key = creatorPipelineColumn(run);
    (buckets[key] || buckets.research).push(run);
  });
  const mountBucket = (countId, hostId, items, emptyText) => {
    document.getElementById(countId).textContent = String(items.length);
    document.getElementById(hostId).innerHTML = items.length
      ? items.map((run) => creatorRunCardMarkup(run)).join('')
      : `<div class='empty'>${emptyText}</div>`;
  };
  mountBucket('creatorResearchCount', 'creatorResearchRuns', buckets.research, 'No runs here.');
  mountBucket('creatorBlueprintCount', 'creatorBlueprintRuns', buckets.blueprint, 'No runs here.');
  mountBucket('creatorLessonCount', 'creatorLessonRuns', buckets.lesson, 'No runs here.');
  mountBucket('creatorQuizCount', 'creatorQuizRuns', buckets.quiz, 'No runs here.');
  mountBucket('creatorQcCount', 'creatorQcRuns', buckets.qc, 'No runs here.');
  mountBucket('creatorDraftCount', 'creatorDraftRuns', buckets.draft, 'No runs here.');
  mountBucket('creatorDoneCount', 'creatorDoneRuns', buckets.done, 'No completed runs yet.');
}
function updateCreatorModalVisibility(activeStageKey, run = currentCreatorRunData) {
  const stage = String(activeStageKey || '');
  const lifecycle = run ? creatorLifecycleState(run) : null;
  const isQcSetup = stage === 'qc_review' && lifecycle && lifecycle.qcTotal <= 0;
  const isStageSetup = run ? creatorIsStageSetup(run) : false;
  const showSource = stage === 'research';
  const showEditor = creatorStageSupportsEditor(stage) && currentCreatorEditMode;
  const showArtifactPreview = !['lesson_generation', 'quiz_generation', 'blueprint', 'research', 'qc_review', 'draft_to_live', 'cover_image'].includes(stage);
  const showArtifactSummary = !isStageSetup && !['qc_review', 'draft_to_live'].includes(stage);
  setSectionVisible('creatorDraftSummarySection', false);
  setSectionVisible('creatorArtifactSummarySection', showArtifactSummary);
  setSectionVisible('creatorChecklistSection', false);
  setSectionVisible('creatorWorkflowBannerSection', true);
  setSectionVisible('creatorStageWarningSection', !isStageSetup && !['draft_to_live'].includes(stage));
  setSectionVisible('creatorStageFocusSection', true);
  setSectionVisible('creatorSourcePackSection', showSource);
  setSectionVisible('creatorArtifactPreviewSection', showArtifactPreview);
  setSectionVisible('creatorArtifactEditorSection', showEditor);
  setSectionVisible('creatorStageListSection', false);
  setSectionVisible('creatorNotesSection', false);
  setSectionVisible('creatorEventsSection', false);
  updateCreatorEditModeButton();
}
function resetStaleUiState() {
  closeModal();
  closeCreatorModal();
  document.getElementById('lastAction').textContent = `Live snapshot loaded. Build ${BUILD_STAMP}`;
}
function renderJobs(id, jobs, emptyText) {
  const el = document.getElementById(id);
  if (!jobs || !jobs.length) {
    el.innerHTML = `<div class='empty'>${emptyText}</div>`;
    return;
  }
  const worker = window.__CURRENT_WORKER__ || {};
  el.innerHTML = jobs.map(job => {
    const judgement = job.details && job.details.judgement ? `${job.details.judgement.confidence} ${job.details.judgement.trustTier}` : 'no confidence';
    const changes = job.details && job.details.changedFields ? `changed ${job.details.changedFields.join(', ')}` : '';
    const courseName = job.humanCourseName || job.courseId || 'Unknown course';
    const dayLabel = job.humanDayLabel || job.lessonId || '-';
    const lessonTitle = job.humanLessonTitle || job.lessonId || '-';
    const displayStatus = job.displayStatus || job.status;
    const kindLabel = normalizedTaskKind(job.kind);
    const updated = job.humanUpdatedAt ? `updated ${job.humanUpdatedAt}` : '';
    const statusClass = displayStatus === 'rewriting' ? 'warn' : 'bad';
    const error = job.lastError ? `<div class='job-meta status ${statusClass}'>${job.lastError}</div>` : '';
    const lessonLine = kindLabel === 'question' ? `<div class='job-meta'>${escapeHtml(lessonTitle)}</div>` : '';
    const liveLine = worker && worker.taskKey === job.taskKey
      ? `<div class='job-meta status warn'>live ${escapeHtml(worker.phase || 'working')} | heartbeat ${escapeHtml(worker.heartbeatAt || '-')}</div>`
      : '';
    return `<div class='job-card' data-task-key='${escapeHtml(job.taskKey)}' tabindex='0' role='button' onclick='openTaskDetail(this.getAttribute("data-task-key")); return false;' onkeydown='if(event.key==="Enter"||event.key===" "){ event.preventDefault(); openTaskDetail(this.getAttribute("data-task-key")); return false; }'>
      <div class='job-title'>${escapeHtml(cardTitle(job)).replaceAll('\\n', '<br>')}</div>
      <div class='job-meta'>${escapeHtml(courseName)}</div>
      <div class='job-meta'>${escapeHtml(dayLabel)}</div>
      ${lessonLine}
      <div class='job-meta'>${escapeHtml(kindLabel)} | ${escapeHtml(displayStatus)} | attempts ${job.attempts}</div>
      ${liveLine}
      <div class='job-meta'>confidence ${escapeHtml(judgement)}</div>
      <div class='job-meta'>${escapeHtml(changes || updated || ('updated ' + (job.updatedAt || '-')))}</div>
      ${changes && updated ? `<div class='job-meta'>${escapeHtml(updated)}</div>` : ''}
      ${error}
    </div>`;
  }).join('');
}
function renderWorkerStatus(worker) {
  const el = document.getElementById('workerStatus');
  if (!el) return;
  const phase = String(worker && worker.phase ? worker.phase : 'unknown');
  const taskKey = String(worker && worker.taskKey ? worker.taskKey : '');
  const heartbeatAt = String(worker && worker.heartbeatAt ? worker.heartbeatAt : '-');
  const progressAt = String(worker && worker.progressAt ? worker.progressAt : '-');
  const startedAt = String(worker && worker.taskStartedAt ? worker.taskStartedAt : '-');
  const liveLabel = taskKey ? 'actively processing' : 'idle and waiting for the next issue';
  el.innerHTML = `
    <div><strong>Live Worker State</strong> <span class='status ${taskKey ? 'warn' : 'good'}'>${escapeHtml(liveLabel)}</span></div>
    <div class='tiny'>phase: ${escapeHtml(phase)}${taskKey ? ` | task ${escapeHtml(taskKey)}` : ''}</div>
    <div class='tiny'>progress heartbeat: ${escapeHtml(progressAt)} | worker heartbeat: ${escapeHtml(heartbeatAt)}</div>
    <div class='tiny'>task started: ${escapeHtml(startedAt)}</div>
  `;
}
function isPathLike(value) {
  return typeof value === 'string' && (value.includes('/') || value.includes('\\\\'));
}
function basename(value) {
  const text = String(value || '').trim();
  if (!text) return '';
  return text.split(/[\\\\/]/).filter(Boolean).pop() || text;
}
function providerSummary(item) {
  const provider = String(item && item.provider ? item.provider : '').toLowerCase();
  const configured = String(item && item.configuredModel ? item.configuredModel : '').trim();
  const resolved = String(item && item.resolvedModel ? item.resolvedModel : '').trim();
  const endpoint = String(item && item.endpoint ? item.endpoint : '').trim();
  if (provider === 'mlx') {
    return {
      modelLabel: 'Model',
      runtimeLabel: 'Apertus 8B Instruct 4bit',
      endpointLabel: 'local MLX runtime',
      endpointValue: endpoint || '-',
    };
  }
  const modelValue = resolved || configured || '-';
  return {
    modelLabel: 'Model',
    runtimeLabel: modelValue,
    endpointLabel: 'Endpoint',
    endpointValue: endpoint || '-',
  };
}
function renderResidentRole(item) {
  const name = String(item && item.name ? item.name : 'ROLE');
  const host = String(item && item.host ? item.host : '127.0.0.1');
  const port = String(item && item.port ? item.port : '-');
  const detail = String(item && item.detail ? item.detail : `${host}:${port}`);
  const status = String(item && item.status ? item.status : 'DOWN');
  const modelLabel = String(item && item.modelLabel ? item.modelLabel : '');
  return `
    <div class='runtime-item'>
      <div><strong>${escapeHtml(name)}</strong> <span class='status ${clsFor(status)}'>${escapeHtml(status)}</span></div>
      <div class='tiny'>Resident creator role</div>
      ${modelLabel ? `<div class='tiny'>Model: ${escapeHtml(modelLabel)}</div>` : ''}
      <div class='tiny'>Endpoint: ${escapeHtml(host)}:${escapeHtml(port)}</div>
      <div class='tiny'>${escapeHtml(detail)}</div>
    </div>
  `;
}
function renderRuntime(runtime, residentRoles = []) {
  const host = document.getElementById('runtimeProviders');
  const providers = Array.isArray(runtime && runtime.providers) ? runtime.providers : [];
  const roleItems = Array.isArray(residentRoles) ? residentRoles : [];
  if (!providers.length && !roleItems.length) {
    host.innerHTML = "<div class='runtime-item'><div><strong>No runtime data</strong> <span class='status bad'>ERROR</span></div></div>";
    return;
  }
  const providerItems = providers.map(item => `
    <div class='runtime-item'>
      <div><strong>${escapeHtml(item.provider)}</strong> <span class='status ${clsFor(item.status)}'>${escapeHtml(item.status)}</span></div>
      <div class='tiny'>${escapeHtml(item.detail)}</div>
      <div class='tiny'>${escapeHtml(providerSummary(item).modelLabel)}: ${escapeHtml(providerSummary(item).runtimeLabel && isPathLike(providerSummary(item).runtimeLabel) ? basename(providerSummary(item).runtimeLabel) : providerSummary(item).runtimeLabel)}</div>
      <div class='tiny'>${escapeHtml(providerSummary(item).endpointLabel)}: ${escapeHtml(providerSummary(item).endpointValue)}</div>
    </div>
  `);
  host.innerHTML = providerItems.join('') + roleItems.map(renderResidentRole).join('');
}
function renderPower(power) {
  const profiles = power && power.profiles ? power.profiles : {};
  const profile = (power && power.profile) || profiles[power.mode] || {};
  const mode = String(power && power.mode ? power.mode : '');
  const gentle = document.getElementById('powerModeGentle');
  const balanced = document.getElementById('powerModeBalanced');
  const fast = document.getElementById('powerModeFast');
  if (gentle) gentle.classList.toggle('nav-active', mode === 'gentle');
  if (balanced) balanced.classList.toggle('nav-active', mode === 'balanced');
  if (fast) fast.classList.toggle('nav-active', mode === 'fast');
  document.getElementById('powerSummary').innerHTML = `Mode: <strong>${escapeHtml(power.mode)}</strong><br>threads ${escapeHtml(String(profile.num_thread ?? '-'))} | tokens ${escapeHtml(String(profile.num_predict ?? '-'))} | ctx ${escapeHtml(String(profile.num_ctx ?? '-'))}<br>lesson rewrite tokens ${escapeHtml(String(profile.lesson_rewrite_predict ?? profile.num_predict ?? '-'))}`;
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
function inlineMarkdownToHtml(value) {
  return escapeHtml(String(value ?? ''))
    .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
    .replace(/__(.+?)__/g, '<strong>$1</strong>')
    .replace(/\\*(.+?)\\*/g, '<em>$1</em>')
    .replace(/_(.+?)_/g, '<em>$1</em>')
    .replace(/\\[([^\\]]+)\\]\\((https?:[^\\s)]+)\\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
}
function markdownToHtml(value) {
  const source = String(value ?? '').replace(/\\r\\n/g, '\\n').trim();
  if (!source) return '';
  const lines = source.split('\\n');
  const parts = [];
  let inUl = false;
  let inOl = false;
  let paragraph = [];
  const flushParagraph = () => {
    if (!paragraph.length) return;
    parts.push(`<p>${inlineMarkdownToHtml(paragraph.join(' '))}</p>`);
    paragraph = [];
  };
  const closeLists = () => {
    if (inUl) {
      parts.push('</ul>');
      inUl = false;
    }
    if (inOl) {
      parts.push('</ol>');
      inOl = false;
    }
  };
  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      flushParagraph();
      closeLists();
      continue;
    }
    if (/^---+$/.test(line) || /^\\*\\*\\*+$/.test(line)) {
      flushParagraph();
      closeLists();
      parts.push('<hr>');
      continue;
    }
    const heading = line.match(/^(#{1,4})\\s+(.+)$/);
    if (heading) {
      flushParagraph();
      closeLists();
      const level = heading[1].length;
      parts.push(`<h${level}>${inlineMarkdownToHtml(heading[2])}</h${level}>`);
      continue;
    }
    const unordered = line.match(/^[-*]\\s+(.+)$/);
    if (unordered) {
      flushParagraph();
      if (inOl) {
        parts.push('</ol>');
        inOl = false;
      }
      if (!inUl) {
        parts.push('<ul>');
        inUl = true;
      }
      parts.push(`<li>${inlineMarkdownToHtml(unordered[1])}</li>`);
      continue;
    }
    const ordered = line.match(/^\\d+\\.\\s+(.+)$/);
    if (ordered) {
      flushParagraph();
      if (inUl) {
        parts.push('</ul>');
        inUl = false;
      }
      if (!inOl) {
        parts.push('<ol>');
        inOl = true;
      }
      parts.push(`<li>${inlineMarkdownToHtml(ordered[1])}</li>`);
      continue;
    }
    closeLists();
    paragraph.push(line);
  }
  flushParagraph();
  closeLists();
  return parts.join('');
}
function renderRichText(value) {
  const raw = String(value ?? '').trim();
  if (!raw) return '<div class="empty">No content.</div>';
  if (/<[a-z][\\s\\S]*>/i.test(raw)) {
    return `<div class='rendered-content'>${raw}</div>`;
  }
  return `<div class='rendered-content'>${markdownToHtml(raw)}</div>`;
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
    if (!title && !body && !emailSubject && !emailBody) {
      el.innerHTML = `<div class='empty'>No readable lesson view.</div>`;
      return;
    }
    el.innerHTML = `
      <div class='human-question'>${escapeHtml(title || 'Untitled lesson')}</div>
      <div class='human-meta'>${escapeHtml(emailSubject ? `Email subject: ${emailSubject}` : 'No email subject.')}</div>
      <div class='choice-item'>${renderRichText(body || 'No lesson content.')}</div>
      <div class='human-meta'>Email body:</div>
      <div class='choice-item'>${renderRichText(emailBody || 'No email body.')}</div>
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
function applySnapshot(feed, health, creatorSnapshot, lastActionText = 'Feed refreshed.') {
  window.__CURRENT_WORKER__ = health.worker || {};
  document.getElementById('generatedAt').textContent = `Updated ${feed.generatedAt}`;
  document.getElementById('workspace').textContent = health.workspaceRoot || '';
  document.getElementById('workspaceQc').textContent = health.workspaceRoot || '';
  document.getElementById('questionCount').textContent = (feed.inventory && feed.inventory.questions) || (health.inventory && health.inventory.questions) || 0;
  document.getElementById('lessonCount').textContent = (feed.inventory && feed.inventory.lessons) || (health.inventory && health.inventory.lessons) || 0;
  document.getElementById('courseCount').textContent = (feed.inventory && feed.inventory.courses) || (health.inventory && health.inventory.courses) || 0;
  document.getElementById('queuedCount').textContent = feed.counts.pending || 0;
  document.getElementById('runningCount').textContent = feed.counts.running || 0;
  document.getElementById('completedCount').textContent = feed.counts.completed || 0;
  document.getElementById('failedCount').textContent = feed.failedCount || feed.counts.failed || 0;
  document.getElementById('quarantinedCount').textContent = feed.quarantinedCount || feed.counts.quarantined || 0;
  document.getElementById('archivedCount').textContent = feed.archivedCount || 0;
  renderJobs('queuedJobs', feed.queued, 'No queued jobs.');
  renderJobs('runningJobs', feed.running, 'No running jobs.');
  renderJobs('completedJobs', feed.completed, 'No completed jobs yet.');
  renderJobs('failedJobs', feed.failed, 'No failed jobs.');
  renderJobs('quarantinedJobs', feed.quarantined, 'No quarantined jobs.');
  renderJobs('archivedJobs', feed.archived, 'No archived jobs.');
  renderCreatorRuns(creatorSnapshot || { runs: [], activeRunCount: 0 });
  renderWorkerStatus(health.worker || {});
  renderRuntime(health.runtime || {}, (health.system && health.system.residentRoles) || []);
  renderPower(health.power || { mode: '-', profiles: {} });
  document.getElementById('lastAction').textContent = lastActionText;
}
async function refreshAll() {
  try {
    const [feed, health, creator] = await Promise.all([fetchJson('/api/feed'), fetchJson('/api/health'), fetchJson('/api/creator/runs')]);
    applySnapshot(feed, health, creator, 'Feed refreshed.');
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
async function refreshCreatorRuns() {
  try {
    const creator = await fetchJson('/api/creator/runs');
    renderCreatorRuns(creator);
    document.getElementById('lastAction').textContent = JSON.stringify(creator, null, 2);
  } catch (error) {
    document.getElementById('lastAction').textContent = error instanceof Error ? error.message : String(error);
  }
}
async function createCreatorRun() {
  const topic = document.getElementById('creatorTopic').value.trim();
  const targetLanguage = document.getElementById('creatorLanguage').value.trim() || 'en';
  const researchMode = document.getElementById('creatorResearchMode').value.trim() || 'optional';
  if (!topic) {
    window.alert('Course topic is required.');
    return;
  }
  const result = await postAction('/api/creator/runs', { topic, targetLanguage, researchMode });
  if (result && result.run && result.run.runId) {
    document.getElementById('creatorTopic').value = '';
    await openCreatorRun(result.run.runId);
  }
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
    const kindLabel = normalizedTaskKind(task.kind);
    document.getElementById('modalMeta').textContent = `${kindLabel} | ${task.displayStatus || task.status} | attempts ${task.attempts}`;
    const hasAfterDraft = !!(task.details && task.details.after);
    const changedFields = task.details && task.details.changedFields ? task.details.changedFields.join(', ') : '-';
    const warnings = task.details && task.details.warnings ? task.details.warnings.join('; ') : 'none';
    const resolvedErrors = task.details && task.details.resolvedErrors ? task.details.resolvedErrors.join('; ') : 'none';
    const remainingErrors = task.details && task.details.remainingErrors ? task.details.remainingErrors.join('; ') : 'none';
    const recoveryMode = task.details && task.details.recoveryMode ? task.details.recoveryMode : '-';
    const partialApplied = task.details && task.details.partialApplied ? 'yes' : 'no';
    const providerTimings = Array.isArray(task.details && task.details.providerTimings) ? task.details.providerTimings : [];
    const rca = task.details && task.details.rca ? task.details.rca : null;
    const quarantine = task.details && task.details.quarantine ? task.details.quarantine : null;
    const summaryLines = [
      `Changed fields: ${changedFields}`,
      `Resolved errors: ${resolvedErrors}`,
      `Remaining errors: ${remainingErrors}`,
      `Warnings: ${warnings}`,
      `Recovery mode: ${recoveryMode}`,
      `Partial draft saved: ${partialApplied}`,
      `Backup: ${task.details && task.details.backup ? task.details.backup : '-'}`,
    ];
    if (!hasAfterDraft) summaryLines.unshift('Rewrite result: no draft was produced before the task failed.');
    if (providerTimings.length) summaryLines.push(`Provider timings: ${providerTimings.map(item => `${item.provider}:${item.status}:${item.durationMs}ms`).join(' | ')}`);
    if (rca) summaryLines.push(`RCA: ${rca.type || '-'} | ${rca.summary || '-'}`);
    if (quarantine) summaryLines.push(`Quarantine: ${quarantine.status || 'active'} | attempts ${quarantine.attempts || task.attempts}`);
    document.getElementById('modalSummary').textContent = summaryLines.join('\\n');
    renderHumanContent('modalBeforeHuman', task.details && task.details.before ? task.details.before : null, kindLabel);
    if (hasAfterDraft) {
      renderHumanContent('modalAfterHuman', task.details.after, kindLabel);
    } else {
      document.getElementById('modalAfterHuman').innerHTML = `<div class='empty'>No rewritten draft was saved before failure.</div>`;
    }
    renderChangeSummary(task);
    const feedback = (task.feedback || []).map(item => `${item.createdAt}: ${item.comment}`).join('\\n\\n');
    document.getElementById('modalFeedbackHistory').textContent = feedback || 'No feedback yet.';
    document.getElementById('challengeComment').value = '';
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    document.getElementById('modalSummary').textContent = `Failed to load task detail.\n${message}`;
    document.getElementById('modalBeforeHuman').innerHTML = `<div class='empty'>Failed to load detail.</div>`;
    document.getElementById('modalAfterHuman').innerHTML = `<div class='empty'>Failed to load detail.</div>`;
    document.getElementById('modalChangeSummary').innerHTML = `<div class='empty'>Failed to load detail.</div>`;
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
  await runActionWithFeedback({
    buttonId: 'challengeTaskButton',
    busyLabel: 'Requeuing...',
    feedbackId: 'detailActionFeedback',
    startMessage: 'Challenging result and requeueing task...',
    successMessage: 'Task challenged and requeued.',
    action: () => postAction('/api/challenge', { taskKey: currentDetailTaskKey, comment }),
  });
  closeModal();
}
async function openCreatorRun(runId) {
  const isSameRun = currentCreatorRunId === runId;
  currentCreatorRunId = runId;
  currentCreatorStageKey = null;
  if (!isSameRun) {
    currentCreatorReviewIndex = 0;
    currentCreatorEditMode = false;
  }
  document.getElementById('creatorModal').classList.add('open');
  document.getElementById('creatorModalTitle').textContent = 'Creator Run';
  document.getElementById('creatorModalMeta').textContent = runId;
  document.getElementById('creatorModalSummary').textContent = 'Loading...';
  document.getElementById('creatorDraftSummary').innerHTML = "<div class='empty'>Loading...</div>";
  document.getElementById('creatorArtifactSummary').innerHTML = "<div class='empty'>Loading...</div>";
  document.getElementById('creatorSourcePack').innerHTML = "<div class='empty'>Loading...</div>";
  document.getElementById('creatorStageWarning').textContent = 'Loading...';
  resetCreatorSourceForm();
  document.getElementById('creatorArtifactPreview').innerHTML = "<div class='empty'>Loading...</div>";
  document.getElementById('creatorArtifactEditor').value = '';
  document.getElementById('creatorNotes').innerHTML = "<div class='empty'>Loading...</div>";
  document.getElementById('creatorEvents').innerHTML = "<div class='empty'>Loading...</div>";
  document.getElementById('creatorComment').value = '';
  applyCreatorFeedback(runId);
  try {
    const result = await fetchJson(`/api/creator/run?runId=${encodeURIComponent(runId)}`);
    const run = result.run;
    if (!run) {
      document.getElementById('creatorModalSummary').textContent = 'Creator run not found.';
      return;
    }
    document.getElementById('creatorModalTitle').textContent = run.topic || run.runId;
    document.getElementById('creatorModalMeta').textContent = `status ${run.status || '-'} | language ${run.targetLanguage || '-'} | research ${run.researchMode || '-'}`;
    document.getElementById('creatorModalSummary').textContent = [
      `Run id: ${run.runId || '-'}`,
      `Active stage: ${creatorStageLabel(run.activeStage || '-')}`,
      `Created: ${run.createdAt || '-'}`,
      `Updated: ${run.updatedAt || '-'}`,
    ].join('\\n');
    const draftSummary = run.draftSummary || {};
    const artifactSummaries = run.artifactSummaries || {};
    const stageBlueprint = (run.payload && run.payload.stageBlueprint) || {};
    const sourcePack = (run.payload && run.payload.sourcePack) || [];
    const activeStageKey = run.activeStage || '';
    currentCreatorStageKey = activeStageKey;
    const activeStagePlan = stageBlueprint[activeStageKey] || {};
    const stageArtifacts = (run.payload && run.payload.stageArtifacts) || {};
    const activeArtifact = stageArtifacts[activeStageKey] || {};
    const preferredSources = sourcePack.filter((item) => String(item.reviewStatus || 'neutral') === 'preferred');
    const rejectedSources = sourcePack.filter((item) => String(item.reviewStatus || 'neutral') === 'rejected');
    const summaryItems = [
      ['Course title candidate', draftSummary.courseTitleCandidate || run.topic || '-'],
      ['Target language', draftSummary.targetLanguage || run.targetLanguage || '-'],
      ['Research mode', draftSummary.researchMode || run.researchMode || '-'],
      ['Operating model', draftSummary.operatingModel || '-'],
      ['Compatibility contract', draftSummary.compatibilityContract || '-'],
      ['QC progress', draftSummary.qcProgress || '-'],
      ['Draft package status', draftSummary.draftPackageStatus || '-'],
      ['Draft package', ((run.payload && run.payload.promotion) || {}).packagePath || '-'],
      ['Amanoba draft import', draftSummary.amanobaDraftImportStatus || '-'],
      ['Amanoba draft course', draftSummary.amanobaDraftCourseId || '-'],
      ['Amanoba live status', draftSummary.amanobaLiveStatus || '-'],
      ['Amanoba live course', draftSummary.amanobaLiveCourseId || '-'],
      ['Amanoba rollback', draftSummary.amanobaRollbackStatus || '-'],
      ['Amanoba delete import', draftSummary.amanobaDeleteStatus || '-'],
      ['Next checkpoint', draftSummary.nextCheckpoint || '-'],
      ['Current stage goal', activeStagePlan.goal || '-'],
      ['Current stage checkpoint', activeStagePlan.checkpoint || '-'],
    ];
    document.getElementById('creatorDraftSummary').innerHTML = summaryItems.map(([label, value]) => `
      <div class='creator-summary-item'>
        <div class='label'>${escapeHtml(label)}</div>
        <div>${escapeHtml(value)}</div>
      </div>
    `).join('');
    const activeSummary = artifactSummaries[activeStageKey] || {};
    const summaryStats = Array.isArray(activeSummary.stats) ? activeSummary.stats : [];
    const summarySamples = Array.isArray(activeSummary.samples) ? activeSummary.samples : [];
    const summaryRows = [];
    const lifecycle = creatorLifecycleState(run);
    const warning = creatorStageWarning(run);
    if (activeSummary.headline) {
      summaryRows.push(`
        <div class='creator-summary-item'>
          <div class='label'>${escapeHtml(creatorStageLabel(activeStageKey || 'artifact'))}</div>
          <div>${escapeHtml(activeSummary.headline)}</div>
        </div>
      `);
    }
    if (summaryStats.length) {
      summaryRows.push(`
        <div class='creator-summary-item'>
          <div class='label'>Stats</div>
          <div>${summaryStats.map((item) => escapeHtml(item)).join('<br>')}</div>
        </div>
      `);
    }
    if (summarySamples.length) {
      summaryRows.push(`
        <div class='creator-summary-item'>
          <div class='label'>Sample Titles</div>
          <div>${summarySamples.map((item) => escapeHtml(item)).join('<br>')}</div>
        </div>
      `);
    }
    if (sourcePack.length && activeStageKey !== 'qc_review' && activeStageKey !== 'draft_to_live') {
      summaryRows.push(`
        <div class='creator-summary-item'>
          <div class='label'>Grounding Basis</div>
          <div>${escapeHtml(`${sourcePack.length} sources · preferred ${preferredSources.length} · rejected ${rejectedSources.length}`)}${preferredSources.length ? `<br>${preferredSources.slice(0, 3).map((item) => escapeHtml(item.domain || item.title || '-')).join('<br>')}` : ''}</div>
        </div>
      `);
    }
    if (activeStageKey !== 'qc_review') {
      summaryRows.push(`
        <div class='creator-summary-item'>
          <div class='label'>Decision Risk</div>
          <div><strong>${escapeHtml(warning.title)}</strong><br>${escapeHtml(warning.detail)}</div>
        </div>
      `);
    }
    if (activeStageKey === 'qc_review' || activeStageKey === 'draft_to_live' || lifecycle.runStatus === 'completed') {
      const qc = ((run.payload || {}).qcStatus) || {};
      summaryRows.push(`
        <div class='creator-summary-item'>
          <div class='label'>QC Readiness</div>
          <div>${escapeHtml(lifecycle.qcReady ? 'Ready for downstream release.' : 'Not ready for downstream release yet.')}<br>${escapeHtml(`${qc.completed || 0}/${qc.total || 0} complete · failed ${qc.failed || 0} · quarantined ${qc.quarantined || 0}`)}</div>
        </div>
      `);
    }
    if (activeStageKey === 'draft_to_live' || lifecycle.runStatus === 'completed') {
      const releaseSteps = [
        lifecycle.hasPackage ? 'Package exported' : 'Package missing',
        lifecycle.isDraftImported ? 'Amanoba draft imported' : 'Amanoba draft import missing',
        lifecycle.isPublished ? 'Published live' : 'Live publish pending',
      ];
      summaryRows.push(`
        <div class='creator-summary-item'>
          <div class='label'>Release Readiness</div>
          <div>${releaseSteps.map((item) => escapeHtml(item)).join('<br>')}</div>
        </div>
      `);
    }
    document.getElementById('creatorArtifactSummary').innerHTML = summaryRows.join('') || "<div class='empty'>No artifact summary for this stage.</div>";
    document.getElementById('creatorSourcePack').innerHTML = sourcePack.length ? sourcePack.map((item) => {
      const encoded = encodeURIComponent(JSON.stringify({
        sourceId: item.sourceId || '',
        title: item.title || '',
        url: item.url || '',
        sourceType: item.sourceType || '',
        score: item.score || '',
        snippet: item.snippet || '',
      }));
      return `
      <div class='creator-event-item'>
        <div><strong>${escapeHtml(item.title || item.url || 'Untitled source')}</strong></div>
        <div class='badge-row'>${sourceStatusBadge(item.reviewStatus || 'neutral')}</div>
        <div class='tiny'>${escapeHtml(item.sourceType || '-')} | domain ${escapeHtml(item.domain || '-')} | score ${escapeHtml(item.score || '-')} | fetched ${escapeHtml(item.fetchedAt || '-')}</div>
        ${item.url ? `<div class='tiny'><a href='${escapeHtml(item.url)}' target='_blank' rel='noreferrer'>${escapeHtml(item.url)}</a></div>` : ''}
        <div>${escapeHtml(item.snippet || 'No snippet.')}</div>
        <div class='row-actions' style='margin-top:8px;'>
          <button class='secondary small' onclick='editCreatorSourceFromEncoded("${encoded}"); return false;'>Edit</button>
          <button class='small' onclick='setCreatorSourceStatus("${escapeHtml(item.sourceId || "")}", "preferred", this)'>Prefer</button>
          <button class='secondary small' onclick='setCreatorSourceStatus("${escapeHtml(item.sourceId || "")}", "neutral", this)'>Clear</button>
          <button class='danger small' onclick='setCreatorSourceStatus("${escapeHtml(item.sourceId || "")}", "rejected", this)'>Reject</button>
          <button class='danger small' onclick='deleteCreatorSource("${escapeHtml(item.sourceId || "")}", this)'>Delete</button>
        </div>
      </div>
    `;
    }).join('') : "<div class='empty'>No external sources collected yet.</div>";
    resetCreatorSourceForm();
    document.getElementById('creatorArtifactPreview').innerHTML = activeArtifact.content
      ? renderRichText(activeArtifact.content)
      : "<div class='empty'>No stage artifact yet.</div>";
    document.getElementById('creatorArtifactEditor').value = activeArtifact.content || '';
    const notes = Array.isArray(run.notes) ? run.notes : [];
    document.getElementById('creatorNotes').innerHTML = notes.length ? notes.slice().reverse().map((note) => `
      <div class='creator-event-item'>
        <div><strong>${escapeHtml(creatorStageLabel(note.stageKey || note.type || 'note'))}</strong></div>
        <div class='tiny'>${escapeHtml(note.createdAt || '-')}</div>
        <div>${escapeHtml(note.comment || 'No comment.')}</div>
      </div>
    `).join('') : "<div class='empty'>No run notes yet.</div>";
    const events = Array.isArray(run.events) ? run.events : [];
    document.getElementById('creatorEvents').innerHTML = events.length ? events.map((item) => `
      <div class='creator-event-item'>
        <div><strong>${escapeHtml(creatorStageLabel(item.stageKey || '-'))}</strong> · ${escapeHtml(creatorStageLabel(item.action || '-'))}</div>
        <div class='tiny'>${escapeHtml(item.createdAt || '-')}</div>
        <div>${escapeHtml(item.comment || 'No comment.')}</div>
      </div>
    `).join('') : "<div class='empty'>No events yet.</div>";
    currentCreatorRunData = run;
    updateCreatorModalVisibility(activeStageKey, run);
    renderCreatorStageFocus(run, activeStageKey, activeArtifact);
    renderCreatorChecklist(run);
    renderCreatorControls(run);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    document.getElementById('creatorModalSummary').textContent = message;
    document.getElementById('creatorDraftSummary').innerHTML = "<div class='empty'>Failed to load creator run.</div>";
    document.getElementById('creatorArtifactSummary').innerHTML = "<div class='empty'>Failed to load creator run.</div>";
    document.getElementById('creatorChecklist').innerHTML = "<div class='empty'>Failed to load creator run.</div>";
    document.getElementById('creatorWorkflowBanner').textContent = 'Failed to load creator run.';
    document.getElementById('creatorStageWarning').textContent = 'Failed to load creator run.';
    document.getElementById('creatorSourcePack').innerHTML = "<div class='empty'>Failed to load creator run.</div>";
    document.getElementById('creatorArtifactPreview').innerHTML = "<div class='empty'>Failed to load creator run.</div>";
    document.getElementById('creatorStageFocusMeta').textContent = 'Failed to load creator run.';
    document.getElementById('creatorStageFocusBody').innerHTML = "<div class='empty'>Failed to load creator run.</div>";
    document.getElementById('creatorStageFocusNav').innerHTML = '';
    document.getElementById('creatorArtifactEditor').value = '';
    document.getElementById('creatorNotes').innerHTML = "<div class='empty'>Failed to load creator run.</div>";
    document.getElementById('creatorEvents').innerHTML = "<div class='empty'>Failed to load creator run.</div>";
  }
}
function closeCreatorModal() {
  currentCreatorRunId = null;
  currentCreatorStageKey = null;
  currentCreatorSourceId = null;
  currentCreatorRunData = null;
  currentCreatorEditMode = false;
  document.getElementById('creatorModal').classList.remove('open');
}
async function saveCreatorArtifact() {
  if (!currentCreatorRunId) return;
  const content = document.getElementById('creatorArtifactEditor').value;
  const result = await runActionWithFeedback({
    buttonId: 'creatorSaveButton',
    busyLabel: 'Saving...',
    feedbackId: 'creatorActionFeedback',
    startMessage: 'Saving artifact...',
    successMessage: 'Artifact saved.',
    action: () => postAction('/api/creator/artifact', {
      runId: currentCreatorRunId,
      stageKey: currentCreatorStageKey,
      content,
    }),
  });
  if (result && result.run && result.run.runId) {
    rememberCreatorFeedback('good', 'Manual changes saved.', result.run.runId);
    await openCreatorRun(result.run.runId);
  }
}
async function saveCreatorSource(buttonEl) {
  if (!currentCreatorRunId) return;
  const source = {
    sourceId: currentCreatorSourceId || '',
    title: document.getElementById('creatorSourceTitle').value.trim(),
    url: document.getElementById('creatorSourceUrl').value.trim(),
    sourceType: document.getElementById('creatorSourceType').value.trim(),
    score: document.getElementById('creatorSourceScore').value.trim(),
    snippet: document.getElementById('creatorSourceSnippet').value.trim(),
  };
  const result = await runActionWithFeedback({
    buttonEl,
    busyLabel: 'Saving...',
    feedbackId: 'creatorActionFeedback',
    startMessage: source.sourceId ? 'Saving source update...' : 'Saving new source...',
    successMessage: source.sourceId ? 'Source updated.' : 'Source added.',
    action: () => postAction('/api/creator/source-save', {
      runId: currentCreatorRunId,
      source,
    }),
  });
  if (result.run) {
    rememberCreatorFeedback('good', source.sourceId ? 'Source updated.' : 'Source added.', result.run.runId);
    await openCreatorRun(result.run.runId);
    await refreshCreatorRuns();
    const pack = (((result.run || {}).payload || {}).sourcePack || []);
    const saved = pack.find((item) => String(item.sourceId || '') === String(source.sourceId || '')) || pack.find((item) => String(item.title || '') === source.title && String(item.url || '') === source.url);
    if (saved) loadCreatorSource(saved);
  }
}
async function deleteCreatorSource(sourceId, buttonEl) {
  if (!currentCreatorRunId || !sourceId) return;
  const result = await runActionWithFeedback({
    buttonEl,
    busyLabel: 'Deleting...',
    feedbackId: 'creatorActionFeedback',
    startMessage: 'Deleting source...',
    successMessage: 'Source deleted.',
    action: () => postAction('/api/creator/source-delete', {
      runId: currentCreatorRunId,
      sourceId,
    }),
  });
  if (result.run) {
    rememberCreatorFeedback('good', 'Source deleted.', result.run.runId);
    await openCreatorRun(result.run.runId);
    await refreshCreatorRuns();
  }
}
async function refreshCreatorSources(buttonEl) {
  if (!currentCreatorRunId) return;
  const result = await runActionWithFeedback({
    buttonEl,
    busyLabel: 'Refreshing...',
    feedbackId: 'creatorActionFeedback',
    startMessage: 'Refreshing source pack...',
    successMessage: 'Source pack refreshed.',
    action: () => postAction('/api/creator/source-refresh', {
      runId: currentCreatorRunId,
    }),
  });
  if (result.run) {
    rememberCreatorFeedback('good', 'Source pack refreshed.', result.run.runId);
    await openCreatorRun(result.run.runId);
    await refreshCreatorRuns();
  }
}
async function setCreatorSourceStatus(sourceId, reviewStatus, buttonEl) {
  if (!currentCreatorRunId || !sourceId) return;
  const actionLabel =
    reviewStatus === 'preferred' ? 'Marking source as preferred...'
    : reviewStatus === 'rejected' ? 'Rejecting source...'
    : 'Clearing source review state...';
  const successLabel =
    reviewStatus === 'preferred' ? 'Source marked preferred.'
    : reviewStatus === 'rejected' ? 'Source rejected.'
    : 'Source review cleared.';
  const result = await runActionWithFeedback({
    buttonEl,
    busyLabel: 'Saving...',
    feedbackId: 'creatorActionFeedback',
    startMessage: actionLabel,
    successMessage: successLabel,
    action: () => postAction('/api/creator/source-status', {
      runId: currentCreatorRunId,
      sourceId,
      reviewStatus,
    }),
  });
  if (result.run) {
    const label =
      reviewStatus === 'preferred' ? 'Source marked preferred.'
      : reviewStatus === 'rejected' ? 'Source rejected.'
      : 'Source review cleared.';
    rememberCreatorFeedback('good', label, result.run.runId);
    await openCreatorRun(result.run.runId);
    await refreshCreatorRuns();
  }
}
async function generateCreatorArtifact() {
  if (!currentCreatorRunId) return;
  const comment = document.getElementById('creatorComment').value.trim();
  const result = await runActionWithFeedback({
    buttonId: 'creatorGenerateButton',
    busyLabel: 'Working...',
    feedbackId: 'creatorActionFeedback',
    startMessage: comment ? 'Making a new draft from your note...' : 'Making a new draft...',
    successMessage: comment ? 'New draft created from your note.' : 'New draft created.',
    action: () => postAction('/api/creator/generate', {
      runId: currentCreatorRunId,
      stageKey: currentCreatorStageKey,
      comment,
    }),
  });
  if (result && result.run && result.run.runId) {
    rememberCreatorFeedback('good', comment ? 'New draft created from your note.' : 'New draft created.', result.run.runId);
    await openCreatorRun(result.run.runId);
    await refreshCreatorRuns();
  }
}
async function submitCreatorAction(action) {
  if (!currentCreatorRunId) return;
  const comment = document.getElementById('creatorComment').value.trim();
  const buttonId =
    action === 'accept' ? 'creatorAcceptButton'
    : action === 'update' ? 'creatorUpdateButton'
    : action === 'delete' ? 'creatorDeleteButton'
    : '';
  const busyLabel =
    action === 'accept' ? 'Accepting...'
    : action === 'update' ? 'Sending Back...'
    : action === 'delete' ? 'Deleting...'
    : 'Working...';
  const startMessage =
    action === 'accept' ? 'Accepting current stage...'
    : action === 'update' ? 'Sending stage back for update...'
    : action === 'delete' ? 'Deleting creator run...'
    : 'Working...';
  const successMessage =
    action === 'accept' ? 'Stage accepted.'
    : action === 'update' ? 'Stage sent back for update.'
    : action === 'delete' ? 'Creator run deleted.'
    : 'Action completed.';
  const result = await runActionWithFeedback({
    buttonId,
    busyLabel,
    feedbackId: 'creatorActionFeedback',
    startMessage,
    successMessage,
    action: () => postAction('/api/creator/action', { runId: currentCreatorRunId, action, comment }),
  });
  if (result && result.run && result.run.runId) {
    const doneMessage =
      action === 'accept' ? 'Stage approved. The run moved to the next step.'
      : action === 'update' ? 'Your note was saved. This stage is now waiting for a new draft.'
      : 'Creator run deleted.';
    rememberCreatorFeedback(action === 'delete' ? 'warn' : 'good', doneMessage, result.run.runId);
    await openCreatorRun(result.run.runId);
    await refreshCreatorRuns();
  }
}
async function promoteCreatorDraft() {
  if (!currentCreatorRunId) return;
  const result = await runActionWithFeedback({
    buttonId: 'creatorPromoteButton',
    busyLabel: 'Promoting...',
    feedbackId: 'creatorActionFeedback',
    startMessage: 'Exporting draft package...',
    successMessage: 'Draft package exported.',
    action: () => postAction('/api/creator/promote', { runId: currentCreatorRunId }),
  });
  if (result && result.run && result.run.runId) {
    rememberCreatorFeedback('good', 'Draft package exported.', result.run.runId);
    await openCreatorRun(result.run.runId);
    await refreshCreatorRuns();
  }
}
async function importCreatorDraft() {
  if (!currentCreatorRunId) return;
  const result = await runActionWithFeedback({
    buttonId: 'creatorImportButton',
    busyLabel: 'Importing...',
    feedbackId: 'creatorActionFeedback',
    startMessage: 'Importing draft into Amanoba...',
    successMessage: 'Draft imported into Amanoba.',
    action: () => postAction('/api/creator/import', { runId: currentCreatorRunId }),
  });
  if (result && result.run && result.run.runId) {
    rememberCreatorFeedback('good', 'Draft imported into Amanoba.', result.run.runId);
    await openCreatorRun(result.run.runId);
    await refreshCreatorRuns();
  }
}
async function publishCreatorDraft() {
  if (!currentCreatorRunId) return;
  const result = await runActionWithFeedback({
    buttonId: 'creatorPublishButton',
    busyLabel: 'Publishing...',
    feedbackId: 'creatorActionFeedback',
    startMessage: 'Publishing Amanoba draft...',
    successMessage: 'Amanoba course published.',
    action: () => postAction('/api/creator/publish', { runId: currentCreatorRunId }),
  });
  if (result && result.run && result.run.runId) {
    rememberCreatorFeedback('good', 'Course published in Amanoba.', result.run.runId);
    await openCreatorRun(result.run.runId);
    await refreshCreatorRuns();
  }
}
async function rollbackCreatorPublish() {
  if (!currentCreatorRunId) return;
  const result = await runActionWithFeedback({
    buttonId: 'creatorRollbackButton',
    busyLabel: 'Rolling Back...',
    feedbackId: 'creatorActionFeedback',
    startMessage: 'Rolling live course back to draft...',
    successMessage: 'Live publish rolled back.',
    action: () => postAction('/api/creator/rollback-publish', { runId: currentCreatorRunId }),
  });
  if (result && result.run && result.run.runId) {
    rememberCreatorFeedback('warn', 'Live course rolled back to draft.', result.run.runId);
    await openCreatorRun(result.run.runId);
    await refreshCreatorRuns();
  }
}
async function deleteCreatorImport() {
  if (!currentCreatorRunId) return;
  const result = await runActionWithFeedback({
    buttonId: 'creatorDeleteImportButton',
    busyLabel: 'Deleting...',
    feedbackId: 'creatorActionFeedback',
    startMessage: 'Deleting Amanoba draft...',
    successMessage: 'Amanoba draft deleted.',
    action: () => postAction('/api/creator/delete-import', { runId: currentCreatorRunId }),
  });
  if (result && result.run && result.run.runId) {
    rememberCreatorFeedback('warn', 'Amanoba draft deleted.', result.run.runId);
    await openCreatorRun(result.run.runId);
    await refreshCreatorRuns();
  }
}
document.getElementById('detailModal').addEventListener('click', (event) => {
  if (event.target.id === 'detailModal') closeModal();
});
document.getElementById('creatorModal').addEventListener('click', (event) => {
  if (event.target.id === 'creatorModal') closeCreatorModal();
});
window.addEventListener('hashchange', syncPageFromHash);
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
resetStaleUiState();
applySnapshot(INITIAL_FEED, INITIAL_HEALTH, INITIAL_CREATOR, `Live snapshot loaded. Build ${BUILD_STAMP}`);
syncPageFromHash();
refreshAll();
setInterval(refreshAll, 5000);
</script>
</body>
</html>
"""


def render_dashboard_html(daemon: CourseQualityDaemon) -> str:
    feed = daemon.feed_snapshot()
    health = daemon.health_snapshot()
    creator = daemon.creator_runs_snapshot()
    build_stamp = str(health.get("generatedAt") or feed.get("generatedAt") or "")
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

    def runtime_html(runtime: dict[str, Any], resident_roles: list[dict[str, Any]]) -> str:
        def provider_summary(item: dict[str, Any]) -> tuple[str, str, str, str, str | None]:
            provider = str(item.get("provider") or "").strip().lower()
            configured = str(item.get("configuredModel") or "").strip()
            resolved = str(item.get("resolvedModel") or "").strip()
            endpoint = str(item.get("endpoint") or "").strip()
            if provider == "mlx":
                return ("Model", "Apertus 8B Instruct 4bit", None, None, "Endpoint", endpoint or "-")
            model_value = resolved or configured or "-"
            return ("Model", model_value, None, None, "Endpoint", endpoint or "-")

        rows = []
        for item in runtime.get("providers") or []:
            status = str(item.get("status") or "")
            cls = "good" if status in {"HEALTHY", "STANDBY", "completed"} else ("warn" if status in {"DEGRADED", "pending", "running"} else "bad")
            model_label, model_value, extra_label, extra_value, endpoint_label, endpoint_value = provider_summary(item)
            rows.append(
                "<div class='runtime-item'>"
                f"<div><strong>{esc(item.get('provider') or '-')}</strong> <span class='status {cls}'>{esc(status)}</span></div>"
                f"<div class='tiny'>{esc(item.get('detail') or '')}</div>"
                f"<div class='tiny'>{esc(model_label)}: {esc(model_value)}</div>"
                + (f"<div class='tiny'>{esc(extra_label)}: {esc(extra_value)}</div>" if extra_label and extra_value else "")
                + f"<div class='tiny'>{esc(endpoint_label)}: {esc(endpoint_value)}</div>"
                "</div>"
            )
        for role in resident_roles:
            status = str(role.get("status") or "")
            cls = "good" if status in {"WARM", "HEALTHY"} else "bad"
            rows.append(
                "<div class='runtime-item'>"
                f"<div><strong>{esc(role.get('name') or 'ROLE')}</strong> <span class='status {cls}'>{esc(status)}</span></div>"
                "<div class='tiny'>Resident creator role</div>"
                + (f"<div class='tiny'>Model: {esc(role.get('modelLabel') or '')}</div>" if role.get("modelLabel") else "")
                + f"<div class='tiny'>Endpoint: {esc(role.get('host') or '127.0.0.1')}:{esc(role.get('port') or '-')}</div>"
                + f"<div class='tiny'>{esc(role.get('detail') or '')}</div>"
                "</div>"
            )
        if not rows:
            return "<div class='runtime-item'><div><strong>No runtime data</strong> <span class='status bad'>ERROR</span></div></div>"
        return "".join(rows)

    def creator_runs_html(snapshot: dict[str, Any]) -> str:
        def board_state(run: dict[str, Any]) -> tuple[str, str]:
            status = str(run.get("status") or "")
            stage = str(run.get("activeStage") or "")
            payload = dict(run.get("payload") or {})
            qc = dict(payload.get("qcStatus") or {})
            total = int(qc.get("total") or 0)
            completed = int(qc.get("completed") or 0)
            queued = int(qc.get("queued") or 0)
            running = int(qc.get("running") or 0)
            failed = int(qc.get("failed") or 0)
            quarantined = int(qc.get("quarantined") or 0)
            promotion = dict(payload.get("promotion") or {})
            import_status = dict(payload.get("importStatus") or {})
            publish_status = dict(payload.get("publishStatus") or {})
            has_package = bool(str(promotion.get("packagePath") or "").strip())
            is_imported = bool(str(import_status.get("courseId") or "").strip())
            is_published = str(publish_status.get("status") or "") == "published-live"
            if status == "completed":
                return ("completed", "Completed")
            if stage == "qc_review":
                if failed > 0 or quarantined > 0:
                    return ("blocked", "Blocked")
                if total <= 0:
                    return ("waiting", "Your Input Needed")
                if queued > 0 or running > 0 or completed < total:
                    return ("working", "System Working")
                return ("waiting", "Your Input Needed")
            if stage == "draft_to_live":
                if is_published:
                    return ("waiting", "Your Input Needed")
                if has_package or is_imported:
                    return ("waiting", "Your Input Needed")
                return ("waiting", "Your Input Needed")
            if stage:
                return ("waiting", "Your Input Needed")
            return ("idle", "Idle")

        runs = snapshot.get("runs") or []
        if not runs:
            return "<div class='empty'>No creator runs yet.</div>"
        rows = []
        for run in runs:
            artifact_summaries = run.get("artifactSummaries") or {}
            active_stage = str(run.get("activeStage") or "")
            active_summary = artifact_summaries.get(active_stage) or {}
            active_summary_html = f"<div class='tiny'>{esc(active_summary.get('headline') or '')}</div>" if active_summary.get("headline") else ""
            state_cls, state_label = board_state(run)
            rows.append(
                f"<div class='creator-run-card {esc(state_cls)}' data-run-id='{esc(run.get('runId') or '')}' tabindex='0' role='button' onclick='openCreatorRun(this.getAttribute(\"data-run-id\")); return false;' onkeydown='if(event.key===\"Enter\"||event.key===\" \"){{ event.preventDefault(); openCreatorRun(this.getAttribute(\"data-run-id\")); return false; }}'>"
                f"<div class='creator-title'>{esc(run.get('topic') or run.get('runId') or 'Untitled run')}</div>"
                f"<div class='creator-status-line'><span class='creator-status-dot'></span>{esc(state_label)}</div>"
                f"<div class='tiny'>language {esc(run.get('targetLanguage') or '-')} | research {esc(run.get('researchMode') or '-')}</div>"
                f"<div class='tiny'>status {esc(run.get('status') or '-')} | active stage {esc(str(run.get('activeStage') or '-').replace('_', ' '))}</div>"
                f"{active_summary_html}"
                f"<div class='tiny'>updated {esc(run.get('updatedAt') or '-')}</div>"
                "</div>"
            )
        return "".join(rows)

    power = health.get("power") or {}
    profiles = power.get("profiles") or {}
    profile = power.get("profile") or profiles.get(power.get("mode")) or {}
    power_summary = (
        f"Mode: <strong>{esc(power.get('mode') or '-')}</strong><br>"
        f"threads {esc(profile.get('num_thread') if profile.get('num_thread') is not None else '-')} | "
        f"tokens {esc(profile.get('num_predict') if profile.get('num_predict') is not None else '-')} | "
        f"ctx {esc(profile.get('num_ctx') if profile.get('num_ctx') is not None else '-')}<br>"
        f"lesson rewrite tokens {esc(profile.get('lesson_rewrite_predict') if profile.get('lesson_rewrite_predict') is not None else profile.get('num_predict') if profile.get('num_predict') is not None else '-')}"
    )
    worker = health.get("worker") or {}
    worker_phase = esc(worker.get("phase") or "unknown")
    worker_task = esc(worker.get("taskKey") or "")
    worker_heartbeat = esc(worker.get("heartbeatAt") or "-")
    worker_progress = esc(worker.get("progressAt") or "-")
    worker_started = esc(worker.get("taskStartedAt") or "-")
    worker_label = "actively processing" if worker.get("taskKey") else "idle and waiting for the next issue"
    worker_status_html = (
        f"<div><strong>Live Worker State</strong> <span class='status {'warn' if worker.get('taskKey') else 'good'}'>{esc(worker_label)}</span></div>"
        f"<div class='tiny'>phase: {worker_phase}{' | task ' + worker_task if worker_task else ''}</div>"
        f"<div class='tiny'>progress heartbeat: {worker_progress} | worker heartbeat: {worker_heartbeat}</div>"
        f"<div class='tiny'>task started: {worker_started}</div>"
    )

    html_doc = (
        HTML.replace("__INITIAL_FEED__", json.dumps(feed, ensure_ascii=False).replace("</", "<\\/"))
        .replace("__INITIAL_HEALTH__", json.dumps(health, ensure_ascii=False).replace("</", "<\\/"))
        .replace("__INITIAL_CREATOR__", json.dumps(creator, ensure_ascii=False).replace("</", "<\\/"))
        .replace("__BUILD_STAMP__", esc(build_stamp))
        .replace("__GENERATED_AT__", esc(f"Updated {feed.get('generatedAt') or '-'}"))
        .replace("__WORKSPACE__", esc(health.get("workspaceRoot") or ""))
        .replace("__WORKER_STATUS__", worker_status_html)
        .replace("__CREATOR_SUMMARY__", f"Visible runs <strong>{esc(creator.get('count') or 0)}</strong><br>Active runs <strong>{esc(creator.get('activeCount') or 0)}</strong>")
        .replace("__CREATOR_COUNT_LABEL__", esc(f"{creator.get('count') or 0} visible"))
        .replace("__CREATOR_HTML__", creator_runs_html(creator))
        .replace("__QUESTION_COUNT__", esc((feed.get("inventory") or {}).get("questions") or (health.get("inventory") or {}).get("questions") or 0))
        .replace("__LESSON_COUNT__", esc((feed.get("inventory") or {}).get("lessons") or (health.get("inventory") or {}).get("lessons") or 0))
        .replace("__COURSE_COUNT__", esc((feed.get("inventory") or {}).get("courses") or (health.get("inventory") or {}).get("courses") or 0))
        .replace("__QUEUED_COUNT__", esc((feed.get("counts") or {}).get("pending") or 0))
        .replace("__RUNNING_COUNT__", esc((feed.get("counts") or {}).get("running") or 0))
        .replace("__COMPLETED_COUNT__", esc((feed.get("counts") or {}).get("completed") or 0))
        .replace("__FAILED_COUNT__", esc(feed.get("failedCount") or (feed.get("counts") or {}).get("failed") or 0))
        .replace("__QUARANTINED_COUNT__", esc(feed.get("quarantinedCount") or (feed.get("counts") or {}).get("quarantined") or 0))
        .replace("__ARCHIVED_COUNT__", esc(feed.get("archivedCount") or 0))
        .replace("__QUEUED_HTML__", cards_html(feed.get("queued") or [], "No queued jobs."))
        .replace("__RUNNING_HTML__", cards_html(feed.get("running") or [], "No running jobs."))
        .replace("__COMPLETED_HTML__", cards_html(feed.get("completed") or [], "No completed jobs yet."))
        .replace("__FAILED_HTML__", cards_html(feed.get("failed") or [], "No failed jobs."))
        .replace("__QUARANTINED_HTML__", cards_html(feed.get("quarantined") or [], "No quarantined jobs."))
        .replace("__ARCHIVED_HTML__", cards_html(feed.get("archived") or [], "No archived jobs."))
        .replace("__POWER_SUMMARY__", power_summary)
        .replace("__RUNTIME_HTML__", runtime_html(health.get("runtime") or {}, ((health.get("system") or {}).get("residentRoles") or [])))
        .replace("__LAST_ACTION__", esc(f"Live snapshot loaded. Build {build_stamp}"))
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
        if parsed.path == "/api/creator/runs":
            params = parse_qs(parsed.query)
            limit = int(params.get("limit", ["12"])[0])
            self._send_json(self.daemon.creator_runs_snapshot(limit=limit))
            return
        if parsed.path == "/api/creator/run":
            params = parse_qs(parsed.query)
            run_id = str(params.get("runId", [""])[0])
            self._send_json({"run": self.daemon.creator_run_detail(run_id)})
            return
        if parsed.path == "/api/feed":
            params = parse_qs(parsed.query)
            limit = int(params.get("limit", [self.daemon.config.feed_limit])[0])
            self._send_json(self.daemon.feed_snapshot(limit=limit))
            return
        if parsed.path == "/api/health":
            self._send_json(self.daemon.dashboard_health_snapshot())
            return
        if parsed.path == "/api/healthz":
            worker = self.daemon.worker_status_snapshot()
            self._send_json(
                {
                    "ok": True,
                    "generatedAt": worker.get("heartbeatAt") or utc_now(),
                    "worker": {
                        "phase": worker.get("phase"),
                        "taskKey": worker.get("taskKey"),
                        "heartbeatAt": worker.get("heartbeatAt"),
                        "progressAt": worker.get("progressAt"),
                    },
                }
            )
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
        if parsed.path == "/api/creator/runs":
            body = self._read_json_body()
            topic = str(body.get("topic") or "").strip()
            target_language = str(body.get("targetLanguage") or "en").strip() or "en"
            research_mode = str(body.get("researchMode") or "optional").strip() or "optional"
            if not topic:
                self._send_json({"ok": False, "error": "Topic is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "run": self.daemon.create_creator_run(topic, target_language, research_mode)}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/creator/action":
            body = self._read_json_body()
            run_id = str(body.get("runId") or "").strip()
            action = str(body.get("action") or "").strip()
            comment = str(body.get("comment") or "")
            if not run_id or not action:
                self._send_json({"ok": False, "error": "runId and action are required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                result = self.daemon.creator_action(run_id, action, comment)
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "run": result}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/creator/artifact":
            body = self._read_json_body()
            run_id = str(body.get("runId") or "").strip()
            stage_key = str(body.get("stageKey") or "").strip() or None
            content = str(body.get("content") or "")
            if not run_id:
                self._send_json({"ok": False, "error": "runId is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                result = self.daemon.creator_save_artifact(run_id, content, stage_key)
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "run": result}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/creator/generate":
            body = self._read_json_body()
            run_id = str(body.get("runId") or "").strip()
            stage_key = str(body.get("stageKey") or "").strip() or None
            comment = str(body.get("comment") or "")
            if not run_id:
                self._send_json({"ok": False, "error": "runId is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                result = self.daemon.creator_generate_artifact(run_id, stage_key, comment)
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "run": result}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/creator/source-save":
            body = self._read_json_body()
            run_id = str(body.get("runId") or "").strip()
            source = dict(body.get("source") or {})
            if not run_id:
                self._send_json({"ok": False, "error": "runId is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                result = self.daemon.creator_save_source(run_id, source)
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "run": result}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/creator/source-delete":
            body = self._read_json_body()
            run_id = str(body.get("runId") or "").strip()
            source_id = str(body.get("sourceId") or "").strip()
            if not run_id or not source_id:
                self._send_json({"ok": False, "error": "runId and sourceId are required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                result = self.daemon.creator_delete_source(run_id, source_id)
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "run": result}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/creator/source-refresh":
            body = self._read_json_body()
            run_id = str(body.get("runId") or "").strip()
            if not run_id:
                self._send_json({"ok": False, "error": "runId is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                result = self.daemon.creator_refresh_sources(run_id)
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "run": result}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/creator/source-status":
            body = self._read_json_body()
            run_id = str(body.get("runId") or "").strip()
            source_id = str(body.get("sourceId") or "").strip()
            review_status = str(body.get("reviewStatus") or "").strip()
            if not run_id or not source_id or not review_status:
                self._send_json({"ok": False, "error": "runId, sourceId, and reviewStatus are required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                result = self.daemon.creator_set_source_status(run_id, source_id, review_status)
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "run": result}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/creator/promote":
            body = self._read_json_body()
            run_id = str(body.get("runId") or "").strip()
            if not run_id:
                self._send_json({"ok": False, "error": "runId is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                result = self.daemon.creator_promote_draft(run_id)
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "run": result}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/creator/import":
            body = self._read_json_body()
            run_id = str(body.get("runId") or "").strip()
            if not run_id:
                self._send_json({"ok": False, "error": "runId is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                result = self.daemon.creator_import_draft(run_id)
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "run": result}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/creator/publish":
            body = self._read_json_body()
            run_id = str(body.get("runId") or "").strip()
            if not run_id:
                self._send_json({"ok": False, "error": "runId is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                result = self.daemon.creator_publish_draft(run_id)
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "run": result}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/creator/rollback-publish":
            body = self._read_json_body()
            run_id = str(body.get("runId") or "").strip()
            if not run_id:
                self._send_json({"ok": False, "error": "runId is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                result = self.daemon.creator_rollback_publish(run_id)
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "run": result}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/creator/delete-import":
            body = self._read_json_body()
            run_id = str(body.get("runId") or "").strip()
            if not run_id:
                self._send_json({"ok": False, "error": "runId is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                result = self.daemon.creator_delete_import(run_id)
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"ok": True, "run": result}, status=HTTPStatus.ACCEPTED)
            return
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
