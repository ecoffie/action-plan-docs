#!/usr/bin/env node
/**
 * Builds review-dashboard-28.html from courses-28.json and scripts.json.
 * Embeds data so the dashboard works when opened via file:// (no server needed).
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const coursesPath = path.join(ROOT, 'data', 'courses-28.json');
const scriptsPath = path.join(ROOT, 'data', 'scripts', 'scripts.json');

const courses = JSON.parse(fs.readFileSync(coursesPath, 'utf8'));
const scriptsData = JSON.parse(fs.readFileSync(scriptsPath, 'utf8'));
const scripts = scriptsData.scripts || {};

// Map 28-course lesson IDs to legacy script keys (for narration)
const LESSON_TO_SCRIPT = {
  '1-1-1': '1-01-1', '1-1-2': '1-02-1', '1-1-3': '1-03-1', '1-2-1': '1-04-1',
  '1-3-1': '1-05-1', '1-4-1': '1-06-1', '1-5-1': '1-07-1', '1-6-1': '1-08-1',
  '2-1-1': '2-01-1', '2-2-1': '2-02-1', '2-3-1': '2-03-1', '2-4-1': '2-04-1',
  '2-5-1': '2-04-1', '2-6-1': '2-05-1',
  '3-1-1': '3-01-1', '3-2-1': '3-02-1', '3-3-1': '3-03-1', '3-3-2': '3-04-1',
  '3-4-1': '3-05-1', '3-5-1': '3-06-1',
  '4-1-1': '4-01-1', '4-2-1': '4-02-1', '4-3-1': '4-03-1', '4-4-1': '4-04-1',
  '4-5-1': '4-05-1', '4-6-1': '4-06-1', '4-7-1': '4-07-1',
  '5-1-1': '5-01-1', '5-2-1': '5-02-1', '5-3-1': '5-03-1', '5-4-1': '5-04-1',
};

// Build flat slides array from courses
const slides = [];
let globalIndex = 0;

courses.phases.forEach((phase) => {
  const phaseName = `Phase ${phase.order}: ${phase.name}`;
  phase.courses.forEach((course) => {
    course.lessons.forEach((lesson) => {
      const scriptKey = LESSON_TO_SCRIPT[lesson.id];
      const narration = scriptKey && scripts[scriptKey]?.slides?.[0]?.narration || '';
      const outlines = lesson.slideOutline || [];
      const slideCount = lesson.slideCount || 1;

      if (outlines.length > 0) {
        outlines.forEach((outline, i) => {
          slides.push({
            index: globalIndex++,
            id: `${lesson.id}-${i + 1}`,
            phase: phaseName,
            course: course.title,
            lesson: lesson.title,
            slideNum: i + 1,
            title: outline,
            narration: i === 0 ? narration : '',
          });
        });
      } else {
        for (let i = 0; i < slideCount; i++) {
          const title = i === 0 ? lesson.title : `${lesson.title} – Slide ${i + 1}`;
          slides.push({
            index: globalIndex++,
            id: `${lesson.id}-${i + 1}`,
            phase: phaseName,
            course: course.title,
            lesson: lesson.title,
            slideNum: i + 1,
            title,
            narration: i === 0 ? narration : '',
          });
        }
      }
    });
  });
});

// Generate HTML
const slidesJson = JSON.stringify(slides).replace(/</g, '\\u003c').replace(/>/g, '\\u003e');
const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>28-Course Slide Review | GovCon Giants Action Plan</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: #0f172a;
      color: #f8fafc;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    header {
      background: #1e293b;
      padding: 1rem 1.5rem;
      border-bottom: 1px solid #334155;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
    }
    header h1 {
      font-size: 1.25rem;
      font-weight: 700;
    }
    header .logo { color: #22c55e; }
    .nav-buttons {
      display: flex;
      gap: 0.5rem;
      align-items: center;
    }
    .nav-buttons button {
      padding: 0.5rem 1rem;
      background: #334155;
      border: 1px solid #475569;
      color: #f8fafc;
      border-radius: 0.5rem;
      cursor: pointer;
      font-size: 0.875rem;
      font-weight: 500;
    }
    .nav-buttons button:hover { background: #475569; }
    .nav-buttons button.primary {
      background: #22c55e;
      color: #0f172a;
      border-color: #22c55e;
    }
    .nav-buttons button.primary:hover { background: #16a34a; }
    .slide-indicator {
      font-size: 0.875rem;
      color: #94a3b8;
      min-width: 100px;
      text-align: center;
    }
    .main {
      display: flex;
      flex: 1;
      overflow: hidden;
    }
    .sidebar {
      width: 320px;
      flex-shrink: 0;
      background: #1e293b;
      border-right: 1px solid #334155;
      overflow-y: auto;
      padding: 1rem 0;
    }
    .sidebar h2 {
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #64748b;
      padding: 0.5rem 1rem 0.25rem;
      margin-top: 0.5rem;
    }
    .sidebar h2:first-child { margin-top: 0; }
    .sidebar h3 {
      font-size: 0.8rem;
      font-weight: 600;
      color: #94a3b8;
      padding: 0.35rem 1rem 0.15rem;
    }
    .slide-link {
      display: block;
      padding: 0.4rem 1rem 0.4rem 1.5rem;
      color: #94a3b8;
      text-decoration: none;
      font-size: 0.8rem;
      border-left: 3px solid transparent;
      transition: all 0.15s;
      line-height: 1.3;
    }
    .slide-link:hover {
      color: #f8fafc;
      background: #334155;
    }
    .slide-link.active {
      color: #22c55e;
      background: #22c55e15;
      border-left-color: #22c55e;
    }
    .slide-viewer {
      flex: 1;
      overflow: auto;
      padding: 2rem;
      display: flex;
      align-items: flex-start;
      justify-content: center;
    }
    .slide-frame {
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      border: 1px solid #334155;
      border-radius: 1rem;
      box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
      overflow: hidden;
      width: 100%;
      max-width: 960px;
      aspect-ratio: 16/9;
    }
    .slide-frame iframe {
      width: 100%;
      height: 100%;
      border: none;
    }
    @media (max-width: 900px) {
      .main { flex-direction: column; }
      .sidebar { width: 100%; max-height: 220px; }
    }
  </style>
</head>
<body>
  <header>
    <h1>28-Course Slide Review · <span class="logo">GovCon Giants</span> Action Plan</h1>
    <div class="nav-buttons">
      <button type="button" id="btn-prev" class="primary">← Previous</button>
      <span class="slide-indicator" id="slide-indicator">1 of ${slides.length}</span>
      <button type="button" id="btn-next" class="primary">Next →</button>
    </div>
  </header>
  <div class="main">
    <nav class="sidebar" id="sidebar"></nav>
    <div class="slide-viewer">
      <div class="slide-frame">
        <iframe id="slide-iframe" title="Slide"></iframe>
      </div>
    </div>
  </div>
  <script>
    const SLIDES = ${slidesJson};

    function renderSlideHtml(slide) {
      const subtitle = slide.narration
        ? (slide.narration.length > 220 ? slide.narration.substring(0, 220) + '...' : slide.narration)
        : slide.lesson + (slide.slideNum > 1 ? ' – ' + slide.title : '');
      return '<!DOCTYPE html>\\
<html lang="en">\\
<head><meta charset="UTF-8"><meta name="viewport" content="width=1920, height=1080">\\
<title>' + escapeHtml(slide.title) + '</title>\\
<style>\\
*{margin:0;padding:0;box-sizing:border-box}\\
body{font-family:\\'Segoe UI\\',system-ui,sans-serif;width:1920px;height:1080px;background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:#f8fafc;display:flex;flex-direction:column;padding:80px}\\
.phase-badge{display:inline-block;background:#22c55e;color:#0f172a;padding:8px 20px;border-radius:8px;font-weight:700;font-size:12px;margin-bottom:24px;text-transform:uppercase;letter-spacing:1px}\\
.course-label{font-size:14px;color:#64748b;margin-bottom:8px}\\
.slide-title{font-size:48px;font-weight:700;line-height:1.2;margin-bottom:32px;max-width:1400px}\\
.slide-subtitle{font-size:28px;color:#94a3b8;line-height:1.5;max-width:1400px}\\
.footer{margin-top:auto;display:flex;justify-content:space-between;align-items:center;font-size:22px;color:#64748b}\\
.slide-id{font-weight:600;color:#22c55e}\\
.logo{font-size:26px;font-weight:700}.logo span{color:#22c55e}\\
</style>\\
</head>\\
<body>\\
<div class="phase-badge">' + escapeHtml(slide.phase) + '</div>\\
<div class="course-label">' + escapeHtml(slide.course) + ' · ' + escapeHtml(slide.lesson) + '</div>\\
<h1 class="slide-title">' + escapeHtml(slide.title) + '</h1>\\
<p class="slide-subtitle">' + escapeHtml(subtitle) + '</p>\\
<div class="footer">\\
<span class="slide-id">' + escapeHtml(slide.id) + '</span>\\
<span class="logo">GovCon<span>Giants</span></span>\\
</div>\\
</body>\\
</html>';
    }

    function escapeHtml(s) {
      if (!s) return '';
      const d = document.createElement('div');
      d.textContent = s;
      return d.innerHTML;
    }

    let currentIndex = 0;
    const iframe = document.getElementById('slide-iframe');
    const sidebar = document.getElementById('sidebar');
    const indicator = document.getElementById('slide-indicator');

    function showSlide(index) {
      currentIndex = Math.max(0, Math.min(index, SLIDES.length - 1));
      const slide = SLIDES[currentIndex];
      const doc = iframe.contentDocument || iframe.contentWindow.document;
      doc.open();
      doc.write(renderSlideHtml(slide));
      doc.close();
      indicator.textContent = (currentIndex + 1) + ' of ' + SLIDES.length;
      document.querySelectorAll('.slide-link').forEach((el) => {
        el.classList.toggle('active', parseInt(el.dataset.index, 10) === currentIndex);
      });
    }

    function buildSidebar() {
      let lastPhase = '', lastCourse = '';
      SLIDES.forEach((slide, i) => {
        if (slide.phase !== lastPhase) {
          lastPhase = slide.phase;
          const h2 = document.createElement('h2');
          h2.textContent = slide.phase;
          sidebar.appendChild(h2);
        }
        if (slide.course !== lastCourse) {
          lastCourse = slide.course;
          const h3 = document.createElement('h3');
          h3.textContent = slide.course;
          sidebar.appendChild(h3);
        }
        const a = document.createElement('a');
        a.href = '#';
        a.className = 'slide-link' + (i === 0 ? ' active' : '');
        a.dataset.index = i;
        a.textContent = slide.lesson + (slide.slideNum > 1 ? ' · ' + slide.slideNum + '. ' + slide.title : '');
        a.onclick = (e) => { e.preventDefault(); showSlide(i); };
        sidebar.appendChild(a);
      });
    }

    document.getElementById('btn-prev').onclick = () => showSlide(currentIndex - 1);
    document.getElementById('btn-next').onclick = () => showSlide(currentIndex + 1);

    buildSidebar();
    showSlide(0);
  </script>
</body>
</html>
`;

const outPath = path.join(ROOT, 'slides', 'review-dashboard-28.html');
fs.writeFileSync(outPath, html, 'utf8');
console.log(`Wrote ${outPath} (${slides.length} slides)`);
