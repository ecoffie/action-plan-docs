# How We Work – GovCon Action Plan

A living doc of preferences, conventions, and decisions so the AI (and you) remembers what works.

**Update this file as you go.** Add what you like, don't like, and how you want things done.

---

## Slide Format & Design

### What I like
- **War Room Boot Camp format** – Use the format from the Feb 7 War Room (veteran-vosb-sdvosb-presentation-v2.html) and January Bootcamp
- **Centered text** – Content centered both vertically (top-to-bottom) and horizontally (left-to-right), not stacked at the top
- **Mix of images and text** – Slides should include images where relevant, not just text
- **Consulting-style layout** – Title bar at top, visual zone in center, footer at bottom (reference: Bootcamp/presentations/)
- **Inter font** – From Google Fonts
- **White slides** with shadow, lime green (#8BC34A) accents, gray (#666) for secondary text
- **960×540** slide dimensions

### What I don't like
- Text crammed at the top of slides
- Slides that are only text with no images
- Blank or repetitive placeholder slides (same content repeated)
- Old dark theme (slate/teal background) – prefer white/light

---

## Slide Structure

- **28 courses** across 5 phases (Phase → Course → Lesson → Slide)
- **Slide outlines** come from `webinars/*.md` (extract from `## Slide Outline` section)
- **Individual HTML files** – One file per slide in `slides/individual/slide-001.html` through `slide-315.html`
- **Images** – Map in `scripts/build-individual-slides.py` via `SLIDE_IMAGES` dict. Add more mappings as you add assets.
- **Resources** – Action Plan repo is source of truth. Vault and assets hold handouts, guides, images.

---

## Build Commands

```bash
# Extract slide outlines from webinars → courses-28.json
python3 scripts/extract-webinar-slides.py

# Build individual slide HTML files
python3 scripts/build-individual-slides.py

# Build review dashboard (sidebar + iframe viewer)
python3 scripts/build-review-dashboard-28.py
```

---

## Key Paths

| What | Path |
|------|------|
| Course structure | `data/courses-28.json` |
| Webinar content | `webinars/phase-*.md` |
| Narration scripts | `data/scripts/scripts.json` |
| Individual slides | `slides/individual/` |
| Review dashboard | `slides/review-dashboard-28.html` |
| Assets / images | `assets/`, `assets/veteran-v2-assets/` |
| Reference formats | `Bootcamp/presentations/` (War Room, January Bootcamp) |

---

## Browser

- Prefer **Google Chrome** over Safari when opening HTML files.

---

## Add your own

- What else do you like or dislike?
- Conventions for naming, file organization?
- Things the AI often gets wrong?
