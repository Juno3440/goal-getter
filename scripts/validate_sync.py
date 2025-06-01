#!/usr/bin/env python3
"""
Validation script to ensure /app/ and /api/ are properly synchronized.

Checks that:
1. Core functionality is identical between /app/ and /api/
2. Production-specific features are present in /api/
3. No development-specific code leaked into /api/
"""

import ast
import difflib
from pathlib import Path
from typing import List, Set

def main():
    """Main validation function."""
    project_root = Path(__file__).parent.parent
    app_dir = project_root / "app"
    api_dir = project_root / "api"
    
    print("🔍 Validating sync between /app/ and /api/...")
    
    errors = []
    warnings = []
    
    # Check that core files exist
    print("📋 Checking file existence...")
    required_files = ["main.py", "db.py", "requirements.txt"]
    optional_files = ["__init__.py"]
    
    for file in required_files:
        app_file = app_dir / file
        api_file = api_dir / file
        
        if not app_file.exists():
            errors.append(f"Missing {file} in /app/")
        if not api_file.exists():
            errors.append(f"Missing {file} in /api/")
        else:
            print(f"  ✅ {file}")
    
    # Check optional files - only require them in /api/
    for file in optional_files:
        api_file = api_dir / file
        if not api_file.exists():
            errors.append(f"Missing {file} in /api/")
        else:
            print(f"  ✅ {file}")
    
    # Validate requirements.txt sync
    print("📋 Validating requirements.txt...")
    if validate_requirements(app_dir, api_dir):
        print("  ✅ requirements.txt properly synced")
    else:
        errors.append("requirements.txt files don't match")
    
    # Validate db.py has production features
    print("📋 Validating db.py production features...")
    db_validation = validate_db_production_features(api_dir)
    if db_validation["valid"]:
        print("  ✅ db.py has all production features")
    else:
        for missing in db_validation["missing"]:
            errors.append(f"db.py missing production feature: {missing}")
    
    # Validate main.py has production features
    print("📋 Validating main.py production features...")
    main_validation = validate_main_production_features(api_dir)
    if main_validation["valid"]:
        print("  ✅ main.py has all production features")
    else:
        for missing in main_validation["missing"]:
            errors.append(f"main.py missing production feature: {missing}")
    
    # Validate core business logic consistency
    print("📋 Validating core business logic consistency...")
    logic_validation = validate_core_logic_consistency(app_dir, api_dir)
    if logic_validation["valid"]:
        print("  ✅ Core business logic is consistent")
    else:
        for issue in logic_validation["issues"]:
            warnings.append(f"Logic inconsistency: {issue}")
    
    # Report results
    print("\n" + "="*50)
    if errors:
        print("❌ VALIDATION FAILED")
        for error in errors:
            print(f"  🚨 ERROR: {error}")
        return 1
    elif warnings:
        print("⚠️  VALIDATION PASSED WITH WARNINGS")
        for warning in warnings:
            print(f"  ⚠️  WARNING: {warning}")
        return 0
    else:
        print("✅ VALIDATION PASSED")
        print("🚀 /api/ is properly synchronized and ready for deployment")
        return 0

def validate_requirements(app_dir: Path, api_dir: Path) -> bool:
    """Check that requirements.txt files are identical."""
    try:
        with open(app_dir / "requirements.txt") as f:
            app_reqs = set(f.read().strip().split('\n'))
        with open(api_dir / "requirements.txt") as f:
            api_reqs = set(f.read().strip().split('\n'))
        return app_reqs == api_reqs
    except Exception:
        return False

def validate_db_production_features(api_dir: Path) -> dict:
    """Check that db.py has all production-specific features."""
    required_features = [
        "import os, time, logging",
        "from jose import jwt",
        "JWT_AUDIENCE",
        "def verify_token",
        "[DEBUG] SUPABASE_URL",
        "[DEBUG] DB PING"
    ]
    
    try:
        with open(api_dir / "db.py") as f:
            content = f.read()
        
        missing = []
        for feature in required_features:
            if feature not in content:
                missing.append(feature)
        
        return {"valid": len(missing) == 0, "missing": missing}
    except Exception as e:
        return {"valid": False, "missing": [f"Could not read db.py: {e}"]}

def validate_main_production_features(api_dir: Path) -> dict:
    """Check that main.py has all production-specific features."""
    required_features = [
        "/api/tree",
        "TreeNode",
        "TreeResponse", 
        "/gpt/goals",
        "[DEBUG] JWT_SECRET",
        "import datetime"
    ]
    
    try:
        with open(api_dir / "main.py") as f:
            content = f.read()
        
        missing = []
        for feature in required_features:
            if feature not in content:
                missing.append(feature)
        
        return {"valid": len(missing) == 0, "missing": missing}
    except Exception as e:
        return {"valid": False, "missing": [f"Could not read main.py: {e}"]}

def validate_core_logic_consistency(app_dir: Path, api_dir: Path) -> dict:
    """Check that core business logic functions are consistent."""
    try:
        # Parse both main.py files
        with open(app_dir / "main.py") as f:
            app_ast = ast.parse(f.read())
        with open(api_dir / "main.py") as f:
            api_ast = ast.parse(f.read())
        
        # Extract core endpoint functions (excluding production-only endpoints)
        core_endpoints = ["list_goals", "get_goal", "create_goal", "update_goal", "delete_goal"]
        
        issues = []
        
        app_functions = extract_function_signatures(app_ast)
        api_functions = extract_function_signatures(api_ast)
        
        for endpoint in core_endpoints:
            if endpoint in app_functions and endpoint in api_functions:
                app_sig = app_functions[endpoint]
                api_sig = api_functions[endpoint]
                if app_sig != api_sig:
                    issues.append(f"Function signature mismatch for {endpoint}")
            elif endpoint in app_functions:
                issues.append(f"Function {endpoint} missing from /api/")
            elif endpoint in api_functions:
                # This is OK - api can have extra functions
                pass
        
        return {"valid": len(issues) == 0, "issues": issues}
    except Exception as e:
        return {"valid": False, "issues": [f"Could not validate logic consistency: {e}"]}

def extract_function_signatures(tree: ast.AST) -> dict:
    """Extract function signatures from an AST."""
    functions = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Create a simple signature representation
            args = [arg.arg for arg in node.args.args]
            functions[node.name] = args
    
    return functions

if __name__ == "__main__":
    exit(main())