# Capturing Web Images for Slides

Two ways to grab visuals from the web and add them to slides: a **project script** (saves directly to assets) and an **MCP server** (for AI-assisted capture during chat).

---

## 1. Project Capture Script (Recommended)

The script `scripts/capture-slide-image.py` captures webpages or downloads images and saves them to `assets/images/`, then prints the exact line to add to `SLIDE_IMAGES`.

### Setup (one time)

```bash
pip install playwright
playwright install chromium
```

### Usage

**Screenshot a webpage:**
```bash
python3 scripts/capture-slide-image.py "https://sam.gov" \
  --lesson 1-3-1 --slide "what is sam.gov?" --name sam-homepage

python3 scripts/capture-slide-image.py "https://www.gsa.gov/topic/sam-gov" \
  --lesson 1-3-1 --slide "introduction" --name sam-gsa-overview

python3 scripts/capture-slide-image.py "https://www.dnb.com/duns-number" \
  --lesson 1-1-2 --slide "what is duns?" --name duns-dnb-page
```

**Capture a specific element** (e.g. header, hero section):
```bash
python3 scripts/capture-slide-image.py "https://sam.gov" \
  --lesson 1-3-1 --slide "what is sam.gov?" --selector "main" --name sam-main-content
```

**Full-page capture** (entire scrollable page):
```bash
python3 scripts/capture-slide-image.py "https://sam.gov" \
  --lesson 1-3-1 --slide "sam.gov overview" --full-page --name sam-full-page
```

**Download an image directly** (no Playwright needed):
```bash
python3 scripts/capture-slide-image.py "https://example.com/diagram.png" \
  --lesson 1-1-1 --slide "comparison" --download --name my-diagram
```

### After capture

1. The script prints a line like:
   ```
   ("1-3-1", "what is sam.gov?"): "../../assets/images/sam-homepage.png",
   ```
2. Add that line to `SLIDE_IMAGES` in `scripts/build-individual-slides.py`
3. Rebuild:
   ```bash
   python3 scripts/build-individual-slides.py
   python3 scripts/build-review-dashboard-28.py
   ```

---

## 2. MCP Screenshot Server (AI-Assisted)

Use an MCP server so the AI can take screenshots during a chat. When you say *"grab a screenshot of SAM.gov for the What is SAM.gov slide"*, the AI can call the tool.

### Option A: Universal Screenshot MCP (npx)

1. **Add to Cursor MCP config**  
   Cursor Settings → Features → MCP → Add New MCP Server

   - **Name:** `screenshot-server`
   - **Command:** `npx`
   - **Args:** `["-y", "universal-screenshot-mcp"]`

   Or edit `~/.cursor/mcp.json` (or Cursor’s MCP config file):

   ```json
   {
     "mcpServers": {
       "screenshot-server": {
         "command": "npx",
         "args": ["-y", "universal-screenshot-mcp"]
       }
     }
   }
   ```

2. **Limitation:** This server saves to `~/Desktop/Screenshots`, `~/Downloads`, or `~/Documents` (for security). To use images in slides, move them into the project:

   ```bash
   mv ~/Downloads/screenshot-*.png "/Users/ericcoffie/Projects/Action Plan/assets/images/"
   ```

3. Then add the image to `SLIDE_IMAGES` in `build-individual-slides.py` and rebuild.

### Option B: Run the project script via AI

You can skip MCP and ask the AI to run the capture script directly, e.g.:

> "Run the capture script for https://sam.gov, lesson 1-3-1, slide 'what is sam.gov?', name sam-homepage"

The AI can run:

```bash
python3 scripts/capture-slide-image.py "https://sam.gov" --lesson 1-3-1 --slide "what is sam.gov?" --name sam-homepage
```

Then add the printed `SLIDE_IMAGES` entry and rebuild.

---

## Slide/Lesson reference

| Topic        | Lesson ID | Example slide titles                  |
|-------------|-----------|---------------------------------------|
| SAM.gov     | 1-3-1     | "what is sam.gov?", "introduction"    |
| DUNS / UEI  | 1-1-2     | "what is duns?", "what is uei?"       |
| NAICS       | 1-2-1     | "sam.gov lookup", "official naics website" |
| Contract Opps | 2-2-1   | "sam.gov contract opportunities"      |

Lesson IDs and slide titles come from `data/courses-28.json` → `slideOutline`.

---

## Best practices

- **Name clearly:** Use `--name` so filenames are descriptive (e.g. `sam-homepage`, `uei-assignment-page`).
- **Slide title:** Match the slide title from `slideOutline` (lowercase). Check `courses-28.json` for exact wording.
- **Copyright:** Use government sites (SAM.gov, GSA, SBA) when possible; they’re usually public domain. For other sites, confirm usage rights.
