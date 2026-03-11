#!/usr/bin/env python3
"""Builds review-dashboard-28.html from courses-28.json and scripts.json."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
courses = json.loads((ROOT / "data" / "courses-28.json").read_text())
scripts_data = json.loads((ROOT / "data" / "scripts" / "scripts.json").read_text())
scripts = scripts_data.get("scripts", {})

LESSON_TO_SCRIPT = {
    "1-1-1": "1-01-1", "1-1-2": "1-02-1", "1-1-3": "1-03-1", "1-2-1": "1-04-1",
    "1-3-1": "1-05-1", "1-4-1": "1-06-1", "1-5-1": "1-07-1", "1-6-1": "1-08-1",
    "2-1-1": "2-01-1", "2-2-1": "2-02-1", "2-3-1": "2-03-1", "2-4-1": "2-04-1",
    "2-5-1": "2-04-1", "2-6-1": "2-05-1",
    "3-1-1": "3-01-1", "3-2-1": "3-02-1", "3-3-1": "3-03-1", "3-3-2": "3-04-1",
    "3-4-1": "3-05-1", "3-5-1": "3-06-1",
    "4-1-1": "4-01-1", "4-2-1": "4-02-1", "4-3-1": "4-03-1", "4-4-1": "4-04-1",
    "4-5-1": "4-05-1", "4-6-1": "4-06-1", "4-7-1": "4-07-1",
    "5-1-1": "5-01-1", "5-2-1": "5-02-1", "5-3-1": "5-03-1", "5-4-1": "5-04-1",
}

slides = []
idx = 0
for phase in courses["phases"]:
    phase_name = f"Phase {phase['order']}: {phase['name']}"
    for course in phase["courses"]:
        for lesson in course["lessons"]:
            script_key = LESSON_TO_SCRIPT.get(lesson["id"])
            narration = ""
            if script_key and script_key in scripts:
                s = scripts[script_key].get("slides", [{}])
                if s:
                    narration = s[0].get("narration", "")
            outlines = lesson.get("slideOutline", [])
            slide_count = lesson.get("slideCount", 1)
            if outlines:
                for i, outline in enumerate(outlines):
                    slides.append({
                        "index": idx, "id": f"{lesson['id']}-{i+1}",
                        "phase": phase_name, "course": course["title"], "lesson": lesson["title"],
                        "slideNum": i + 1, "title": outline,
                        "narration": narration if i == 0 else "",
                    })
                    idx += 1
            else:
                # No slideOutline: create 1 slide only (avoids repetitive placeholder slides)
                slides.append({
                    "index": idx, "id": f"{lesson['id']}-1",
                    "phase": phase_name, "course": course["title"], "lesson": lesson["title"],
                    "slideNum": 1, "title": lesson["title"],
                    "narration": narration,
                })
                idx += 1

slides_json = json.dumps(slides).replace("<", "\\u003c").replace(">", "\\u003e")

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>28-Course Slide Review | GovCon Giants Action Plan</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #f8fafc; min-height: 100vh; display: flex; flex-direction: column; }}
    header {{ background: #1e293b; padding: 1rem 1.5rem; border-bottom: 1px solid #334155; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; }}
    header h1 {{ font-size: 1.25rem; font-weight: 700; }}
    header .logo {{ color: #22c55e; }}
    .nav-buttons {{ display: flex; gap: 0.5rem; align-items: center; }}
    .nav-buttons button {{ padding: 0.5rem 1rem; background: #334155; border: 1px solid #475569; color: #f8fafc; border-radius: 0.5rem; cursor: pointer; font-size: 0.875rem; font-weight: 500; }}
    .nav-buttons button:hover {{ background: #475569; }}
    .nav-buttons button.primary {{ background: #22c55e; color: #0f172a; border-color: #22c55e; }}
    .nav-buttons button.primary:hover {{ background: #16a34a; }}
    .slide-indicator {{ font-size: 0.875rem; color: #94a3b8; min-width: 100px; text-align: center; }}
    .main {{ display: flex; flex: 1; overflow: hidden; }}
    .sidebar {{ width: 320px; flex-shrink: 0; background: #1e293b; border-right: 1px solid #334155; overflow-y: auto; padding: 1rem 0; }}
    .sidebar h2 {{ position: sticky; top: 0; z-index: 2; background: #1e293b; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; padding: 0.5rem 1rem 0.25rem; margin-top: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
    .sidebar h2:first-child {{ margin-top: 0; }}
    .sidebar h3 {{ position: sticky; top: 1.6rem; z-index: 1; background: #1e293b; font-size: 0.8rem; font-weight: 600; color: #94a3b8; padding: 0.35rem 1rem 0.15rem; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
    .slide-link {{ display: block; padding: 0.4rem 1rem 0.4rem 1.5rem; color: #94a3b8; text-decoration: none; font-size: 0.8rem; border-left: 3px solid transparent; transition: all 0.15s; line-height: 1.3; }}
    .slide-link:hover {{ color: #f8fafc; background: #334155; }}
    .slide-link.active {{ color: #22c55e; background: #22c55e15; border-left-color: #22c55e; }}
    .slide-viewer {{ flex: 1; overflow: auto; padding: 2rem; display: flex; align-items: flex-start; justify-content: center; }}
    .slide-frame {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border: 1px solid #334155; border-radius: 1rem; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); overflow: hidden; width: 100%; max-width: 960px; aspect-ratio: 16/9; min-height: 400px; }}
    .slide-frame iframe {{ width: 100%; height: 100%; border: none; }}
    @media (max-width: 900px) {{ .main {{ flex-direction: column; }} .sidebar {{ width: 100%; max-height: 220px; }} }}
  </style>
</head>
<body>
  <header>
    <h1>28-Course Slide Review · <span class="logo">GovCon Giants</span> Action Plan</h1>
    <div class="nav-buttons">
      <button type="button" id="btn-prev" class="primary">← Previous</button>
      <span class="slide-indicator" id="slide-indicator">1 of {len(slides)}</span>
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
    const SLIDES = {slides_json};

    let currentIndex = 0;
    const iframe = document.getElementById('slide-iframe');
    const sidebar = document.getElementById('sidebar');
    const indicator = document.getElementById('slide-indicator');

    function showSlide(index) {{
      currentIndex = Math.max(0, Math.min(index, SLIDES.length - 1));
      const slideNum = (currentIndex + 1).toString().padStart(3, '0');
      iframe.src = 'individual/slide-' + slideNum + '.html';
      indicator.textContent = (currentIndex + 1) + ' of ' + SLIDES.length;
      document.querySelectorAll('.slide-link').forEach((el) => {{
        el.classList.toggle('active', parseInt(el.dataset.index, 10) === currentIndex);
      }});
    }}

    function buildSidebar() {{
      let lastPhase = '', lastCourse = '';
      SLIDES.forEach((slide, i) => {{
        if (slide.phase !== lastPhase) {{
          lastPhase = slide.phase;
          const h2 = document.createElement('h2');
          h2.textContent = slide.phase;
          sidebar.appendChild(h2);
        }}
        if (slide.course !== lastCourse) {{
          lastCourse = slide.course;
          const h3 = document.createElement('h3');
          h3.textContent = slide.course;
          sidebar.appendChild(h3);
        }}
        const a = document.createElement('a');
        a.href = '#';
        a.className = 'slide-link' + (i === 0 ? ' active' : '');
        a.dataset.index = i;
        a.textContent = slide.lesson + (slide.slideNum > 1 ? ' · ' + slide.slideNum + '. ' + slide.title : '');
        a.onclick = (e) => {{ e.preventDefault(); showSlide(i); }};
        sidebar.appendChild(a);
      }});
    }}

    document.getElementById('btn-prev').onclick = () => showSlide(currentIndex - 1);
    document.getElementById('btn-next').onclick = () => showSlide(currentIndex + 1);

    buildSidebar();
    showSlide(0);
  </script>
</body>
</html>
'''

out_path = ROOT / "slides" / "review-dashboard-28.html"
out_path.write_text(html, encoding="utf-8")
print(f"Wrote {out_path} ({len(slides)} slides)")
