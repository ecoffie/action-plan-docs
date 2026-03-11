/**
 * Slide Generator for Action Plan Course
 * Generates HTML slides from course curriculum + scripts for AI avatar tools
 * Run from Action Plan repo root: node scripts/generate-slides.js
 */

const fs = require('fs');
const path = require('path');

const rootDir = path.join(__dirname, '..');
const curriculumPath = path.join(rootDir, 'data/course-curriculum.json');
const scriptsPath = path.join(rootDir, 'data/scripts/scripts.json');
const templatePath = path.join(rootDir, 'slides/slide-template.html');
const outputDir = path.join(rootDir, 'slides/generated');

const curriculum = JSON.parse(fs.readFileSync(curriculumPath, 'utf8'));
const scripts = JSON.parse(fs.readFileSync(scriptsPath, 'utf8'));
const template = fs.readFileSync(templatePath, 'utf8');

if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

let slideIndex = 0;
const manifest = [];

for (const phase of curriculum.phases) {
  for (const module of phase.modules) {
    for (const lesson of module.lessons) {
      const scriptData = scripts.scripts[lesson.id];
      if (!scriptData) continue;

      for (const slide of scriptData.slides) {
        slideIndex++;
        const html = template
          .replace('{{PHASE_NAME}}', `Phase ${phase.order}: ${phase.name}`)
          .replace('{{MODULE_TITLE}}', module.title)
          .replace('{{SLIDE_TITLE}}', slide.title)
          .replace('{{SLIDE_SUBTITLE}}', slide.narration.substring(0, 200) + (slide.narration.length > 200 ? '...' : ''))
          .replace('{{LESSON_ID}}', lesson.id);

        const filename = `slide-${String(slideIndex).padStart(3, '0')}-${lesson.id}.html`;
        const filepath = path.join(outputDir, filename);
        fs.writeFileSync(filepath, html);

        manifest.push({
          slideIndex,
          phaseId: phase.id,
          moduleId: module.id,
          lessonId: lesson.id,
          title: slide.title,
          filename,
          narration: slide.narration,
        });
      }
    }
  }
}

fs.writeFileSync(
  path.join(outputDir, 'manifest.json'),
  JSON.stringify({ slides: manifest, totalSlides: slideIndex }, null, 2)
);

console.log(`Generated ${slideIndex} slides in slides/generated/`);
console.log(`Manifest saved to slides/generated/manifest.json`);
