"""
EditScribe Quick Start Script
Simplifies running the complete editorial workflow
"""

import requests
import json
import sys
import time
from pathlib import Path


class EditScribeClient:
    """Simple client for EditScribe API"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    def upload_manuscript(self, file_path):
        """Upload a manuscript file"""
        print(f"\n📤 Uploading manuscript: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/upload", files=files)
            
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"   Manuscript ID: {data['manuscript_id']}")
            print(f"   Word count: {data['word_count']:,}")
            return data['manuscript_id']
        else:
            print(f"❌ Upload failed: {response.text}")
            return None
    
    def run_stage(self, manuscript_id, stage_name):
        """Run a specific editorial stage"""
        print(f"\n🔄 Running {stage_name.upper()} stage...")
        
        endpoint_map = {
            'acquisitions': 'acquisitions',
            'developmental': 'developmental',
            'line': 'line',
            'copy': 'copy',
            'proof': 'proof',
            'cold-read': 'cold-read'
        }
        
        endpoint = endpoint_map.get(stage_name)
        if not endpoint:
            print(f"❌ Unknown stage: {stage_name}")
            return False
        
        response = requests.post(f"{self.base_url}/workflow/{manuscript_id}/{endpoint}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {stage_name.upper()} complete!")
            
            if 'total_issues' in data:
                print(f"   Issues found: {data['total_issues']}")
            
            return True
        else:
            print(f"❌ {stage_name.upper()} failed: {response.text}")
            return False
    
    def get_workflow_status(self, manuscript_id):
        """Get current workflow status"""
        response = requests.get(f"{self.base_url}/workflow/{manuscript_id}/status")
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_stage_result(self, manuscript_id, stage_name):
        """Get results from a completed stage"""
        response = requests.get(f"{self.base_url}/workflow/{manuscript_id}/{stage_name}/result")
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_complete_report(self, manuscript_id):
        """Get complete editorial report"""
        response = requests.get(f"{self.base_url}/projects/{manuscript_id}/complete-report")
        
        if response.status_code == 200:
            return response.json()
        return None


def print_banner():
    """Print welcome banner"""
    print("="*60)
    print("EditScribe - Professional Manuscript Editing System")
    print("="*60)


def run_complete_workflow(client, manuscript_id, include_cold_read=True):
    """Run the complete editorial workflow"""
    
    stages = [
        'acquisitions',
        'developmental',
        'line',
        'copy',
        'proof'
    ]
    
    if include_cold_read:
        stages.append('cold-read')
    
    print(f"\n📋 Running {len(stages)} editorial stages...")
    
    for stage in stages:
        success = client.run_stage(manuscript_id, stage)
        if not success:
            print(f"\n⚠️  Workflow stopped at {stage}")
            return False
        time.sleep(1)  # Brief pause between stages
    
    return True


def save_results(client, manuscript_id, output_dir):
    """Save all results to files"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print(f"\n💾 Saving results to: {output_path}")
    
    # Save complete report
    report = client.get_complete_report(manuscript_id)
    if report:
        with open(output_path / "complete_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        print(f"   ✅ Saved complete_report.json")
    
    # Save individual stage results
    stages = ['acquisitions', 'developmental', 'line', 'copy', 'proof', 'cold-read']
    
    for stage in stages:
        result = client.get_stage_result(manuscript_id, stage)
        if result:
            with open(output_path / f"{stage}_report.json", 'w') as f:
                json.dump(result, f, indent=2)
            print(f"   ✅ Saved {stage}_report.json")


def main():
    """Main entry point"""
    print_banner()
    
    # Check if manuscript file provided
    if len(sys.argv) < 2:
        print("\n❌ Usage: python quick_start.py <manuscript_file.docx>")
        print("\nExample:")
        print("   python quick_start.py my_novel.docx")
        print("\nOptions:")
        print("   --no-cold-read    Skip the optional Cold Reader stage")
        print("   --output-dir DIR  Save results to specific directory (default: ./results)")
        sys.exit(1)
    
    manuscript_file = sys.argv[1]
    include_cold_read = '--no-cold-read' not in sys.argv
    
    # Get output directory
    output_dir = "./results"
    if '--output-dir' in sys.argv:
        idx = sys.argv.index('--output-dir')
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]
    
    # Check file exists
    if not Path(manuscript_file).exists():
        print(f"\n❌ File not found: {manuscript_file}")
        sys.exit(1)
    
    # Initialize client
    client = EditScribeClient()
    
    # Upload manuscript
    manuscript_id = client.upload_manuscript(manuscript_file)
    if not manuscript_id:
        sys.exit(1)
    
    # Run workflow
    print(f"\n{'='*60}")
    print("Starting Editorial Workflow")
    print(f"{'='*60}")
    
    success = run_complete_workflow(client, manuscript_id, include_cold_read)
    
    if success:
        print(f"\n{'='*60}")
        print("✅ WORKFLOW COMPLETE!")
        print(f"{'='*60}")
        
        # Save results
        save_results(client, manuscript_id, output_dir)
        
        print(f"\n📊 Summary:")
        print(f"   Manuscript ID: {manuscript_id}")
        print(f"   Results saved to: {output_dir}")
        print(f"\n💡 Next steps:")
        print(f"   1. Review the complete_report.json")
        print(f"   2. Check individual stage reports for detailed feedback")
        print(f"   3. Review your manuscript in: backend/projects/{manuscript_id}/")
        
    else:
        print(f"\n❌ Workflow failed. Check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
