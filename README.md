# Government Contracting Action Plan

Action Plan documents and course content for the Government Contracting training series. This repo is the single source of truth for curriculum, lessons, resources, handouts, and scripts.

## Structure

| Folder | Purpose |
|--------|---------|
| **data/** | Curriculum, scripts, lesson resources, progress trackers |
| **webinars/** | 30 webinar outlines (markdown) |
| **slides/** | Slide template + generated HTML slides for AI video |
| **handouts/** | Downloadable resource files per lesson |
| **scripts/** | `generate-slides.js` – builds slides from curriculum + scripts |
| **docs/** | Guides, reference files, AI video production |
| **assets/** | Templates, checklists, guides from The Vault |
| **courses/** | Legacy course content |
| **The Vault /** | Original source materials |

## Quick Start

**Generate slides for AI video production:**

```bash
node scripts/generate-slides.js
```

Output: `slides/generated/` – HTML files + manifest.json

## Key Files

- `data/course-curriculum.json` – 30 lessons across 5 phases  
- `data/scripts/scripts.json` – TTS narration for each lesson  
- `data/lesson-resources.json` – Download links per lesson  
- `data/lesson-handouts.json` – Progress tracker checklists per lesson  

## Website

When ready to build the course website, import this data from the Action Plan repo. The website (GovCon Funnels) consumes this content—it does not define it.
