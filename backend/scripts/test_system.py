#!/usr/bin/env python3
"""
Comprehensive system test for Synapse backend
Tests all components without requiring external services
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    try:
        from app.main import app
        print("✅ FastAPI app imports successfully")
        
        from app.models.model_manager import ModelManager
        print("✅ Model manager imports successfully")
        
        from app.services.youtube_service import YouTubeService
        print("✅ YouTube service imports successfully")
        
        from app.database.database import create_tables, SessionLocal
        print("✅ Database modules import successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing environment...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'DATABASE_URL', 'MODEL_CACHE_DIR', 
        'WHISPER_MODEL', 'SUMMARIZATION_MODEL'
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Missing")
            all_good = False
    
    return all_good

async def test_database():
    """Test database functionality"""
    print("\n🔍 Testing database...")
    
    try:
        from app.database.database import create_tables, SessionLocal
        
        # Test table creation
        await create_tables()
        print("✅ Database tables created successfully")
        
        # Test connection
        db = SessionLocal()
        db.close()
        print("✅ Database connection working")
        
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_youtube_service():
    """Test YouTube service"""
    print("\n🔍 Testing YouTube service...")
    
    try:
        from app.services.youtube_service import YouTubeService
        
        yt_service = YouTubeService()
        
        # Test URL validation
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
            ("https://youtu.be/dQw4w9WgXcQ", True),
            ("https://invalid-url.com", False),
        ]
        
        all_good = True
        for url, expected in test_cases:
            result = yt_service.validate_youtube_url(url)
            status = "✅" if result == expected else "❌"
            print(f"{status} URL validation: {url} -> {result}")
            if result != expected:
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"❌ YouTube service error: {e}")
        return False

def test_api_structure():
    """Test API structure and routes"""
    print("\n🔍 Testing API structure...")
    
    try:
        from app.main import app
        
        # Get all routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        # Check expected routes
        expected_routes = [
            "/",
            "/api/health", 
            "/api/process-video",
            "/api/job-status/{job_id}",
            "/api/job-results/{job_id}"
        ]
        
        all_good = True
        for expected in expected_routes:
            # Check if route exists (allowing for path parameters)
            route_exists = any(
                expected.replace("{job_id}", "") in route 
                for route in routes
            )
            
            status = "✅" if route_exists else "❌"
            print(f"{status} Route: {expected}")
            if not route_exists:
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"❌ API structure error: {e}")
        return False

def test_model_manager_init():
    """Test model manager initialization (without loading models)"""
    print("\n🔍 Testing model manager initialization...")
    
    try:
        from app.models.model_manager import ModelManager
        
        # Just test initialization, not model loading
        manager = ModelManager()
        print(f"✅ Model manager initialized with device: {manager.device}")
        
        # Test device detection
        if manager.device == "mps":
            print("✅ MPS (Metal Performance Shaders) detected - M1 optimization available")
        elif manager.device == "cuda":
            print("✅ CUDA detected")
        else:
            print("✅ CPU fallback available")
        
        return True
    except Exception as e:
        print(f"❌ Model manager error: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Synapse System Tests\n")
    
    tests = [
        ("Imports", test_imports),
        ("Environment", test_environment),
        ("Database", test_database),
        ("YouTube Service", test_youtube_service),
        ("API Structure", test_api_structure),
        ("Model Manager", test_model_manager_init),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        results[test_name] = result
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your system is ready to go!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

