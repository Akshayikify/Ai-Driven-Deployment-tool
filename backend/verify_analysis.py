from app.services.analysis import analysis_engine
import os
import shutil

def test_analysis_engine():
    test_dir = "app/temp/test_analysis"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)

    print("--- Testing Python/FastAPI Detection ---")
    with open(os.path.join(test_dir, "requirements.txt"), "w") as f:
        f.write("fastapi\nuvicorn\n")
    
    findings = analysis_engine.analyze_directory(test_dir)
    assert findings["language"] == "Python"
    assert findings["framework"] == "FastAPI"
    print("Python/FastAPI: PASS")

    print("\n--- Testing React/Vite Detection ---")
    shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    pkg_json = {
        "dependencies": {
            "react": "^18.0.0",
            "vite": "^4.0.0"
        }
    }
    import json
    with open(os.path.join(test_dir, "package.json"), "w") as f:
        json.dump(pkg_json, f)
    
    findings = analysis_engine.analyze_directory(test_dir)
    assert findings["language"] == "JavaScript/TypeScript"
    assert "React" in findings["framework"] or "Vite" in findings["framework"]
    print("React/Vite: PASS")

    shutil.rmtree(test_dir)
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_analysis_engine()
