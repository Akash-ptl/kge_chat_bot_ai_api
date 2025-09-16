#!/usr/bin/env python3
"""
Test script to verify the application can import without errors
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_app_imports():
    """Test that the main app can be imported without errors"""
    print("🔍 Testing Application Import...")

    try:
        from app.main import app
        print("✅ Main application import - SUCCESS")
        return True
    except Exception as e:
        print(f"❌ Main application import - FAILED: {e}")
        return False

def test_core_modules():
    """Test core module imports"""
    print("\n🔍 Testing Core Module Imports...")
    results = []

    # Test database manager
    try:
        from app.db_manager import db_manager
        print("✅ Database Manager - SUCCESS")
        results.append(True)
    except Exception as e:
        print(f"❌ Database Manager - FAILED: {e}")
        results.append(False)

    # Test config
    try:
        from app.config import settings
        print("✅ Config Settings - SUCCESS")
        results.append(True)
    except Exception as e:
        print(f"❌ Config Settings - FAILED: {e}")
        results.append(False)

    # Test models
    try:
        from app.models.app import AppModel
        from app.models.content import DocumentContent
        from app.models.guardrail import GuardrailModel
        print("✅ Model Imports - SUCCESS")
        results.append(True)
    except Exception as e:
        print(f"❌ Model Imports - FAILED: {e}")
        results.append(False)

    return all(results)

if __name__ == "__main__":
    print("🚀 DEPLOYMENT READINESS CHECK")
    print("=" * 50)

    # Test core modules first
    core_success = test_core_modules()

    # Test main app import
    app_success = test_app_imports()

    print("\n" + "=" * 50)
    if core_success and app_success:
        print("🎉 DEPLOYMENT READY - All imports successful!")
        sys.exit(0)
    else:
        print("❌ DEPLOYMENT ISSUES - Fix import errors before deploying")
        sys.exit(1)
