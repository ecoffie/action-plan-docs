# Architectural Overview – GovCon Action Plan Course

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ACTION PLAN (Source of Truth)                         │
│                         Posted to GitHub                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  data/                    webinars/              assets/     The Vault /     │
│  ├─ courses-28.json       ├─ phase-1-01-*.md    ├─ guides/   ├─ Consultant/  │
│  ├─ course-curriculum     ├─ phase-1-02-*.md    ├─ checklists├─ SAM/         │
│  ├─ scripts/scripts.json  ├─ ... (30 files)     ├─ templates ├─ Proposal/    │
│  ├─ lesson-resources      └─ SERIES-OVERVIEW    └─ documents └─ ...          │
│  └─ lesson-handouts                                                            │
│                                                                               │
│  slides/                  handouts/              docs/                        │
│  ├─ slide-template.html   ├─ *.pdf, *.docx      ├─ COURSE-STRUCTURE-28       │
│  ├─ review-dashboard      └─ (resource files)   ├─ LESSON-REFERENCE-FILES    │
│  └─ generated/                                 ├─ AI_VIDEO_PRODUCTION_GUIDE │
│                                                └─ ARCHITECTURE-OVERVIEW     │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ import / sync
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     GOVCON FUNNELS (Delivery Platform)                       │
│                     Next.js website                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Free course / Action Plan course UI                                       │
│  • Lesson video player (Vimeo)                                               │
│  • Resources download per lesson                                             │
│  • Progress tracking (localStorage)                                          │
│  • Lead capture → GoHighLevel (CRM / Email)                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ leads
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GOHIGHLEVEL                                       │
│  • CRM                                                                       │
│  • Email sequences                                                           │
│  • Lead capture / forms                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Content Hierarchy

```
Phase (5)
  └── Course (28 total)
        └── Lesson (31 total)
              └── Slide (10–20 per course)
                    └── Narration (TTS script)
```

| Level  | Count | Example |
|--------|-------|---------|
| Phase  | 5     | Setup, Bidding, Business Development, Business Enhancement, Contract Management |
| Course | 28    | Choose Your Business Structure, Identify Your NAICS, Create SAM.gov Profile, … |
| Lesson | 31    | Supplier vs Consultant, DUNS and UEI, How to Identify NAICS, … |
| Slide  | ~350  | ~10–20 per course |

---

## Data Flow

| Step | Source | Output |
|------|--------|--------|
| Content creation | webinars/*.md, The Vault, assets | Presentation notes, slide outlines |
| Curriculum definition | courses-28.json | Course structure, lessons, resources |
| Scripts | data/scripts/scripts.json | TTS narration per lesson |
| Slide generation | scripts/generate-slides.js | HTML slides in slides/generated/ |
| AI video pipeline | Scripts + slides | 30 videos (TTS + AI avatar) |
| Platform | GovCon Funnels | Reads Action Plan data, serves course UI |

---

## Key Repositories / Folders

| Location | Role |
|----------|------|
| **Action Plan** | Single source of truth. Curriculum, webinars, scripts, handouts, slide templates. |
| **GovCon Funnels** | Website. Consumes Action Plan data. No course content defined here. |
| **GoHighLevel** | CRM and email. Receives leads from GovCon Funnels. |

---

## File Roles

| File / Folder | Purpose |
|---------------|---------|
| `data/courses-28.json` | 28-course structure: phases, courses, lessons, slide outlines, resources |
| `data/course-curriculum.json` | Legacy 30-lesson curriculum (for compatibility) |
| `data/scripts/scripts.json` | Narration text per lesson (TTS / AI avatar) |
| `data/lesson-resources.json` | Download links per lesson |
| `data/lesson-handouts.json` | Progress tracker checklists per lesson |
| `webinars/phase-*-*.md` | Full webinar outlines and presentation notes |
| `handouts/` | Resource files (PDF, DOCX, etc.) for lessons |
| `slides/review-dashboard.html` | Slide review UI |
| `docs/COURSE-STRUCTURE-28.md` | Human-readable 28-course mapping |
| `docs/LESSON-REFERENCE-FILES.md` | Vault → lesson mapping and narration prompts |

---

## Video Pipeline

```
scripts.json (narration)
        +
courses-28.json (slide outlines)
        │
        ▼
generate-slides.js → HTML slides
        │
        ▼
TTS (ElevenLabs, etc.) → Audio
        │
        ▼
AI Avatar (HeyGen, Synthesia) → Video
        │
        ▼
Vimeo → videoId in curriculum
```

---

## Summary

- **Action Plan** holds all course content and structure.
- **GovCon Funnels** is the delivery layer that imports and displays it.
- **GoHighLevel** handles leads and email.
- Content hierarchy: Phase → Course → Lesson → Slide.
- Videos are produced from scripts and slides via TTS and AI avatar tools.
