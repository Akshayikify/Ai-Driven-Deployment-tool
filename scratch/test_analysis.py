import os
import sys
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.analysis import analysis_engine

def test_analysis():
    workspace = os.getcwd()
    print(f"Analyzing {workspace}...")
    findings = analysis_engine.analyze_directory(workspace)
    
    # Remove file_index for cleaner output
    if "file_index" in findings:
        del findings["file_index"]
        
    print(json.dumps(findings, indent=2))

if __name__ == "__main__":
    test_analysis()
