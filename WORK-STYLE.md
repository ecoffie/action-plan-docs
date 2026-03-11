# Work Style & Preferences – GovCon Action Plan

**Like CLAUDE.md** – A living document for you to update and for AI assistants to reference. Capture what you like, what you don't, how you work, and project conventions. Keep it updated so context persists across sessions.

**How to use:** Add entries to "What I Don't Like" or new sections when preferences change. Append dated notes under Updates. Reference this file at the start of sessions so the AI remembers your style.

---

## Project Context

- **Action Plan** = single source of truth for GovCon Giants course content
- **28-course structure:** Phase → Course → Lesson → Slide
- **GovCon Funnels** (Next.js) delivers the content; pulls from Action Plan
- **The Vault** = source files (PDFs, DOCX, etc.) for handouts and reference

---

## Slide Design Preferences

### Format (War Room / January Bootcamp style)
- **Centered layout** – Text centered both vertically and horizontally (middle of slide, not top-aligned)
- **Title bar** at top (dark bar with Phase · Course)
- **Visual zone** in middle – main content centered with `align-items: center`, `justify-content: center`, `text-align: center`
- **Footer** at bottom – GovconGiants.org link
- **Mix in images** – Not just text; use images on slides where relevant
- **White slides** with shadow, Inter font, lime green (#8BC34A) accents
- **960×540** slide dimensions (landscape)

### Reference presentations
- `Bootcamp/presentations/veteran-vosb-sdvosb-presentation-v2.html` (War Room Feb 7)
- `Bootcamp/presentations/veteran-vosb-sdvosb-presentation.html` (consulting format)
- `Bootcamp/presentations/january-2026-bootcamp-slides.html`

---

## What I Don't Like

- Text stacked at top of slides (prefer centered)
- Slides that repeat the same content (no placeholder duplicates)
- Blank or generic slides with no unique content
- Courses with only one slide

---

## Key Paths

| Item | Path |
|------|------|
| Course structure | `data/courses-28.json` |
| Scripts/narration | `data/scripts/scripts.json` |
| Webinars (slide outlines) | `webinars/phase-*.md` |
| Individual slides | `slides/individual/slide-001.html` … |
| Review dashboard | `slides/review-dashboard-28.html` |
| Build individual slides | `python3 scripts/build-individual-slides.py` |
| Build dashboard | `python3 scripts/build-review-dashboard-28.py` |
| Extract webinar slides | `python3 scripts/extract-webinar-slides.py` |
| Capture web images | `python3 scripts/capture-slide-image.py` (see docs/SLIDE-IMAGE-CAPTURE.md) |
| Assets / images | `assets/`, `assets/images/`, `assets/veteran-v2-assets/` |

---

## How to Add Visuals to Slides

1. **Put your image** in `assets/images/manual/` (or `assets/images/`, `assets/veteran-v2-assets/`).
2. **Edit** `scripts/build-individual-slides.py` and add an entry to `SLIDE_IMAGES`:

   ```python
   SLIDE_IMAGES: Dict[Tuple[str, str], str] = {
       ("1-1-1", "comparison table"): "../../assets/images/Copy of corporation matrix.jpg",
       ("4-1-1", "title"): "../../assets/veteran-v2-assets/sba-datahub-sdvosb-chart.png",
       # Add more: (lesson_id, slide_title_lower) -> path relative to slides/individual/
   }
   ```

3. **Key format:** `(lesson_id, slide_title_lower)`
   - `lesson_id` = e.g. `"1-1-1"`, `"4-2-1"` (from `courses-28.json`)
   - `slide_title_lower` = exact slide title from `slideOutline`, lowercased (e.g. `"comparison table"`, `"title slide"`)

4. **Path format:** Relative to `slides/individual/`, so use `../../assets/...` to reach the assets folder.

5. **Rebuild:** Run `python3 scripts/build-individual-slides.py` then `python3 scripts/build-review-dashboard-28.py` to regenerate.

**Capture from web:** Use `scripts/capture-slide-image.py` to screenshot URLs (SAM.gov, DUNS/UEI pages, etc.) or download images. See `docs/SLIDE-IMAGE-CAPTURE.md` for full guide. Optional: add **universal-screenshot-mcp** (npx) to Cursor MCP for AI-assisted capture.

---

## Browser

- Prefer **Google Chrome** (not Safari) when opening HTML in browser

---

## Updates

*Add dated entries below as preferences change.*

- 2026-02-08: War Room format, centered layout, image support. Prefer Chrome. No repetitive/blank slides.
