#!/usr/bin/env python3
"""
Batch capture 2 screenshots per course across all 28 courses.
Each entry: (url, lesson_id, slide_title, filename)
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "capture-slide-image.py"

# Phase 1 - Setup (6 courses)
CAPTURES = [
    # 1-1 Choose Your Business Structure (already has comparison table)
    ("https://www.gsa.gov/about-us/organization", "1-1-1", "why business structure matters", "p1-c1-business-structure"),
    ("https://www.sba.gov/business-guide/launch-your-business/choose-your-business-structure", "1-1-2", "introduction", "p1-c1-sba-structures"),
    # 1-2 Identify Your NAICS
    ("https://www.census.gov/naics/", "1-2-1", "official naics website", "p1-c2-naics-website"),
    ("https://sam.gov", "1-2-1", "sam.gov lookup", "p1-c2-sam-lookup"),
    # 1-3 Create Your SAM.gov Profile
    ("https://sam.gov", "1-3-1", "what is sam.gov?", "p1-c3-sam-homepage"),
    ("https://sam.gov/content/entity-information", "1-3-1", "entity registration overview", "p1-c3-entity-registration"),
    # 1-4 DSBS
    ("https://dsbs.sba.gov/", "1-4-1", "what is dsbs?", "p1-c4-dsbs-homepage"),
    ("https://dsbs.sba.gov/dsbs/search/dsp_dsbs.cfm", "1-4-1", "step-by-step registration", "p1-c4-dsbs-search"),
    # 1-5 Apex Accelerator (aptac-us.org may block automation; use SBA)
    ("https://www.sba.gov/business-guide/find-funding/ptac-counseling", "1-5-1", "what are apex accelerators?", "p1-c5-aptac-sba"),
    ("https://www.sba.gov/business-guide/find-funding/ptac-counseling", "1-5-1", "finding local apex accelerator", "p1-c5-aptac-locator-sba"),
    # 1-6 Capability Statement
    ("https://www.sba.gov/business-guide/grow-your-business/capability-statement", "1-6-1", "what is a capability statement?", "p1-c6-capability-statement"),
    ("https://www.sba.gov/federal-contracting/contracting-assistance-programs", "1-6-1", "certifications", "p1-c6-sba-certifications"),
    # Phase 2 - Bidding (6 courses)
    ("https://sam.gov/search/?index=opp", "2-1-1", "SAM.gov Contract Opportunities", "p2-c1-contract-opportunities"),
    ("https://sam.gov/search/?index=opp", "2-1-1", "saved searches and alerts", "p2-c1-saved-searches"),
    ("https://www.sba.gov/federal-contracting/contracting-guide/teaming", "2-2-1", "teaming structures", "p2-c2-teaming"),
    ("https://www.sba.gov/federal-contracting/contracting-guide/teaming-agreements", "2-2-1", "teaming agreements", "p2-c2-teaming-agreements"),
    ("https://www.sba.gov/business-guide/manage-your-business/manage-your-finances", "2-3-1", "why credit matters", "p2-c3-credit"),
    ("https://www.sba.gov/bonding", "2-3-1", "bonding requirements", "p2-c3-bonding"),
    ("https://sam.gov/search/?index=opp", "2-4-1", "RFP vs RFQ vs RFI", "p2-c4-opportunity-types"),
    ("https://sam.gov/content/opportunities", "2-4-1", "understanding solicitations", "p2-c4-solicitations"),
    ("https://sam.gov/search/?index=opp", "2-5-1", "submission process", "p2-c5-submission"),
    ("https://sam.gov/content/opportunities", "2-5-1", "proposal best practices", "p2-c5-proposal"),
    ("https://www.fpds.gov/", "2-6-1", "review award results", "p2-c6-fpds"),
    ("https://www.usaspending.gov/", "2-6-1", "document lessons learned", "p2-c6-usaspending"),
    # Phase 3 - Business Development (5 courses)
    ("https://www.fpds.gov/", "3-1-1", "FPDS and USAspending", "p3-c1-fpds"),
    ("https://www.usaspending.gov/", "3-1-1", "build target list", "p3-c1-usaspending"),
    ("https://www.sba.gov/federal-contracting/contracting-assistance-programs/osdbu-outreach", "3-2-1", "OSDBU meetings", "p3-c2-osdbu"),
    ("https://www.sba.gov/federal-contracting/contracting-assistance-programs", "3-2-1", "capabilities briefing", "p3-c2-capabilities"),
    ("https://www.sam.gov/content/industry-days", "3-3-1", "events and access", "p3-c3-industry-events"),
    ("https://www.sam.gov/content/industry-days", "3-3-2", "site visits overview", "p3-c3-site-visits"),
    ("https://www.sba.gov/federal-contracting/contracting-assistance-programs/8a-business-development-program", "3-4-1", "vendor portals", "p3-c4-vendor-portals"),
    ("https://dsbs.sba.gov/", "3-4-1", "supplier diversity programs", "p3-c4-supplier-diversity"),
    ("https://www.fpds.gov/", "3-5-1", "FPDS monitoring", "p3-c5-fpds-monitoring"),
    ("https://www.usaspending.gov/", "3-5-1", "subcontracting opportunities", "p3-c5-sub-opportunities"),
    # Phase 4 - Business Enhancement (7 courses) - 4-1 and 4-2 already have some images
    ("https://www.sba.gov/federal-contracting/contracting-assistance-programs", "4-1-1", "certification options", "p4-c1-cert-options"),
    ("https://www.sba.gov/federal-contracting/contracting-assistance-programs", "4-1-1", "eligibility", "p4-c1-eligibility"),
    ("https://www.sba.gov/federal-contracting/contracting-assistance-programs/8a-business-development-program", "4-2-1", "8(a) program overview", "p4-c2-8a-overview"),
    ("https://www.sba.gov/federal-contracting/contracting-assistance-programs/8a-business-development-program", "4-2-1", "application process", "p4-c2-8a-application"),
    ("https://www.sba.gov/federal-contracting/contracting-assistance-programs/mentor-protege-program", "4-3-1", "program benefits", "p4-c3-mentor-protege"),
    ("https://www.sba.gov/federal-contracting/contracting-assistance-programs/mentor-protege-program", "4-3-1", "joint ventures", "p4-c3-joint-ventures"),
    ("https://www.sba.gov/federal-contracting/contracting-assistance-programs", "4-4-1", "self-performance value", "p4-c4-self-performance"),
    ("https://www.sba.gov/business-guide/grow-your-business/capability-statement", "4-4-1", "document past performance", "p4-c4-past-performance"),
    ("https://www.sba.gov/federal-contracting/contracting-guide/teaming", "4-5-1", "evaluate partners", "p4-c5-evaluate-partners"),
    ("https://www.sba.gov/federal-contracting/contracting-guide/teaming-agreements", "4-5-1", "strategic partnerships", "p4-c5-strategic-partnerships"),
    ("https://www.sba.gov/federal-contracting/contracting-assistance-programs/mentor-protege-program", "4-6-1", "mid-size advantages", "p4-c6-mid-size"),
    ("https://www.sba.gov/federal-contracting/contracting-assistance-programs/mentor-protege-program", "4-6-1", "teaming arrangements", "p4-c6-teaming"),
    ("https://www.sba.gov/about-sba/sba-events", "4-7-1", "speaking benefits", "p4-c7-speaking"),
    ("https://www.sba.gov/about-sba", "4-7-1", "topic selection", "p4-c7-topic-selection"),
    # Phase 5 - Contract Management (4 courses)
    ("https://wawf.eb.mil/", "5-1-1", "what is WAWF?", "p5-c1-wawf"),
    ("https://piee.eb.mil/", "5-1-1", "what is PIEE?", "p5-c1-piee"),
    ("https://www.sba.gov/federal-contracting/contracting-guide/subcontracting", "5-2-1", "prime responsibility", "p5-c2-prime-responsibility"),
    ("https://www.sba.gov/federal-contracting/contracting-guide/subcontracting", "5-2-1", "flow-down clauses", "p5-c2-flowdown"),
    ("https://www.sba.gov/federal-contracting/contracting-guide", "5-3-1", "why compliance matters", "p5-c3-compliance"),
    ("https://www.sba.gov/federal-contracting/contracting-guide", "5-3-1", "contract terms overview", "p5-c3-contract-terms"),
    ("https://www.sba.gov/business-guide/manage-your-business", "5-4-1", "why communication matters", "p5-c4-communication"),
    ("https://www.sba.gov/business-guide/manage-your-business", "5-4-1", "establishing communication", "p5-c4-establishing"),
]


def main():
    total = len(CAPTURES)
    results = []
    for i, (url, lesson, slide, name) in enumerate(CAPTURES, 1):
        print(f"[{i}/{total}] {name}...", end=" ", flush=True)
        try:
            r = subprocess.run(
                [sys.executable, str(SCRIPT), url, "--lesson", lesson, "--slide", slide, "--name", name],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=45,
            )
            if r.returncode == 0:
                # Extract SLIDE_IMAGES line from output
                for line in r.stdout.splitlines():
                    if '("' in line and '): "' in line:
                        results.append(line.strip().rstrip(","))
                        break
                print("OK")
            else:
                print("FAILED:", r.stderr[:80] if r.stderr else r.stdout[:80])
        except subprocess.TimeoutExpired:
            print("TIMEOUT")
        except Exception as e:
            print("ERROR:", e)
    print("\n--- Add these to SLIDE_IMAGES in build-individual-slides.py ---\n")
    for r in results:
        print(f"    {r},")


if __name__ == "__main__":
    main()
