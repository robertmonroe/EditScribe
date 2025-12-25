"""
Project Manager - File Organization for EditScribe
Manages all project files, reports, versions, and metadata
"""

import os
import json
import difflib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List


class ProjectManager:
    """
    Manages project file structure and persistence.
    
    Structure:
    projects/
        {manuscript_id}/
            manuscript/
                original.txt
                current.txt
                versions/
                    v1_after_acquisitions.txt
                    v2_after_developmental.txt
                    ...
            reports/
                acquisitions/
                    editorial_letter.md
                    editorial_letter.json
                developmental/
                    report.md
                    issues.json
                ...
            style_sheet/
                style_sheet.json
            workflow/
                status.json
                history.json
            metadata.json
    """
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            # Use absolute path relative to this file's location
            current_file = Path(__file__).resolve()
            backend_dir = current_file.parent.parent  # Go up to backend/
            base_dir = backend_dir / "projects"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def create_project(self, manuscript_id: str, title: str, original_text: str) -> Dict[str, Any]:
        """Create new project structure"""
        project_dir = self.base_dir / manuscript_id
        
        # Create directory structure
        (project_dir / "manuscript" / "versions").mkdir(parents=True, exist_ok=True)
        (project_dir / "reports" / "acquisitions").mkdir(parents=True, exist_ok=True)
        (project_dir / "reports" / "developmental").mkdir(parents=True, exist_ok=True)
        (project_dir / "reports" / "line").mkdir(parents=True, exist_ok=True)
        (project_dir / "reports" / "copy").mkdir(parents=True, exist_ok=True)
        (project_dir / "reports" / "proof").mkdir(parents=True, exist_ok=True)
        (project_dir / "style_sheet").mkdir(parents=True, exist_ok=True)
        (project_dir / "workflow").mkdir(parents=True, exist_ok=True)
        
        # Save original manuscript
        with open(project_dir / "manuscript" / "original.txt", "w", encoding="utf-8") as f:
            f.write(original_text)
        
        # Save current manuscript (same as original initially)
        with open(project_dir / "manuscript" / "current.txt", "w", encoding="utf-8") as f:
            f.write(original_text)
        
        # Create metadata
        metadata = {
            "manuscript_id": manuscript_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "word_count": len(original_text.split()),
            "stages_completed": []
        }
        
        with open(project_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        return metadata
    
    def save_manuscript_version(self, manuscript_id: str, stage: str, text: str):
        """Save manuscript version after a stage"""
        project_dir = self.base_dir / manuscript_id
        version_file = project_dir / "manuscript" / "versions" / f"v_{stage}.txt"
        
        with open(version_file, "w", encoding="utf-8") as f:
            f.write(text)
        
        # Update current manuscript
        with open(project_dir / "manuscript" / "current.txt", "w", encoding="utf-8") as f:
            f.write(text)

    def list_versions(self, manuscript_id: str) -> list:
        """List all available manuscript versions"""
        project_dir = self.base_dir / manuscript_id
        versions_dir = project_dir / "manuscript" / "versions"
        
        versions = []
        if versions_dir.exists():
            for file in versions_dir.glob("v_*.txt"):
                stage = file.stem[2:] # remove 'v_'
                stats = file.stat()
                versions.append({
                    "version": stage,
                    "filename": file.name,
                    "created_at": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                    "size": stats.st_size
                })
        
        # Add original if exists
        original = project_dir / "manuscript" / "original.txt"
        if original.exists():
            stats = original.stat()
            versions.append({
                "version": "original",
                "filename": "original.txt",
                "created_at": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "size": stats.st_size
            })
            
        return sorted(versions, key=lambda x: x["created_at"], reverse=True)

    def restore_version(self, manuscript_id: str, version_name: str) -> bool:
        """Restore specific version as current"""
        project_dir = self.base_dir / manuscript_id
        
        if version_name == "original":
            src = project_dir / "manuscript" / "original.txt"
        else:
            # Handle both 'stage' and full filename cases
            src = project_dir / "manuscript" / "versions" / f"v_{version_name}.txt"
            if not src.exists():
                 src = project_dir / "manuscript" / "versions" / f"{version_name}"
        
        if not src.exists():
            return False
            
        # Create backup of current before restoring
        current = project_dir / "manuscript" / "current.txt"
        if current.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup = project_dir / "manuscript" / "versions" / f"v_pre_restore_{timestamp}.txt"
            import shutil
            shutil.copy2(current, backup)
            
        # Restore
        with open(src, "r", encoding="utf-8") as f:
            text = f.read()
            
        with open(current, "w", encoding="utf-8") as f:
            f.write(text)
            
        return True
    
    def save_acquisitions_report(self, manuscript_id: str, report: Dict[str, Any]):
        """Save Acquisitions Editor report"""
        project_dir = self.base_dir / manuscript_id / "reports" / "acquisitions"
        
        # Save JSON
        with open(project_dir / "editorial_letter.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        
        # Save Markdown
        md_content = self._format_acquisitions_markdown(report)
        with open(project_dir / "editorial_letter.md", "w", encoding="utf-8") as f:
            f.write(md_content)
    
    def save_stage_report(self, manuscript_id: str, stage: str, issues: list, report_data: Optional[Dict] = None):
        """Save report for developmental/line/copy/proof stages"""
        project_dir = self.base_dir / manuscript_id / "reports" / stage
        
        # Save issues JSON
        with open(project_dir / "issues.json", "w", encoding="utf-8") as f:
            json.dump(issues, f, indent=2)
        
        # Save report JSON if provided
        if report_data:
            with open(project_dir / "report.json", "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)
        
        # Save Markdown summary
        md_content = self._format_stage_markdown(stage, issues)
        with open(project_dir / "report.md", "w", encoding="utf-8") as f:
            f.write(md_content)
    
    def save_style_sheet(self, manuscript_id: str, style_sheet: Dict[str, Any]):
        """Save Style Sheet"""
        project_dir = self.base_dir / manuscript_id / "style_sheet"
        
        with open(project_dir / "style_sheet.json", "w", encoding="utf-8") as f:
            json.dump(style_sheet, f, indent=2)
    
    def save_workflow_status(self, manuscript_id: str, workflow: Dict[str, Any]):
        """Save workflow status"""
        project_dir = self.base_dir / manuscript_id / "workflow"
        
        with open(project_dir / "status.json", "w", encoding="utf-8") as f:
            json.dump(workflow, f, indent=2)
    
    def load_project(self, manuscript_id: str) -> Optional[Dict[str, Any]]:
        """Load complete project data"""
        project_dir = self.base_dir / manuscript_id
        
        if not project_dir.exists():
            return None
        
        # Load metadata
        with open(project_dir / "metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        # Load current manuscript
        with open(project_dir / "manuscript" / "current.txt", "r", encoding="utf-8") as f:
            current_text = f.read()
        
        # Load workflow status
        workflow_file = project_dir / "workflow" / "status.json"
        workflow = None
        if workflow_file.exists():
            with open(workflow_file, "r", encoding="utf-8") as f:
                workflow = json.load(f)
        
        return {
            "metadata": metadata,
            "current_text": current_text,
            "workflow": workflow
        }

    def load_style_sheet(self, manuscript_id: str) -> Optional[Dict[str, Any]]:
        """Load style sheet from disk"""
        style_sheet_file = self.base_dir / manuscript_id / "style_sheet" / "style_sheet.json"
        if style_sheet_file.exists():
            with open(style_sheet_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def load_workflow_status(self, manuscript_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow status from disk"""
        workflow_file = self.base_dir / manuscript_id / "workflow" / "status.json"
        if workflow_file.exists():
            with open(workflow_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def load_acquisitions_report(self, manuscript_id: str) -> Optional[Dict[str, Any]]:
        """Load acquisitions report from disk"""
        report_file = self.base_dir / manuscript_id / "reports" / "acquisitions" / "editorial_letter.json"
        if report_file.exists():
            with open(report_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def load_stage_report(self, manuscript_id: str, stage: str) -> Optional[Dict[str, Any]]:
        """Load stage report from disk"""
        # For micro stages, we primarily look for issues.json, but also report.json if it exists
        project_dir = self.base_dir / manuscript_id / "reports" / stage
        
        result = {}
        
        issues_file = project_dir / "issues.json"
        if issues_file.exists():
            with open(issues_file, "r", encoding="utf-8") as f:
                result["issues"] = json.load(f)
                
        report_file = project_dir / "report.json"
        if report_file.exists():
            with open(report_file, "r", encoding="utf-8") as f:
                result["report"] = json.load(f)
                
        return result if result else None
    
    def list_projects(self) -> list:
        """List all projects"""
        projects = []
        
        for project_dir in self.base_dir.iterdir():
            if project_dir.is_dir():
                metadata_file = project_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                        projects.append(metadata)
        
        return sorted(projects, key=lambda x: x["last_modified"], reverse=True)
    
    def delete_project(self, manuscript_id: str) -> bool:
        """Delete a project and all its files"""
        import shutil
        project_dir = self.base_dir / manuscript_id
        
        if not project_dir.exists():
            return False
        
        try:
            shutil.rmtree(project_dir)
            return True
        except Exception as e:
            print(f"Error deleting project {manuscript_id}: {e}")
            return False

    def duplicate_project(self, manuscript_id: str) -> Optional[Dict[str, Any]]:
        """Duplicate an existing project (Backup)"""
        import shutil
        import uuid
        
        source_dir = self.base_dir / manuscript_id
        if not source_dir.exists():
            return None
            
        # Generate new ID
        new_id = str(uuid.uuid4())
        dest_dir = self.base_dir / new_id
        
        try:
            # Copy entire directory
            shutil.copytree(source_dir, dest_dir)
            
            # Update metadata with new ID and title
            metadata_file = dest_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                
                metadata["manuscript_id"] = new_id
                metadata["title"] = f"{metadata.get('title', 'Untitled')} (Copy)"
                metadata["created_at"] = datetime.now().isoformat()
                metadata["last_modified"] = datetime.now().isoformat()
                
                with open(metadata_file, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2)
            
            # Update style sheet ID if exists
            style_sheet_file = dest_dir / "style_sheet" / "style_sheet.json"
            if style_sheet_file.exists():
                with open(style_sheet_file, "r", encoding="utf-8") as f:
                    style_data = json.load(f)
                style_data["manuscript_id"] = new_id
                with open(style_sheet_file, "w", encoding="utf-8") as f:
                    json.dump(style_data, f, indent=2)
            
            # Update workflow ID if exists
            workflow_file = dest_dir / "workflow" / "status.json"
            if workflow_file.exists():
                with open(workflow_file, "r", encoding="utf-8") as f:
                    workflow_data = json.load(f)
                workflow_data["manuscript_id"] = new_id
                with open(workflow_file, "w", encoding="utf-8") as f:
                    json.dump(workflow_data, f, indent=2)

            return metadata
        except Exception as e:
            print(f"Error duplicating project {manuscript_id}: {e}")
            # cleanup partial copy
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            return None

    def rename_project(self, manuscript_id: str, new_title: str) -> bool:
        """Rename a project"""
        project_dir = self.base_dir / manuscript_id
        if not project_dir.exists():
            return False
            
        metadata_file = project_dir / "metadata.json"
        
        try:
            if metadata_file.exists():
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                
                metadata["title"] = new_title
                metadata["last_modified"] = datetime.now().isoformat()
                
                with open(metadata_file, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2)
                return True
            return False
        except Exception as e:
            print(f"Error renaming project {manuscript_id}: {e}")
            return False
    
    def generate_complete_report(self, manuscript_id: str) -> str:
        """Generate complete editorial package"""
        project_dir = self.base_dir / manuscript_id
        reports_dir = project_dir / "reports"
        
        sections = []
        
        # Header
        with open(project_dir / "metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        sections.append(f"# Complete Editorial Report: {metadata['title']}\n")
        sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        sections.append("---\n\n")
        
        # Acquisitions
        acq_file = reports_dir / "acquisitions" / "editorial_letter.md"
        if acq_file.exists():
            with open(acq_file, "r", encoding="utf-8") as f:
                sections.append("## Acquisitions Editor Report\n\n")
                sections.append(f.read())
                sections.append("\n\n---\n\n")
        
        # Other stages
        for stage in ["developmental", "line", "copy", "proof"]:
            stage_file = reports_dir / stage / "report.md"
            if stage_file.exists():
                with open(stage_file, "r", encoding="utf-8") as f:
                    sections.append(f"## {stage.title()} Editor Report\n\n")
                    sections.append(f.read())
                    sections.append("\n\n---\n\n")
        
        complete_report = "".join(sections)
        
        # Save complete report
        with open(reports_dir / "complete_report.md", "w", encoding="utf-8") as f:
            f.write(complete_report)
        
        return complete_report
    
    def _format_acquisitions_markdown(self, report: Dict[str, Any]) -> str:
        """Format acquisitions report as Markdown"""
        sections = []
        
        sections.append("# Acquisitions Editor Report\n\n")
        
        if "editorial_letter" in report:
            sections.append("## Editorial Letter\n\n")
            sections.append(report["editorial_letter"])
            sections.append("\n\n")
        
        if "p_and_l_assessment" in report:
            sections.append("## P&L Assessment\n\n")
            sections.append("```json\n")
            sections.append(json.dumps(report["p_and_l_assessment"], indent=2))
            sections.append("\n```\n\n")
        
        return "".join(sections)
    
    def _format_stage_markdown(self, stage: str, issues: list) -> str:
        """Format stage report as Markdown"""
        sections = []
        
        sections.append(f"# {stage.title()} Editor Report\n\n")
        sections.append(f"**Total Issues Found:** {len(issues)}\n\n")
        
        # Group by severity
        by_severity = {}
        for issue in issues:
            severity = issue.get("severity", "unknown")
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(issue)
        
        for severity in ["critical", "major", "minor"]:
            if severity in by_severity:
                sections.append(f"## {severity.upper()} Issues ({len(by_severity[severity])})\n\n")
                
                for issue in by_severity[severity]:
                    sections.append(f"### {issue.get('category', 'Unknown').title()}\n")
                    sections.append(f"**Location:** {issue.get('location', 'Unknown')}\n\n")
                    sections.append(f"**Description:** {issue.get('description', 'N/A')}\n\n")
                    sections.append(f"**Suggestion:** {issue.get('suggestion', 'N/A')}\n\n")
                    sections.append("---\n\n")
        
        return "".join(sections)

    def compare_versions(self, manuscript_id: str, v1: str, v2: str) -> List[Dict[str, Any]]:
        """
        Compare two versions of a manuscript and return line-by-line diffs.
        
        Args:
            manuscript_id: Project ID
            v1: First version name (e.g., 'original', 'current', 'acquisitions')
            v2: Second version name
            
        Returns:
            List of diff objects: [{'type': 'added|removed|unchanged', 'content': 'line text'}]
        """
        text1 = self.get_manuscript_version(manuscript_id, v1)
        text2 = self.get_manuscript_version(manuscript_id, v2)
        
        if text1 is None:
            text1 = ""
        if text2 is None:
            text2 = ""
            
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        
        diff = difflib.ndiff(lines1, lines2)
        changes = []
        
        for line in diff:
            if line.startswith('  '):
                changes.append({'type': 'unchanged', 'content': line[2:]})
            elif line.startswith('- '):
                changes.append({'type': 'removed', 'content': line[2:]})
            elif line.startswith('+ '):
                changes.append({'type': 'added', 'content': line[2:]})
            # ? lines are hints, we skip them for simple display
            
        return changes
