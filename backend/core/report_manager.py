"""
Report Manager - Save and retrieve editing reports
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class ReportManager:
    """Manages saving and loading of editing reports"""
    
    def __init__(self, reports_dir: str = "backend/reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
    
    def save_acquisitions_report(self, manuscript_id: str, report: Dict):
        """Save Acquisitions Editor report"""
        manuscript_dir = self.reports_dir / manuscript_id
        manuscript_dir.mkdir(exist_ok=True)
        
        # Save editorial letter as markdown
        editorial_letter_path = manuscript_dir / "acquisitions_editorial_letter.md"
        with open(editorial_letter_path, "w", encoding="utf-8") as f:
            f.write(f"# Acquisitions Editor Report\n\n")
            f.write(f"**Manuscript ID:** {manuscript_id}\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write("## Editorial Letter\n\n")
            f.write(report.get("editorial_letter", ""))
        
        # Save full report as JSON
        report_path = manuscript_dir / "acquisitions_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved Acquisitions report to {manuscript_dir}")
    
    def save_stage_report(self, manuscript_id: str, stage: str, issues: list, fixes_applied: int = 0):
        """Save review stage report (Developmental, Line, Copy, Proof)"""
        manuscript_dir = self.reports_dir / manuscript_id
        manuscript_dir.mkdir(exist_ok=True)
        
        report_data = {
            "manuscript_id": manuscript_id,
            "stage": stage,
            "timestamp": datetime.now().isoformat(),
            "total_issues": len(issues),
            "fixes_applied": fixes_applied,
            "issues": issues
        }
        
        # Save as JSON
        report_path = manuscript_dir / f"{stage}_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # Save as Markdown
        md_path = manuscript_dir / f"{stage}_report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {stage.title()} Editor Report\n\n")
            f.write(f"**Manuscript ID:** {manuscript_id}\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Issues Found:** {len(issues)}\n\n")
            f.write(f"**Fixes Applied:** {fixes_applied}\n\n")
            f.write("---\n\n")
            f.write("## Issues\n\n")
            
            for i, issue in enumerate(issues, 1):
                severity = issue.get("severity", "unknown").upper()
                category = issue.get("category", "unknown")
                location = issue.get("location", "Unknown")
                description = issue.get("description", "")
                suggestion = issue.get("suggestion", "")
                
                f.write(f"### Issue {i}: {category}\n\n")
                f.write(f"**Severity:** {severity}\n\n")
                f.write(f"**Location:** {location}\n\n")
                f.write(f"**Description:** {description}\n\n")
                f.write(f"**Suggestion:** {suggestion}\n\n")
                f.write("---\n\n")
        
        print(f"✅ Saved {stage} report to {manuscript_dir}")
    
    def load_report(self, manuscript_id: str, stage: str) -> Optional[Dict]:
        """Load a saved report"""
        report_path = self.reports_dir / manuscript_id / f"{stage}_report.json"
        
        if not report_path.exists():
            return None
        
        with open(report_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_all_reports(self, manuscript_id: str) -> Dict:
        """Get all reports for a manuscript"""
        manuscript_dir = self.reports_dir / manuscript_id
        
        if not manuscript_dir.exists():
            return {}
        
        reports = {}
        for report_file in manuscript_dir.glob("*_report.json"):
            stage = report_file.stem.replace("_report", "")
            with open(report_file, "r", encoding="utf-8") as f:
                reports[stage] = json.load(f)
        
        return reports
    
    def generate_complete_report(self, manuscript_id: str) -> str:
        """Generate a complete markdown report combining all stages"""
        manuscript_dir = self.reports_dir / manuscript_id
        
        if not manuscript_dir.exists():
            return "No reports found"
        
        complete_report = f"# Complete Editorial Report\n\n"
        complete_report += f"**Manuscript ID:** {manuscript_id}\n\n"
        complete_report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        complete_report += "---\n\n"
        
        # Combine all markdown reports
        for md_file in sorted(manuscript_dir.glob("*.md")):
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
                # Skip the header from individual reports
                if "# " in content:
                    content = content.split("\n", 1)[1]
                complete_report += content + "\n\n"
        
        # Save complete report
        complete_path = manuscript_dir / "complete_report.md"
        with open(complete_path, "w", encoding="utf-8") as f:
            f.write(complete_report)
        
        return complete_report
