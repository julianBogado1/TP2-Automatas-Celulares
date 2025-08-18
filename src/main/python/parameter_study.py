#!/usr/bin/env python3
"""
Master script for running complete parameter study (Inciso c).

This script orchestrates the entire workflow:
1. Compile and run Java batch simulations  
2. Process statistical analysis of results
3. Generate publication-quality plots
4. Create summary report
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def run_command(command, description, cwd=None):
    """Run a system command with error handling."""
    print(f"\nRunning: {description}")
    print(f"Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=True)
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(f"Return code: {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False

def check_java_installation():
    """Check if Java and Maven are installed."""
    print("Checking Java and Maven installation...")
    
    java_ok = run_command(["java", "--version"], "Java version check")
    maven_ok = run_command(["mvn", "--version"], "Maven version check")
    
    if not java_ok or not maven_ok:
        print("Error: Java 21+ and Maven are required for this study")
        print("Please install them and try again")
        return False
    
    return True

def compile_java_project():
    """Compile the Java project using Maven."""
    print_section("COMPILING JAVA PROJECT")
    
    project_root = Path(__file__).parent.parent.parent.parent
    print(f"Project root: {project_root}")
    print(f"pom.xml exists: {(project_root / 'pom.xml').exists()}")
    
    success = run_command(
        ["mvn", "compile"], 
        "Maven compile",
        cwd=project_root
    )
    
    if not success:
        print("Failed to compile Java project")
        return False
    
    print("✓ Java project compiled successfully")
    return True

def run_parameter_sweep():
    """Run the Java parameter sweep study."""
    print_section("RUNNING PARAMETER SWEEP SIMULATIONS")
    
    project_root = Path(__file__).parent.parent.parent.parent
    print(f"Parameter sweep project root: {project_root}")
    
    print("Starting parameter sweep (this may take several minutes)...")
    print("Progress will be shown for each parameter value...")
    
    start_time = time.time()
    
    success = run_command([
        "mvn", "exec:java",
        "-Dexec.mainClass=ar.edu.itba.sims.Inciso1c",
        "-Dexec.cleanupDaemonThreads=false"
    ], "Parameter sweep simulations", cwd=project_root)
    
    end_time = time.time()
    duration = end_time - start_time
    
    if not success:
        print("Failed to run parameter sweep")
        return False
    
    print(f"✓ Parameter sweep completed in {duration/60:.1f} minutes")
    return True

def run_statistical_analysis():
    """Run statistical analysis on simulation results."""
    print_section("STATISTICAL ANALYSIS")
    
    python_dir = Path(__file__).parent
    
    success = run_command([
        sys.executable, "statistics.py"
    ], "Statistical analysis", cwd=python_dir)
    
    if not success:
        print("Failed to run statistical analysis")
        return False
    
    print("✓ Statistical analysis completed")
    return True

def generate_plots():
    """Generate all parameter study plots."""
    print_section("GENERATING PLOTS")
    
    python_dir = Path(__file__).parent
    
    success = run_command([
        sys.executable, "curves.py"
    ], "Plot generation", cwd=python_dir)
    
    if not success:
        print("Failed to generate plots")
        return False
    
    print("✓ All plots generated successfully")
    return True

def create_summary_report():
    """Create a summary report of the study."""
    print_section("CREATING SUMMARY REPORT")
    
    report_content = f"""# Parameter Study Report (Inciso c)
Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Study Overview
This report summarizes the results of the off-lattice flocking model parameter study.

### Parameters Studied:
1. **Noise (η) Study**: Varied noise level from 0.0 to 5.0 (fixed density ρ = 2.0)
2. **Density (ρ) Study**: Varied density from 0.5 to 5.0 particles/unit² (fixed noise η = 1.0)

### Fixed Parameters:
- Box size (L): 20.0
- Interaction radius (R): 1.0  
- Velocity magnitude (v): 0.03
- Simulation steps: 1000
- Runs per parameter: 5

## Results Location:
- Raw simulation data: `results/eta_study/` and `results/rho_study/`
- Processed statistics: `results/*/processed/*.txt`
- Plots: `results/plots/`

## Key Files:
- `eta_vs_va.png`: Order parameter vs noise level
- `rho_vs_va.png`: Order parameter vs density  
- `combined_study.png`: Combined parameter study plots
- Statistical summaries in processed directories

## Interpretation:
The order parameter (va) measures the degree of collective alignment in the flock.
- va ≈ 0: Random motion (disordered phase)
- va ≈ 1: Perfect alignment (ordered phase)

Typical expectations:
- **Noise study**: Higher noise should decrease order parameter
- **Density study**: Higher density should increase order parameter (up to a point)

## Next Steps:
1. Examine plots for phase transitions
2. Compare with theoretical predictions
3. Analyze error bars for statistical significance
4. Consider additional parameter ranges if needed
"""

    try:
        report_path = "results/PARAMETER_STUDY_REPORT.md"
        os.makedirs("results", exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        print(f"✓ Summary report created: {report_path}")
        return True
        
    except Exception as e:
        print(f"Failed to create summary report: {e}")
        return False

def main():
    """Main workflow function."""
    print_section("INCISO C: PARAMETER STUDY WORKFLOW")
    print("This script will run the complete parameter study for the off-lattice flocking model")
    print("Estimated time: 10-30 minutes depending on your hardware")
    
    # Step 1: Check prerequisites
    if not check_java_installation():
        sys.exit(1)
    
    # Step 2: Compile Java project
    if not compile_java_project():
        sys.exit(1)
    
    # Step 3: Run parameter sweep
    if not run_parameter_sweep():
        sys.exit(1)
    
    # Step 4: Statistical analysis
    if not run_statistical_analysis():
        sys.exit(1)
    
    # Step 5: Generate plots
    if not generate_plots():
        sys.exit(1)
    
    # Step 6: Create summary report
    if not create_summary_report():
        sys.exit(1)
    
    # Final summary
    print_section("STUDY COMPLETED SUCCESSFULLY!")
    print("✓ Java simulations completed")
    print("✓ Statistical analysis completed") 
    print("✓ Plots generated")
    print("✓ Summary report created")
    print(f"\nResults available in: {os.path.abspath('results/')}")
    print("Check the plots in results/plots/ and the summary report.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStudy interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)