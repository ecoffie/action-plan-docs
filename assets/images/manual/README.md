# Manual Slide Images

Drop your images here. When ready to add one to a slide:

1. Add an entry to `SLIDE_IMAGES` in `scripts/build-individual-slides.py`:
   ```python
   ("lesson-id", "slide title lowercased"): "../../assets/images/manual/your-image.png",
   ```
2. Rebuild: `python3 scripts/build-individual-slides.py && python3 scripts/build-review-dashboard-28.py`

Slide titles come from `data/courses-28.json` → each lesson's `slideOutline`.
