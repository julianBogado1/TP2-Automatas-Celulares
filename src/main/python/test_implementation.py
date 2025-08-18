#!/usr/bin/env python3
"""
Test script to validate the Inciso c implementation.

This script performs basic validation tests without running full simulations.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import statistics
        import curves
        from statistics import ParameterStudyAnalyzer, StatisticsSummary
        from curves import CurvePlotter
        import numpy as np
        import matplotlib.pyplot as plt
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_statistics_analyzer():
    """Test the statistics analyzer with mock data."""
    print("Testing statistics analyzer...")
    
    try:
        # Create temporary test directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock study structure
            eta_dir = os.path.join(temp_dir, "eta_study", "raw_data")
            os.makedirs(eta_dir)
            
            # Create mock run directory with order parameter file
            run_dir = os.path.join(eta_dir, "eta_1.0_run_1", "order_parameter")
            os.makedirs(run_dir)
            
            # Create mock order parameter data
            order_file = os.path.join(run_dir, "N-800_L-20.00_Ruido-1.00.txt")
            with open(order_file, 'w') as f:
                # Write mock time series data
                for i in range(100):
                    va = 0.5 + 0.3 * (i / 100)  # Mock increasing order parameter
                    f.write(f"{va:.6f}\n")
            
            # Test analyzer
            from statistics import ParameterStudyAnalyzer
            analyzer = ParameterStudyAnalyzer(temp_dir)
            
            # This should not crash
            eta_results = analyzer.analyze_eta_study()
            
            print("✓ Statistics analyzer test passed")
            return True
            
    except Exception as e:
        print(f"✗ Statistics analyzer test failed: {e}")
        return False

def test_curve_plotter():
    """Test the curve plotter with mock data."""
    print("Testing curve plotter...")
    
    try:
        from curves import CurvePlotter
        from statistics import StatisticsSummary
        
        # Create mock results
        mock_results = {
            1.0: StatisticsSummary(1.0, 0.8, 0.1, 0.02, 5, 0.85, 0.08),
            2.0: StatisticsSummary(2.0, 0.6, 0.15, 0.03, 5, 0.65, 0.12),
            3.0: StatisticsSummary(3.0, 0.4, 0.2, 0.04, 5, 0.45, 0.18)
        }
        
        # Test data extraction
        plotter = CurvePlotter()
        param_values, va_means, va_errors = plotter._extract_plotting_data(mock_results)
        
        # Verify extraction
        assert len(param_values) == 3
        assert len(va_means) == 3
        assert len(va_errors) == 3
        assert param_values == [1.0, 2.0, 3.0]
        
        print("✓ Curve plotter test passed")
        return True
        
    except Exception as e:
        print(f"✗ Curve plotter test failed: {e}")
        return False

def test_java_compilation():
    """Test Java project compilation."""
    print("Testing Java compilation...")
    
    try:
        import subprocess
        project_root = Path(__file__).parent.parent.parent.parent
        print(f"Testing Maven in directory: {project_root}")
        print(f"pom.xml exists: {(project_root / 'pom.xml').exists()}")
        
        # Try to compile
        result = subprocess.run([
            "mvn", "compile", "-q"
        ], cwd=project_root, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✓ Java compilation successful")
            return True
        else:
            print(f"✗ Java compilation failed:")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Java compilation timed out")
        return False
    except FileNotFoundError:
        print("✗ Maven not found - please install Maven")
        return False
    except Exception as e:
        print(f"✗ Java compilation test failed: {e}")
        return False

def test_directory_structure():
    """Test that all necessary files exist."""
    print("Testing directory structure...")
    
    try:
        base_path = Path(__file__).parent
        project_root = base_path.parent.parent.parent
        
        required_files = [
            # Java files
            project_root / "src/main/java/ar/edu/itba/sims/Inciso1c.java",
            project_root / "src/main/java/ar/edu/itba/sims/Main.java",
            project_root / "src/main/java/ar/edu/itba/sims/InitialConditions.java",
            project_root / "pom.xml",
            
            # Python files  
            base_path / "statistics.py",
            base_path / "curves.py",
            base_path / "parameter_study.py",
            base_path / "requirements.txt"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(str(file_path))
        
        if missing_files:
            print("✗ Missing required files:")
            for file in missing_files:
                print(f"  - {file}")
            return False
        else:
            print("✓ All required files present")
            return True
            
    except Exception as e:
        print(f"✗ Directory structure test failed: {e}")
        return False

def run_all_tests():
    """Run all validation tests."""
    print("="*60)
    print("  INCISO C IMPLEMENTATION VALIDATION")
    print("="*60)
    
    tests = [
        ("Import Test", test_imports),
        ("Directory Structure", test_directory_structure), 
        ("Statistics Analyzer", test_statistics_analyzer),
        ("Curve Plotter", test_curve_plotter),
        ("Java Compilation", test_java_compilation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "="*60)
    print(f"VALIDATION SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Implementation ready to run.")
        print("\nTo run the full parameter study:")
        print("python parameter_study.py")
    else:
        print("❌ Some tests failed. Please fix issues before running full study.")
        return False
    
    print("="*60)
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)