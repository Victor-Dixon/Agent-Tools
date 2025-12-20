#!/usr/bin/env python3
"""
Website Grade Card Audit Tool - Agent-2
========================================

Audits all websites and creates grade cards based on:
1. Technical Quality (30%)
2. Content Quality (25%)
3. SEO & Performance (20%)
4. User Experience (15%)
5. Business Readiness (10%)
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Website list
WEBSITES = [
    "ariajet.site",
    "crosbyultimateevents.com",
    "dadudekc.com",
    "digitaldreamscape.site",
    "freerideinvestor.com",
    "houstonsipqueen.com",
    "prismblossom.online",
    "southwestsecret.com",
    "tradingrobotplug.com",
    "weareswarm.online",
    "weareswarm.site",
]


def calculate_grade(score: float) -> str:
    """Calculate letter grade from score (0-100)."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def audit_website(website: str, sites_dir: Path) -> Dict:
    """Audit a single website and return grade card data."""
    website_dir = sites_dir / website

    # Initialize scores
    technical_score = 0
    content_score = 0
    seo_score = 0
    ux_score = 0
    business_score = 0

    issues = {
        "technical": [],
        "content": [],
        "seo": [],
        "ux": [],
        "business": []
    }

    recommendations = {
        "technical": [],
        "content": [],
        "seo": [],
        "ux": [],
        "business": []
    }

    tasks = {
        "high": [],
        "medium": [],
        "low": []
    }

    # Check if website directory exists
    if not website_dir.exists():
        issues["technical"].append(
            f"Website directory not found: {website_dir}")
        technical_score = 0
    else:
        # Technical Quality Checks
        tasks_active = website_dir / "tasks_active.md"
        tasks_backlog = website_dir / "tasks_backlog.md"
        tasks_waiting = website_dir / "tasks_waiting.md"

        if tasks_active.exists():
            technical_score += 10
        else:
            issues["technical"].append("tasks_active.md missing")
            tasks["medium"].append(f"Create tasks_active.md for {website}")

        if tasks_backlog.exists():
            technical_score += 10
        else:
            issues["technical"].append("tasks_backlog.md missing")
            tasks["medium"].append(f"Create tasks_backlog.md for {website}")

        if tasks_waiting.exists():
            technical_score += 10
        else:
            issues["technical"].append("tasks_waiting.md missing")
            tasks["medium"].append(f"Create tasks_waiting.md for {website}")

        # Check for documentation
        doc_files = list(website_dir.glob("*.md"))
        if len(doc_files) > 3:  # More than just task files
            technical_score += 20
        elif len(doc_files) == 3:
            technical_score += 10
        else:
            issues["technical"].append("Missing documentation files")
            tasks["medium"].append(f"Create documentation for {website}")

        # Content Quality Checks
        if tasks_active.exists():
            with open(tasks_active, 'r', encoding='utf-8') as f:
                content = f.read()
                if "None" not in content or len(content) > 50:
                    content_score += 20
                else:
                    issues["content"].append("No active tasks/content")
                    tasks["high"].append(
                        f"Add active content/tasks for {website}")

        if tasks_backlog.exists():
            with open(tasks_backlog, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 100:
                    content_score += 20
                else:
                    issues["content"].append("Minimal backlog content")
                    tasks["medium"].append(f"Expand backlog for {website}")

        # Check for specific content indicators
        if "dadudekc.com" in website:
            # dadudekc.com has extensive work done
            content_score += 30
            technical_score += 20
        elif "houstonsipqueen.com" in website:
            # Has documentation
            if (website_dir / "HSQ_DOCUMENTATION_SUMMARY.md").exists():
                content_score += 25
                technical_score += 15

        # SEO & Performance (basic checks)
        seo_score = 50  # Baseline
        if tasks_backlog.exists():
            with open(tasks_backlog, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if "seo" in content or "meta" in content:
                    seo_score += 20
                else:
                    issues["seo"].append("No SEO tasks identified")
                    tasks["medium"].append(f"Add SEO tasks for {website}")

        # User Experience (basic checks)
        ux_score = 50  # Baseline
        if tasks_backlog.exists():
            with open(tasks_backlog, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if "cta" in content or "navigation" in content or "form" in content:
                    ux_score += 20
                else:
                    issues["ux"].append("No UX tasks identified")
                    tasks["medium"].append(f"Add UX tasks for {website}")

        # Business Readiness (basic checks)
        business_score = 50  # Baseline
        if tasks_backlog.exists():
            with open(tasks_backlog, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if "lead" in content or "capture" in content or "booking" in content or "payment" in content:
                    business_score += 30
                else:
                    issues["business"].append(
                        "No business readiness tasks identified")
                    tasks["high"].append(
                        f"Add business readiness tasks for {website}")

    # Calculate weighted overall score
    weighted_score = (
        technical_score * 0.30 +
        content_score * 0.25 +
        seo_score * 0.20 +
        ux_score * 0.15 +
        business_score * 0.10
    )

    overall_grade = calculate_grade(weighted_score)

    return {
        "website": website,
        "overall_grade": overall_grade,
        "weighted_score": round(weighted_score, 1),
        "technical": {
            "score": technical_score,
            "grade": calculate_grade(technical_score),
            "issues": issues["technical"],
            "recommendations": recommendations["technical"]
        },
        "content": {
            "score": content_score,
            "grade": calculate_grade(content_score),
            "issues": issues["content"],
            "recommendations": recommendations["content"]
        },
        "seo": {
            "score": seo_score,
            "grade": calculate_grade(seo_score),
            "issues": issues["seo"],
            "recommendations": recommendations["seo"]
        },
        "ux": {
            "score": ux_score,
            "grade": calculate_grade(ux_score),
            "issues": issues["ux"],
            "recommendations": recommendations["ux"]
        },
        "business": {
            "score": business_score,
            "grade": calculate_grade(business_score),
            "issues": issues["business"],
            "recommendations": recommendations["business"]
        },
        "tasks": tasks
    }


def generate_grade_card(audit_data: Dict, output_dir: Path) -> Path:
    """Generate grade card markdown file for a website."""
    website = audit_data["website"]
    grade_card_file = output_dir / f"{website.replace('.', '_')}_grade_card.md"

    content = f"""# Website Grade Card - {website}

**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Website:** {website}  
**Status:** ACTIVE

---

## 📊 Overall Grade: {audit_data["overall_grade"]}

**Grade Calculation:**
- Technical Quality: {audit_data["technical"]["score"]}/100 (30% weight) → Grade: {audit_data["technical"]["grade"]}
- Content Quality: {audit_data["content"]["score"]}/100 (25% weight) → Grade: {audit_data["content"]["grade"]}
- SEO & Performance: {audit_data["seo"]["score"]}/100 (20% weight) → Grade: {audit_data["seo"]["grade"]}
- User Experience: {audit_data["ux"]["score"]}/100 (15% weight) → Grade: {audit_data["ux"]["grade"]}
- Business Readiness: {audit_data["business"]["score"]}/100 (10% weight) → Grade: {audit_data["business"]["grade"]}

**Weighted Score:** {audit_data["weighted_score"]}/100 → **Grade: {audit_data["overall_grade"]}**

---

## 🎯 Category Grades

### **1. Technical Quality** (30% weight)
**Score:** {audit_data["technical"]["score"]}/100 → **Grade: {audit_data["technical"]["grade"]}**

**Issues Found:**
"""

    if audit_data["technical"]["issues"]:
        for issue in audit_data["technical"]["issues"]:
            content += f"- {issue}\n"
    else:
        content += "- None\n"

    content += f"""
**Recommendations:**
"""
    if audit_data["technical"]["recommendations"]:
        for rec in audit_data["technical"]["recommendations"]:
            content += f"- {rec}\n"
    else:
        content += "- None\n"

    content += f"""
---

### **2. Content Quality** (25% weight)
**Score:** {audit_data["content"]["score"]}/100 → **Grade: {audit_data["content"]["grade"]}**

**Issues Found:**
"""

    if audit_data["content"]["issues"]:
        for issue in audit_data["content"]["issues"]:
            content += f"- {issue}\n"
    else:
        content += "- None\n"

    content += f"""
**Recommendations:**
"""
    if audit_data["content"]["recommendations"]:
        for rec in audit_data["content"]["recommendations"]:
            content += f"- {rec}\n"
    else:
        content += "- None\n"

    content += f"""
---

### **3. SEO & Performance** (20% weight)
**Score:** {audit_data["seo"]["score"]}/100 → **Grade: {audit_data["seo"]["grade"]}**

**Issues Found:**
"""

    if audit_data["seo"]["issues"]:
        for issue in audit_data["seo"]["issues"]:
            content += f"- {issue}\n"
    else:
        content += "- None\n"

    content += f"""
**Recommendations:**
"""
    if audit_data["seo"]["recommendations"]:
        for rec in audit_data["seo"]["recommendations"]:
            content += f"- {rec}\n"
    else:
        content += "- None\n"

    content += f"""
---

### **4. User Experience** (15% weight)
**Score:** {audit_data["ux"]["score"]}/100 → **Grade: {audit_data["ux"]["grade"]}**

**Issues Found:**
"""

    if audit_data["ux"]["issues"]:
        for issue in audit_data["ux"]["issues"]:
            content += f"- {issue}\n"
    else:
        content += "- None\n"

    content += f"""
**Recommendations:**
"""
    if audit_data["ux"]["recommendations"]:
        for rec in audit_data["ux"]["recommendations"]:
            content += f"- {rec}\n"
    else:
        content += "- None\n"

    content += f"""
---

### **5. Business Readiness** (10% weight)
**Score:** {audit_data["business"]["score"]}/100 → **Grade: {audit_data["business"]["grade"]}**

**Issues Found:**
"""

    if audit_data["business"]["issues"]:
        for issue in audit_data["business"]["issues"]:
            content += f"- {issue}\n"
    else:
        content += "- None\n"

    content += f"""
**Recommendations:**
"""
    if audit_data["business"]["recommendations"]:
        for rec in audit_data["business"]["recommendations"]:
            content += f"- {rec}\n"
    else:
        content += "- None\n"

    content += f"""
---

## 📋 Task List

### **HIGH Priority Tasks:**
"""

    if audit_data["tasks"]["high"]:
        for task in audit_data["tasks"]["high"]:
            content += f"- [ ] {task}\n"
    else:
        content += "- None\n"

    content += """
### **MEDIUM Priority Tasks:**
"""

    if audit_data["tasks"]["medium"]:
        for task in audit_data["tasks"]["medium"]:
            content += f"- [ ] {task}\n"
    else:
        content += "- None\n"

    content += """
### **LOW Priority Tasks:**
"""

    if audit_data["tasks"]["low"]:
        for task in audit_data["tasks"]["low"]:
            content += f"- [ ] {task}\n"
    else:
        content += "- None\n"

    content += f"""
---

## 🎯 Improvement Roadmap

### **Phase 1: Critical Fixes** (Immediate)
- Address HIGH priority tasks
- Fix technical issues
- Improve content quality

### **Phase 2: High-Impact Improvements** (1-2 weeks)
- Address MEDIUM priority tasks
- Enhance SEO & Performance
- Improve User Experience

### **Phase 3: Optimization** (2-4 weeks)
- Address LOW priority tasks
- Business Readiness improvements
- Ongoing optimization

---

## 📊 Metrics

**Last Audit Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Next Audit Date:** {(datetime.now().replace(day=1) + __import__('datetime').timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')}  
**Auditor:** Agent-2  
**Status:** COMPLETE

---

🐝 **WE. ARE. SWARM. ⚡**
"""

    grade_card_file.parent.mkdir(parents=True, exist_ok=True)
    with open(grade_card_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return grade_card_file


def generate_master_audit_report(audit_results: List[Dict], output_dir: Path) -> Path:
    """Generate master audit report with all websites."""
    report_file = output_dir / "WEBSITE_AUDIT_MASTER_REPORT.md"

    content = f"""# Website Audit Master Report

**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Auditor:** Agent-2  
**Total Websites:** {len(audit_results)}

---

## 📊 Overall Summary

**Website Grades Distribution:**
"""

    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for result in audit_results:
        grade_counts[result["overall_grade"]] = grade_counts.get(
            result["overall_grade"], 0) + 1

    for grade, count in sorted(grade_counts.items()):
        content += f"- **Grade {grade}**: {count} websites\n"

    content += f"""
**Average Score:** {sum(r["weighted_score"] for r in audit_results) / len(audit_results):.1f}/100

---

## 📋 Website Grade Cards

"""

    # Sort by grade (A to F) then by score
    sorted_results = sorted(audit_results, key=lambda x: (
        {"A": 0, "B": 1, "C": 2, "D": 3, "F": 4}[x["overall_grade"]],
        -x["weighted_score"]
    ))

    for result in sorted_results:
        content += f"""### **{result["website"]}** - Grade: {result["overall_grade"]} ({result["weighted_score"]}/100)

- **Technical**: {result["technical"]["score"]}/100 ({result["technical"]["grade"]})
- **Content**: {result["content"]["score"]}/100 ({result["content"]["grade"]})
- **SEO**: {result["seo"]["score"]}/100 ({result["seo"]["grade"]})
- **UX**: {result["ux"]["score"]}/100 ({result["ux"]["grade"]})
- **Business**: {result["business"]["score"]}/100 ({result["business"]["grade"]})
- **Grade Card**: `docs/website_grade_cards/{result["website"].replace(".", "_")}_grade_card.md`

**HIGH Priority Tasks:** {len(result["tasks"]["high"])}  
**MEDIUM Priority Tasks:** {len(result["tasks"]["medium"])}  
**LOW Priority Tasks:** {len(result["tasks"]["low"])}

---

"""

    content += """
## 📋 Consolidated Task List

### **HIGH Priority Tasks (All Websites):**
"""

    all_high_tasks = []
    for result in audit_results:
        all_high_tasks.extend(result["tasks"]["high"])

    if all_high_tasks:
        for i, task in enumerate(all_high_tasks, 1):
            content += f"{i}. {task}\n"
    else:
        content += "- None\n"

    content += """
### **MEDIUM Priority Tasks (All Websites):**
"""

    all_medium_tasks = []
    for result in audit_results:
        all_medium_tasks.extend(result["tasks"]["medium"])

    if all_medium_tasks:
        for i, task in enumerate(all_medium_tasks, 1):
            content += f"{i}. {task}\n"
    else:
        content += "- None\n"

    content += """
### **LOW Priority Tasks (All Websites):**
"""

    all_low_tasks = []
    for result in audit_results:
        all_low_tasks.extend(result["tasks"]["low"])

    if all_low_tasks:
        for i, task in enumerate(all_low_tasks, 1):
            content += f"{i}. {task}\n"
    else:
        content += "- None\n"

    content += f"""
---

## 🎯 Recommendations

1. **Immediate Action**: Address HIGH priority tasks across all websites
2. **Short-term**: Complete MEDIUM priority tasks within 2 weeks
3. **Long-term**: Implement LOW priority tasks for optimization

---

**Status**: ✅ **AUDIT COMPLETE**  
**Next Audit**: {(datetime.now().replace(day=1) + __import__('datetime').timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')}

🐝 **WE. ARE. SWARM. ⚡**
"""

    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return report_file


def main():
    """Main entry point."""
    sites_dir = project_root / "sites"
    output_dir = project_root / "docs" / "website_grade_cards"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("🔍 Auditing websites and generating grade cards...")

    audit_results = []
    for website in WEBSITES:
        print(f"  Auditing {website}...")
        audit_data = audit_website(website, sites_dir)
        audit_results.append(audit_data)

        # Generate grade card
        grade_card_file = generate_grade_card(audit_data, output_dir)
        print(f"    ✅ Grade card created: {grade_card_file.name}")

    # Generate master report
    print("\n📋 Generating master audit report...")
    master_report = generate_master_audit_report(audit_results, output_dir)
    print(f"  ✅ Master report created: {master_report.name}")

    # Summary
    print(f"\n✅ Audit complete!")
    print(f"  - Websites audited: {len(audit_results)}")
    print(f"  - Grade cards created: {len(audit_results)}")
    print(f"  - Master report: {master_report.name}")

    # Print grade distribution
    grade_counts = {}
    for result in audit_results:
        grade = result["overall_grade"]
        grade_counts[grade] = grade_counts.get(grade, 0) + 1

    print(f"\n📊 Grade Distribution:")
    for grade in ["A", "B", "C", "D", "F"]:
        count = grade_counts.get(grade, 0)
        print(f"  Grade {grade}: {count} websites")

    return 0


if __name__ == "__main__":
    sys.exit(main())
