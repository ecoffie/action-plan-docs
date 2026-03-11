#!/usr/bin/env python3
"""
Generate one HTML file per slide for the 28-course structure.
Output: slides/individual/slide-001.html through slide-NNN.html
Each slide has Prev/Next links to navigate sequentially.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Tuple

ROOT = Path(__file__).resolve().parent.parent
COURSES_PATH = ROOT / "data" / "courses-28.json"
SCRIPTS_PATH = ROOT / "data" / "scripts" / "scripts.json"
OUT_DIR = ROOT / "slides" / "individual"

LESSON_TO_SCRIPT = {
    # Phase 1: Setup
    "1-1-1": "1-01-1", "1-1-2": "1-02-1", "1-1-3": "1-03-1",
    "1-2-1": "1-04-1", "1-2-2": "1-04-1", "1-2-3": "1-04-1",
    "1-3-1": "1-05-1", "1-3-2": "1-05-1", "1-3-3": "1-05-1",
    "1-4-1": "1-06-1", "1-4-2": "1-06-1",
    "1-5-1": "1-07-1", "1-5-2": "1-07-1",
    "1-6-1": "1-08-1", "1-6-2": "1-08-1", "1-6-3": "1-08-1",
    # Phase 2: Bidding
    "2-1-1": "2-01-1", "2-1-2": "2-01-1", "2-1-3": "2-01-1",
    "2-2-1": "2-02-1", "2-2-2": "2-02-1", "2-2-3": "2-02-1",
    "2-3-1": "2-03-1", "2-3-2": "2-03-1",
    "2-4-1": "2-04-1", "2-4-2": "2-04-1", "2-4-3": "2-04-1",
    "2-5-1": "2-04-1", "2-5-2": "2-04-1", "2-5-3": "2-04-1",
    "2-6-1": "2-05-1", "2-6-2": "2-05-1",
    # Phase 3: Business Development
    "3-1-1": "3-01-1", "3-1-2": "3-01-1", "3-1-3": "3-01-1",
    "3-2-1": "3-02-1", "3-2-2": "3-02-1", "3-2-3": "3-02-1",
    "3-3-1": "3-03-1", "3-3-2": "3-04-1",
    "3-4-1": "3-05-1", "3-4-2": "3-05-1",
    "3-5-1": "3-06-1", "3-5-2": "3-06-1",
    # Phase 4: Business Enhancement
    "4-1-1": "4-01-1", "4-1-2": "4-01-1", "4-1-3": "4-01-1",
    "4-2-1": "4-02-1", "4-2-2": "4-02-1", "4-2-3": "4-02-1",
    "4-3-1": "4-03-1", "4-3-2": "4-03-1",
    "4-4-1": "4-04-1", "4-4-2": "4-04-1",
    "4-5-1": "4-05-1", "4-5-2": "4-05-1",
    "4-6-1": "4-06-1", "4-6-2": "4-06-1",
    "4-7-1": "4-07-1", "4-7-2": "4-07-1",
    "4-8-1": "4-01-1", "4-8-2": "4-01-1", "4-8-3": "4-02-1",
    # Phase 5: Contract Management
    "5-1-1": "5-01-1", "5-1-2": "5-01-1", "5-1-3": "5-01-1",
    "5-2-1": "5-02-1", "5-2-2": "5-02-1", "5-2-3": "5-02-1",
    "5-3-1": "5-03-1", "5-3-2": "5-03-1", "5-3-3": "5-03-1",
    "5-4-1": "5-04-1", "5-4-2": "5-04-1",
}


def esc(s: str) -> str:
    if not s:
        return ""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


# Map (lesson_id, slide_title_lower) -> image path relative to slide
SLIDE_IMAGES: Dict[Tuple[str, str], str] = {
    # Original / veteran assets
    ("1-1-1", "comparison table"): "../../assets/images/Copy of corporation matrix.jpg",
    ("4-1-1", "title slide"): "../../assets/veteran-v2-assets/sba-datahub-sdvosb-chart.png",
    ("4-1-1", "wosb / edwosb overview"): "../../assets/veteran-v2-assets/sba-datahub-sdvosb-table.png",
    ("4-2-1", "title slide"): "../../assets/veteran-v2-assets/sba-datahub-sdvosb-chart.png",
    # Phase 1 - Setup
    ("1-1-1", "why business structure matters"): "../../assets/images/p1-c1-business-structure.png",
    ("1-1-2", "introduction"): "../../assets/images/p1-c1-sba-structures.png",
    ("1-2-2", "official naics website walkthrough"): "../../assets/images/p1-c2-naics-website.png",
    ("1-2-2", "sam.gov naics lookup"): "../../assets/images/p1-c2-sam-lookup.png",
    ("1-3-1", "what is sam.gov?"): "../../assets/images/p1-c3-sam-homepage.png",
    ("1-3-2", "entity registration overview"): "../../assets/images/p1-c3-entity-registration.png",
    ("1-4-1", "what is dsbs (dynamic small business search)?"): "../../assets/images/p1-c4-dsbs-homepage.png",
    ("1-4-2", "step-by-step registration process"): "../../assets/images/p1-c4-dsbs-search.png",
    ("1-5-1", "what are apex accelerators (formerly ptacs)?"): "../../assets/images/p1-c5-aptac-sba.png",
    ("1-5-2", "finding your local apex accelerator"): "../../assets/images/p1-c5-aptac-locator-sba.png",
    ("1-6-1", "what is a capability statement?"): "../../assets/images/p1-c6-capability-statement.png",
    ("1-6-1", "certifications and set-asides"): "../../assets/images/p1-c6-sba-certifications.png",
    # Phase 2 - Bidding
    ("2-1-1", "sam.gov contract opportunities overview"): "../../assets/images/p2-c1-contract-opportunities.png",
    ("2-1-1", "saved searches and email alerts"): "../../assets/images/p2-c1-saved-searches.png",
    ("2-2-2", "team formation structures"): "../../assets/images/p2-c2-teaming.png",
    ("2-2-3", "what is a teaming agreement?"): "../../assets/images/p2-c2-teaming-agreements.png",
    ("2-3-1", "why credit matters in government contracting"): "../../assets/images/p2-c3-credit.png",
    ("2-3-2", "what is bonding and why it matters"): "../../assets/images/p2-c3-bonding.png",
    ("2-4-1", "rfp structure overview"): "../../assets/images/p2-c4-opportunity-types.png",
    ("2-4-2", "rfp structure: sections a through m"): "../../assets/images/p2-c4-solicitations.png",
    ("2-5-3", "electronic submission requirements"): "../../assets/images/p2-c5-submission.png",
    ("2-5-1", "writing to evaluation criteria"): "../../assets/images/p2-c5-proposal.png",
    ("2-6-1", "finding award results on sam.gov"): "../../assets/images/p2-c6-fpds.png",
    ("2-6-2", "documenting debrief feedback"): "../../assets/images/p2-c6-usaspending.png",
    # Phase 3 - Business Development
    ("3-1-1", "sam.gov contract data (formerly fpds, now integrated)"): "../../assets/images/p3-c1-fpds.png",
    ("3-1-1", "building your target market list (tml)"): "../../assets/images/p3-c1-usaspending.png",
    ("3-2-1", "osdbu/oss offices"): "../../assets/images/p3-c2-osdbu.png",
    ("3-2-3", "what is a capability briefing?"): "../../assets/images/p3-c2-capabilities.png",
    ("3-3-1", "types of industry events"): "../../assets/images/p3-c3-industry-events.png",
    ("3-3-2", "types of site visits (facility tours, pre-award)"): "../../assets/images/p3-c3-site-visits.png",
    ("3-4-1", "what are prime contractor vendor portals?"): "../../assets/images/p3-c4-vendor-portals.png",
    ("3-4-2", "what are supplier diversity programs?"): "../../assets/images/p3-c4-supplier-diversity.png",
    ("3-5-1", "setting up sam.gov contract data monitoring"): "../../assets/images/p3-c5-fpds-monitoring.png",
    ("3-5-2", "subnet for finding sub opportunities"): "../../assets/images/p3-c5-sub-opportunities.png",
    # Phase 4 - Business Enhancement
    ("4-1-1", "why certifications matter"): "../../assets/images/p4-c1-cert-options.png",
    ("4-1-2", "wosb eligibility requirements"): "../../assets/images/p4-c1-eligibility.png",
    ("4-2-1", "sba business development program overview"): "../../assets/images/p4-c2-8a-overview.png",
    ("4-2-3", "application documentation checklist"): "../../assets/images/p4-c2-8a-application.png",
    ("4-3-1", "benefits: knowledge transfer"): "../../assets/images/p4-c3-mentor-protege.png",
    ("4-3-2", "what is a joint venture?"): "../../assets/images/p4-c3-joint-ventures.png",
    ("4-4-1", "what is self-performance?"): "../../assets/images/p4-c4-self-performance.png",
    ("4-4-2", "creating past performance narratives"): "../../assets/images/p4-c4-past-performance.png",
    ("4-5-1", "performance evaluation criteria"): "../../assets/images/p4-c5-evaluate-partners.png",
    ("4-5-2", "ideal partner characteristics"): "../../assets/images/p4-c5-strategic-partnerships.png",
    ("4-6-1", "mid-size vs. large prime mentors"): "../../assets/images/p4-c6-mid-size.png",
    ("4-6-1", "flexibility in teaming"): "../../assets/images/p4-c6-teaming.png",
    ("4-7-1", "speaking as thought leadership"): "../../assets/images/p4-c7-speaking.png",
    ("4-7-2", "choosing your speaking topic"): "../../assets/images/p4-c7-topic-selection.png",
    # Phase 5 - Contract Management
    ("5-1-1", "what is piee?"): "../../assets/images/p5-c1-piee.png",
    ("5-1-2", "what is wawf (wide area workflow)?"): "../../assets/images/p5-c1-wawf.png",
    ("5-2-1", "what are flow-down clauses?"): "../../assets/images/p5-c2-flowdown.png",
    ("5-2-2", "prime contractor responsibility"): "../../assets/images/p5-c2-prime-responsibility.png",
    ("5-3-1", "understanding your contract terms"): "../../assets/images/p5-c3-compliance.png",
    ("5-3-1", "statement of work (sow) essentials"): "../../assets/images/p5-c3-contract-terms.png",
    ("5-4-1", "establishing communication early"): "../../assets/images/p5-c4-communication.png",
    ("5-4-1", "preferred communication methods"): "../../assets/images/p5-c4-establishing.png",
}


def slide_html(slide: dict, prev_num: Optional[int], next_num: Optional[int], total: int, image_path: Optional[str] = None) -> str:
    subtitle = slide.get("narration", "")
    if not subtitle:
        subtitle = slide["lesson"] + (f" – {slide['title']}" if slide["slideNum"] > 1 else "")
    elif len(subtitle) > 280:
        subtitle = subtitle[:280] + "..."
    num = slide["index"] + 1
    prev_link = f'<a href="slide-{prev_num:03d}.html">← Previous</a>' if prev_num else '<span class="disabled">← Previous</span>'
    next_link = f'<a href="slide-{next_num:03d}.html">Next →</a>' if next_num else '<span class="disabled">Next →</span>'

    # Image block: show when we have an image, otherwise empty
    img_block = ''
    if image_path:
        img_block = f'<div class="slide-image"><img src="{esc(image_path)}" alt=""></div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(slide['title'])} · {esc(slide['lesson'])}</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{ --green: #8BC34A; --green-dark: #689F38; --black: #1a1a1a; --gray: #666; }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{ overflow: hidden; width: 100%; height: 100%; font-family: 'Inter', -apple-system, sans-serif; background: #e5e7eb; }}
    .slide {{ width: 960px; min-height: 540px; background: white; margin: 20px auto; box-shadow: 0 10px 40px rgba(0,0,0,0.15); position: relative; display: flex; flex-direction: column; padding: 0; }}
    .title-bar {{ background: var(--black); color: white; padding: 12px 40px; font-size: 0.9rem; font-weight: 600; flex-shrink: 0; text-align: center; }}
    .visual-zone {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 32px 50px; min-height: 360px; }}
    .visual-zone h1 {{ font-size: 2.2rem; font-weight: 800; line-height: 1.2; margin-bottom: 20px; color: var(--black); max-width: 800px; border: none; padding: 0; }}
    .visual-zone .subtitle {{ font-size: 1.25rem; line-height: 1.5; color: var(--gray); max-width: 720px; }}
    .slide-image {{ margin: 20px 0; max-width: 100%; max-height: 220px; }}
    .slide-image img {{ max-width: 100%; max-height: 220px; width: auto; height: auto; object-fit: contain; border-radius: 8px; border: 1px solid #e5e7eb; }}
    .slide-footer {{ padding: 12px 40px; font-size: 0.9rem; color: var(--gray); border-top: 1px solid #eee; flex-shrink: 0; text-align: center; }}
    .slide-footer a {{ color: var(--green-dark); text-decoration: none; }}
    .slide-num {{ position: absolute; bottom: 12px; right: 25px; font-size: 0.9rem; color: #999; }}
    .nav-bar {{ position: fixed; bottom: 0; left: 0; right: 0; background: #1a1a1a; color: white; padding: 12px 24px; display: flex; align-items: center; justify-content: center; gap: 24px; z-index: 10; font-size: 1rem; }}
    .nav-bar a {{ color: var(--green); text-decoration: none; font-weight: 600; }}
    .nav-bar a:hover {{ text-decoration: underline; }}
    .nav-bar .disabled {{ color: #888; cursor: not-allowed; }}
    .slide-wrap {{ display: flex; justify-content: center; align-items: flex-start; min-height: 100vh; padding-bottom: 60px; }}
  </style>
</head>
<body>
  <div class="slide-wrap">
    <div class="slide">
      <div class="title-bar">{esc(slide['phase'])} · {esc(slide['course'])}</div>
      <div class="visual-zone">
        <h1>{esc(slide['title'])}</h1>
        {img_block}
        <p class="subtitle">{esc(subtitle)}</p>
      </div>
      <div class="slide-footer"><a href="https://govcongiants.org">GovconGiants.org</a></div>
      <span class="slide-num">{num}</span>
    </div>
  </div>
  <nav class="nav-bar">
    {prev_link}
    <span>Slide {num} of {total}</span>
    {next_link}
  </nav>
</body>
</html>
"""


