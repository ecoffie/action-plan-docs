#!/usr/bin/env python3
"""
Extract slide outlines from webinar markdown files and update courses-28.json.
Uses '## Slide Outline' section when present; otherwise derives from Agenda (### headers).
"""

import json
import re
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
WEBINARS_DIR = ROOT / "webinars"
COURSES_PATH = ROOT / "data" / "courses-28.json"

# Map webinar file stem to (phase_id, course lessons). Each lesson gets slides from its webinar.
# phase-N-NN -> list of (course_idx, lesson_idx) in courses-28 structure
WEBINAR_TO_LESSONS = {
    "phase-1-01-supplier-service-provider-consultant": ["1-1-1"],
    "phase-1-02-duns-and-uei": ["1-1-2"],
    "phase-1-03-creating-pro-email": ["1-1-3"],
    "phase-1-04-how-to-identify-naics": ["1-2-1"],
    "phase-1-05-how-to-create-sam-gov-profile": ["1-3-1"],
    "phase-1-06-dsbs": ["1-4-1"],
    "phase-1-07-benefits-what-to-say-apex-accelerator": ["1-5-1"],
    "phase-1-08-capability-statement-differentiators": ["1-6-1"],
    "phase-2-01-how-to-find-bid-opportunities": ["2-1-1"],
    "phase-2-02-assemble-team-based-on-opportunities": ["2-2-1"],
    "phase-2-03-apply-for-vendor-supplier-credit": ["2-3-1"],
    "phase-2-04-respond-to-opportunity": ["2-4-1", "2-5-1"],  # Understand Solicitations + Submit Proposal
    "phase-2-05-evaluate-bid-results": ["2-6-1"],
    "phase-3-01-identify-top-25-buyers-future-bids": ["3-1-1"],
    "phase-3-02-meetings-with-government-buyers": ["3-2-1"],
    "phase-3-03-attend-industry-events": ["3-3-1"],
    "phase-3-04-attend-site-visits": ["3-3-2"],
    "phase-3-05-get-on-supplier-list-top-25-suppliers": ["3-4-1"],
    "phase-3-06-monitor-contract-awards-sub-opportunities": ["3-5-1"],
    "phase-4-01-apply-small-business-certification": ["4-1-1"],
    "phase-4-02-8a-certification": ["4-2-1"],
    "phase-4-03-mentor-protege-program": ["4-3-1"],
    "phase-4-04-self-performance-differentiator": ["4-4-1"],
    "phase-4-05-find-better-partners": ["4-5-1"],
    "phase-4-06-identify-mid-size-mentor": ["4-6-1"],
    "phase-4-07-speak-at-event": ["4-7-1"],
    "phase-5-01-system-registrations-piee-wawf": ["5-1-1"],
    "phase-5-02-subcontractor-compliance": ["5-2-1"],
    "phase-5-03-project-compliance": ["5-3-1"],
    "phase-5-04-communication": ["5-4-1"],
}

# Fallback outlines for webinars without "## Slide Outline" - derived from Agenda
FALLBACK_OUTLINES = {
    "phase-2-01-how-to-find-bid-opportunities": [
        "Title", "Introduction", "SAM.gov Contract Opportunities", "Saved searches and alerts",
        "Opportunity types (RFP, RFQ, RFI)", "Search strategies", "Bid/no-bid criteria",
        "Key takeaways", "Next steps",
    ],
    "phase-2-02-assemble-team-based-on-opportunities": [
        "Title", "When you need a team", "Teaming structures", "Partner evaluation",
        "Teaming agreements", "Key takeaways", "Next steps",
    ],
    "phase-2-03-apply-for-vendor-supplier-credit": [
        "Title", "Why credit matters", "Business credit", "Bonding requirements",
        "Key takeaways", "Next steps",
    ],
    "phase-2-04-respond-to-opportunity": [
        "Title", "RFP vs RFQ vs RFI", "Understanding solicitations", "Reading and analyzing RFPs",
        "Compliance matrix", "Technical approach", "Past performance", "Price proposal",
        "Proposal best practices", "Submission process", "Key takeaways", "Next steps",
    ],
    "phase-2-05-evaluate-bid-results": [
        "Title", "Review award results", "Request debriefings", "Document lessons learned",
        "Refine strategy", "Key takeaways", "Next steps",
    ],
    "phase-3-01-identify-top-25-buyers-future-bids": [
        "Title", "Research before SAM.gov", "FPDS and USAspending", "Build target list",
        "Key takeaways", "Next steps",
    ],
    "phase-3-02-meetings-with-government-buyers": [
        "Title", "Relationships matter", "Capabilities briefing", "OSDBU meetings",
        "Preparation and follow-up", "Key takeaways", "Next steps",
    ],
    "phase-3-03-attend-industry-events": [
        "Title", "Events and access", "Preparation", "Networking", "Follow-up",
        "Key takeaways", "Next steps",
    ],
    "phase-3-04-attend-site-visits": [
        "Title", "Site visits overview", "Preparation", "Active listening",
        "Follow-up", "Key takeaways", "Next steps",
    ],
    "phase-3-05-get-on-supplier-list-top-25-suppliers": [
        "Title", "Vendor portals", "Supplier diversity programs", "Registration",
        "Key takeaways", "Next steps",
    ],
    "phase-3-06-monitor-contract-awards-sub-opportunities": [
        "Title", "FPDS monitoring", "IDIQs", "Subcontracting opportunities",
        "Key takeaways", "Next steps",
    ],
    "phase-4-01-apply-small-business-certification": [
        "Title", "Certification options", "WOSB, SDVOSB, HUBZone", "Eligibility",
        "Documentation", "Key takeaways", "Next steps",
    ],
    "phase-4-02-8a-certification": [
        "Title", "8(a) program overview", "Eligibility", "Application process",
        "Sole-source opportunities", "9-year program", "Key takeaways", "Next steps",
    ],
    "phase-4-03-mentor-protege-program": [
        "Title", "Program benefits", "Mentor selection", "Joint ventures",
        "Key takeaways", "Next steps",
    ],
    "phase-4-04-self-performance-differentiator": [
        "Title", "Self-performance value", "Document past performance",
        "Capability statements", "Key takeaways", "Next steps",
    ],
    "phase-4-05-find-better-partners": [
        "Title", "Evaluate partners", "Strategic partnerships",
        "Key takeaways", "Next steps",
    ],
    "phase-4-06-identify-mid-size-mentor": [
        "Title", "Mid-size advantages", "Teaming arrangements",
        "Key takeaways", "Next steps",
    ],
    "phase-4-07-speak-at-event": [
        "Title", "Speaking benefits", "Topic selection", "Proposals",
        "Key takeaways", "Next steps",
    ],
    "phase-5-02-subcontractor-compliance": [
        "Title", "Prime responsibility", "Flow-down clauses", "ISR and SSR reporting",
        "Documentation", "Key takeaways", "Next steps",
    ],
}


