"""
Bible Version Manager - handles versioning like LibriScribe's BackupManager
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from core.models import SeriesBible


class BibleVersionManager:
    """Manages versions of Series Bible"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.versions_dir = self.project_dir / "bible_versions"
        self.versions_dir.mkdir(parents=True, exist_ok=True)
    
    def save_version(self, bible: SeriesBible, note: Optional[str] = None) -> str:
        """Save a new version"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_id = f"v_{timestamp}"
        
        version_file = self.versions_dir / f"{bible.manuscript_id}_{version_id}.json"
        
        version_data = bible.to_dict()
        version_data["_metadata"] = {
            "version_id": version_id,
            "note": note or "Auto-saved",
            "created_at": datetime.now().isoformat()
        }
        
        with open(version_file, 'w') as f:
            json.dump(version_data, f, indent=2)
        
        return version_id
    
    def list_versions(self, manuscript_id: str) -> List[dict]:
        """List all versions"""
        versions = []
        for file in self.versions_dir.glob(f"{manuscript_id}_v_*.json"):
            with open(file, 'r') as f:
                data = json.load(f)
                if "_metadata" in data:
                    versions.append(data["_metadata"])
        versions.sort(key=lambda v: v["created_at"], reverse=True)
        return versions
    
    def load_version(self, manuscript_id: str, version_id: str) -> SeriesBible:
        """Load a specific version"""
        file = self.versions_dir / f"{manuscript_id}_{version_id}.json"
        with open(file, 'r') as f:
            data = json.load(f)
            if "_metadata" in data:
                del data["_metadata"]
            return SeriesBible.from_dict(data)
    
    def restore_version(self, manuscript_id: str, version_id: str) -> SeriesBible:
        """Restore a previous version"""
        bible = self.load_version(manuscript_id, version_id)
        self.save_version(bible, note=f"Restored from {version_id}")
        return bible
