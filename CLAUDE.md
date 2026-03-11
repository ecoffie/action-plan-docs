# CLAUDE.md – GovCon Action Plan

## Project Overview

**Action Plan** is the single source of truth for GovCon Giants course content. It feeds into **GovCon Funnels** (a Next.js app) which delivers the content to users.

- **28-course structure:** Phase → Course → Lesson → Slide
- **The Vault** = source files (PDFs, DOCX, etc.) for handouts and reference
- **Owner:** Eric Coffie + Branden

## Key Paths

| Item | Path |
|------|------|
| Course structure | `data/courses-28.json` |
| Scripts/narration | `data/scripts/scripts.json` |
| Webinars (slide outlines) | `webinars/phase-*.md` |
| Individual slides | `slides/individual/slide-001.html` … |
| Review dashboard | `slides/review-dashboard-28.html` |
| Assets / images | `assets/`, `assets/images/`, `assets/veteran-v2-assets/` |

## Build Commands

```bash
python3 scripts/build-individual-slides.py       # Build individual slides
python3 scripts/build-review-dashboard-28.py      # Build review dashboard
python3 scripts/extract-webinar-slides.py         # Extract webinar slides
python3 scripts/capture-slide-image.py            # Capture web images (see docs/SLIDE-IMAGE-CAPTURE.md)
```

## Slide Design Rules

- **Centered layout** — text centered vertically and horizontally (not top-aligned)
- **Title bar** at top (dark bar with Phase · Course)
- **Visual zone** in middle — main content centered
- **Footer** at bottom — GovconGiants.org link
- **Mix images in** — not just text slides
- **White slides** with shadow, Inter font, lime green (#8BC34A) accents
- **960×540** slide dimensions (landscape)
- Reference styles: `Bootcamp/presentations/veteran-vosb-sdvosb-presentation-v2.html` (War Room format)

## Adding Images to Slides

1. Place image in `assets/images/manual/` (or `assets/images/`, `assets/veteran-v2-assets/`)
2. Edit `scripts/build-individual-slides.py` — add entry to `SLIDE_IMAGES` dict
3. Key format: `(lesson_id, slide_title_lower)` → path relative to `slides/individual/`
4. Rebuild with the build commands above

## Don'ts

- No text stacked at top of slides (must be centered)
- No duplicate/repetitive slides with same content
- No blank or generic placeholder slides
- No courses with only one slide

## Workflow Preferences

- Use **Google Chrome** (not Safari) for opening HTML
- See `ERIC-BRANDEN-PROJECTS-TODO.md` for current task priorities
- See `WORK-STYLE.md` for detailed style preferences and update log

## Workflow Orchestration

### 1. Plan Node Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately — don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules that prevent the same mistake
- Ruthlessly iterate on lessons until mistake rate drops
- Review lessons at session start

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: implement the elegant solution
- Skip this for simple, obvious fixes — don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Zero context switching required from the user

## Task Management

1. **Plan First**: Write plan with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section after completion
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Minimal code impact.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimize Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

## Priority Order (Current)

1. Free Course — Videos, Slides
2. Pro Member — Videos, Slides, Post-purchase emails
3. Tools — OpnGovIQ, Tool videos
4. Jan Surge → Paid bootcamp
5. Client intake form + flow
6. The Vault → Software
7. SEO (all sites)
8. Internal site passcode + tool software
9. Uncle Manny — SAM redo, SDVOSB