def extract_slide_outline(content: str) -> Optional[list[str]]:
    """Extract numbered list from '## Slide Outline' section."""
    m = re.search(r"^## Slide Outline\s*\n(.*?)(?=^## |\Z)", content, re.MULTILINE | re.DOTALL)
    if not m:
        return None
    block = m.group(1).strip()
    outlines = []
    for line in block.split("\n"):
        line = line.strip()
        # Match "1. Title" or "1. Title slide"
        mo = re.match(r"^\d+\.\s+(.+)$", line)
        if mo:
            outlines.append(mo.group(1).strip())
    return outlines if outlines else None


def get_outline_for_webinar(webinar_stem: str) -> list[str]:
    """Get slide outline from file or fallback."""
    path = WEBINARS_DIR / f"{webinar_stem}.md"
    if path.exists():
        content = path.read_text(encoding="utf-8")
        outline = extract_slide_outline(content)
        if outline:
            return outline
    return FALLBACK_OUTLINES.get(webinar_stem, ["Title", "Key takeaways", "Next steps"])


def split_outline_for_2_4_and_2_5(outline: list[str]) -> tuple[list[str], list[str]]:
    """Split phase-2-04 outline: 2-4-1 Understand Solicitations, 2-5-1 Submit Proposal."""
    # 2-4-1: solicitations (RFP/RFQ/RFI, reading, compliance). 2-5-1: proposal dev, submission
    for i, s in enumerate(outline):
        s_lower = s.lower()
        if "technical" in s_lower or "proposal" in s_lower and "compliance" not in s_lower:
            split_idx = i
            break
    else:
        split_idx = max(5, len(outline) // 2)
    part1 = outline[:split_idx]
    part2 = ["Title"] + outline[split_idx:] if split_idx < len(outline) else outline
    return part1, part2


def main():
    courses = json.loads(COURSES_PATH.read_text(encoding="utf-8"))
    lesson_to_outline: dict[str, list[str]] = {}

    for webinar_stem, lesson_ids in WEBINAR_TO_LESSONS.items():
        outline = get_outline_for_webinar(webinar_stem)
        if webinar_stem == "phase-2-04-respond-to-opportunity" and len(lesson_ids) == 2:
            part1, part2 = split_outline_for_2_4_and_2_5(outline)
            lesson_to_outline["2-4-1"] = part1
            lesson_to_outline["2-5-1"] = part2
        else:
            for lid in lesson_ids:
                lesson_to_outline[lid] = outline

    # Update courses-28.json
    for phase in courses["phases"]:
        for course in phase["courses"]:
            for lesson in course["lessons"]:
                lid = lesson["id"]
                if lid in lesson_to_outline:
                    lesson["slideOutline"] = lesson_to_outline[lid]
                    lesson["slideCount"] = len(lesson_to_outline[lid])

    COURSES_PATH.write_text(json.dumps(courses, indent=2, ensure_ascii=False), encoding="utf-8")
    total = sum(len(o) for o in lesson_to_outline.values())
    print(f"Updated {COURSES_PATH} with slide outlines ({total} total slides across lessons)")


if __name__ == "__main__":
    main()