def main():
    courses = json.loads(COURSES_PATH.read_text(encoding="utf-8"))
    scripts_data = json.loads(SCRIPTS_PATH.read_text(encoding="utf-8"))
    scripts = scripts_data.get("scripts", {})

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
                            "slideNum": i + 1, "title": outline, "narration": narration if i == 0 else "",
                        })
                        idx += 1
                else:
                    slides.append({
                        "index": idx, "id": f"{lesson['id']}-1",
                        "phase": phase_name, "course": course["title"], "lesson": lesson["title"],
                        "slideNum": 1, "title": lesson["title"], "narration": narration,
                    })
                    idx += 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = len(slides)
    for i, slide in enumerate(slides):
        prev_num = (i) if i > 0 else None  # 1-based: slide 2 links prev to 1
        next_num = (i + 2) if i < total - 1 else None  # 1-based: slide 1 links next to 2
        img_key = (slide["id"].rsplit("-", 1)[0], slide["title"].lower())
        image_path = SLIDE_IMAGES.get(img_key)
        html = slide_html(slide, prev_num, next_num, total, image_path)
        path = OUT_DIR / f"slide-{i+1:03d}.html"
        path.write_text(html, encoding="utf-8")

    # Create index.html to start at slide 1
    index_content = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta http-equiv="refresh" content="0;url=slide-001.html"><title>Redirecting...</title></head>
<body>Redirecting to slide 1... <a href="slide-001.html">Click here</a> if not redirected.</body></html>
"""
    (OUT_DIR / "index.html").write_text(index_content, encoding="utf-8")
    print(f"Wrote {total} individual slide HTML files to {OUT_DIR}/")


if __name__ == "__main__":
    main()
