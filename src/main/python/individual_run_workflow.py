#!/usr/bin/env python3
"""
Individual Run Workflow for Parameter Studies.

This script implements the complete workflow:
1. Run simulation
2. Generate v_a evolution plot
3. Ask user for cutoff point
4. Calculate average from cutoff onwards
5. Store result for final aggregation

After processing all runs, generates final eta/rho vs v_a curves with error bars.
"""

import subprocess
import sys
import os
import glob
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import shutil

@dataclass
class RunResult:
    config_file: str
    parameter_type: str  # "eta" or "rho"
    parameter_value: float
    run_number: int
    cutoff_step: int
    steady_state_mean: float
    total_steps: int
    seed: int = None

class IndividualRunWorkflow:
    def __init__(self):
        self.results = []  # List[RunResult]
        self.results_file = "individual_run_results.json"
    
    def load_existing_results(self) -> bool:
        """Load previously processed results if available."""
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r') as f:
                    data = json.load(f)
                    self.results = [
                        RunResult(
                            config_file=r["config_file"],
                            parameter_type=r["parameter_type"],
                            parameter_value=r["parameter_value"], 
                            run_number=r["run_number"],
                            cutoff_step=r["cutoff_step"],
                            steady_state_mean=r["steady_state_mean"],
                            total_steps=r["total_steps"],
                            seed=r.get("seed")  # Handle backward compatibility
                        ) for r in data
                    ]
                print(f"✓ Loaded {len(self.results)} previous results")
                return True
            except Exception as e:
                print(f"Error loading existing results: {e}")
        return False
    
    def save_results(self):
        """Save current results to file."""
        try:
            data = [
                {
                    "config_file": r.config_file,
                    "parameter_type": r.parameter_type,
                    "parameter_value": r.parameter_value,
                    "run_number": r.run_number,
                    "cutoff_step": r.cutoff_step,
                    "steady_state_mean": r.steady_state_mean,
                    "total_steps": r.total_steps
                } for r in self.results
            ]
            with open(self.results_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Saved {len(self.results)} results")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def get_config_files(self) -> List[str]:
        """Get all configuration files."""
        project_root = Path(__file__).parent.parent.parent.parent
        config_files = []
        
        # Get eta_study config files (updated path)
        eta_pattern = str(project_root / "src" / "main" / "resources" / "c" / "eta_study" / "configs" / "*.json")
        eta_configs = glob.glob(eta_pattern)
        config_files.extend(eta_configs)
        
        # Get rho_study config files  
        rho_pattern = str(project_root / "src" / "main" / "resources" / "c" / "rho_study" / "configs" / "*.json")
        rho_configs = glob.glob(rho_pattern)
        config_files.extend(rho_configs)
        
        return sorted(config_files)
    
    def parse_config_info(self, config_file: str) -> Tuple[str, float, int]:
        """Extract parameter type, value, and run number from config filename."""
        filename = os.path.basename(config_file)
        
        if "eta_" in filename:
            # Format: eta_X.X_run_Y.json
            parts = filename.replace(".json", "").split("_")
            parameter_type = "eta"
            parameter_value = float(parts[1])
            run_number = int(parts[3])
        elif "rho_" in filename:
            # Format: rho_X.X_run_Y.json
            parts = filename.replace(".json", "").split("_")
            parameter_type = "rho"
            parameter_value = float(parts[1])
            run_number = int(parts[3])
        else:
            raise ValueError(f"Cannot parse config filename: {filename}")
        
        return parameter_type, parameter_value, run_number
    
    def run_simulation(self, config_file: str) -> bool:
        """Run single simulation for given config file."""
        project_root = Path(__file__).parent.parent.parent.parent
        jwd = project_root / "src" / "main" / "resources"
        config_rel_path = os.path.relpath(config_file, jwd)
        
        print(f"\n>>> Running simulation...")
        print(f">>> Config: {os.path.basename(config_file)}")
        
        # Run main simulation
        main_cmd = [
            "mvn.cmd", "exec:java",
            "-Dexec.mainClass=ar.edu.itba.sims.Main",
            f"-Dinput={config_rel_path}",
            "-Dexec.cleanupDaemonThreads=true"
        ]
        
        try:
            result = subprocess.run(main_cmd, cwd=project_root, capture_output=True, text=True, check=True)
            print("✓ Simulation completed")
        except subprocess.CalledProcessError as e:
            print(f"✗ Simulation failed: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            return False
        
        # Run observables calculation
        obs_cmd = [
            "mvn.cmd", "exec:java", 
            "-Dexec.mainClass=ar.edu.itba.sims.Observables",
            "-Dexec.args=v_a",
            "-Dexec.cleanupDaemonThreads=true"
        ]
        
        try:
            result = subprocess.run(obs_cmd, cwd=project_root, capture_output=True, text=True, check=True)
            print("✓ Order parameter calculated")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Observables calculation failed: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            return False
    
    def show_va_plot_and_get_cutoff(self, config_file: str) -> Optional[int]:
        """Show v_a evolution plot using existing orders.py and get user cutoff step."""
        python_dir = Path(__file__).parent
        project_root = Path(__file__).parent.parent.parent.parent
        order_param_dir = project_root / "src" / "main" / "resources" / "order_parameter"
        
        if not order_param_dir.exists():
            print("No order parameter directory found")
            return None
        
        # Find the order parameter file (should be the most recent one)
        order_files = list(order_param_dir.glob("*.txt"))
        if not order_files:
            print("No order parameter files found")
            return None
        
        order_file = order_files[0]  # Take the first (should be only one after single run)
        
        try:
            # Load v_a data for analysis
            with open(order_file, 'r') as f:
                va_values = [float(line.strip()) for line in f if line.strip()]
            
            if not va_values:
                print("No data in order parameter file")
                return None
            
            print(f"\n>>> Displaying v_a evolution plot using orders.py...")
            print(f">>> Config: {os.path.basename(config_file)}")
            
            # Run orders.py to display the plot
            try:
                result = subprocess.run([sys.executable, "orders.py"], 
                                      cwd=python_dir, 
                                      capture_output=False,  # Let it display the plot
                                      text=True)
                
                if result.returncode != 0:
                    print(f"Warning: orders.py returned code {result.returncode}")
            except Exception as e:
                print(f"Error running orders.py: {e}")
                return None
            
            # Get user input for cutoff
            print(f"\nOrder parameter evolution plot displayed via orders.py.")
            print(f"Available data points: {len(va_values)} (every 5th simulation step)")
            print()
            print("Choose the cutoff step where steady-state begins.")
            print("Enter the STEP NUMBER from the simulation, e.g., 500, 1000, 2500...")
            print("(This will be converted to the appropriate file line number)")
            
            while True:
                try:
                    cutoff_input = input("Cutoff step (simulation step, or 'skip' to skip this run): ").strip()
                    if cutoff_input.lower() == 'skip':
                        return None
                    
                    cutoff_step = int(cutoff_input)
                    cutoff_index = cutoff_step // 5  # Convert step to file line index
                    
                    if cutoff_step < 0:
                        print("Cutoff step must be non-negative")
                        continue
                    elif cutoff_index >= len(va_values):
                        max_step = (len(va_values) - 1) * 5
                        print(f"Cutoff step too large. Max available step: {max_step}")
                        continue
                    else:
                        # Show what the cutoff means
                        remaining_points = len(va_values) - cutoff_index
                        steady_state_data = va_values[cutoff_index:]
                        mean_va = np.mean(steady_state_data)
                        print(f"Using cutoff at step {cutoff_step} (file line {cutoff_index}):")
                        print(f"  - Remaining data points: {remaining_points}")
                        print(f"  - Steady-state mean: {mean_va:.6f}")
                        
                        confirm = input("Confirm this cutoff? [y/n]: ").lower().strip()
                        if confirm in ['y', 'yes']:
                            return cutoff_step
                        
                except ValueError:
                    print("Please enter a valid integer or 'skip'")
            
        except Exception as e:
            print(f"Error showing plot: {e}")
            return None
    
    def calculate_steady_state_average(self, config_file: str, cutoff_step: int) -> float:
        """Calculate steady-state average from cutoff step onwards."""
        project_root = Path(__file__).parent.parent.parent.parent
        order_param_dir = project_root / "src" / "main" / "resources" / "order_parameter"
        
        order_files = list(order_param_dir.glob("*.txt"))
        if not order_files:
            raise ValueError("No order parameter files found")
        
        order_file = order_files[0]
        
        with open(order_file, 'r') as f:
            va_values = [float(line.strip()) for line in f if line.strip()]
        
        cutoff_index = cutoff_step // 5  # Convert step to file line index
        if cutoff_index >= len(va_values):
            raise ValueError(f"Cutoff step {cutoff_step} (line {cutoff_index}) beyond data length {len(va_values)}")
        
        steady_state_data = va_values[cutoff_index:]
        return float(np.mean(steady_state_data))
    
    def process_single_run(self, config_file: str) -> bool:
        """Process a single simulation run through complete workflow."""
        try:
            # Parse config info
            param_type, param_value, run_number = self.parse_config_info(config_file)
            
            print(f"\n{'='*60}")
            print(f"PROCESSING: {param_type}={param_value}, run {run_number}")
            print(f"Config: {os.path.basename(config_file)}")
            print(f"{'='*60}")
            
            # Check if already processed
            existing = [r for r in self.results if r.config_file == config_file]
            if existing:
                print(f"✓ Already processed (cutoff: {existing[0].cutoff_step}, mean: {existing[0].steady_state_mean:.6f})")
                return True
            
            # Step 1: Run simulation
            if not self.run_simulation(config_file):
                print("Skipping due to simulation failure")
                return False
            
            # Step 2: Show plot and get cutoff
            cutoff_step = self.show_va_plot_and_get_cutoff(config_file)
            if cutoff_step is None:
                print("Skipping run (no cutoff specified)")
                return False
            
            # Step 3: Calculate average
            steady_state_mean = self.calculate_steady_state_average(config_file, cutoff_step)
            
            # Step 4: Store result (with seed from config)
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                config_seed = config_data.get("seed")
            
            result = RunResult(
                config_file=config_file,
                parameter_type=param_type,
                parameter_value=param_value,
                run_number=run_number,
                cutoff_step=cutoff_step,
                steady_state_mean=steady_state_mean,
                total_steps=config_data.get("steps", cutoff_step),
                seed=config_seed
            )
            
            self.results.append(result)
            self.save_results()
            
            print(f"✓ Processed successfully:")
            print(f"  Parameter: {param_type} = {param_value}")
            print(f"  Cutoff: {cutoff_step} steps")
            print(f"  Steady-state mean: {steady_state_mean:.6f}")
            
            return True
            
        except Exception as e:
            print(f"Error processing {config_file}: {e}")
            return False
    
    def generate_final_plots(self):
        """Generate separate final parameter study plots with error bars."""
        if not self.results:
            print("No results available for plotting")
            return
        
        # Group results by parameter type and value
        eta_groups = {}
        rho_groups = {}
        
        for result in self.results:
            if result.parameter_type == "eta":
                if result.parameter_value not in eta_groups:
                    eta_groups[result.parameter_value] = []
                eta_groups[result.parameter_value].append(result.steady_state_mean)
            else:  # rho
                if result.parameter_value not in rho_groups:
                    rho_groups[result.parameter_value] = []
                rho_groups[result.parameter_value].append(result.steady_state_mean)
        
        output_dir = Path("results/plots")
        output_dir.mkdir(parents=True, exist_ok=True)
        plot_files = []
        
        # Create separate Eta plot
        if eta_groups:
            eta_values = sorted(eta_groups.keys())
            eta_means = []
            eta_errors = []
            
            for eta in eta_values:
                values = eta_groups[eta]
                eta_means.append(np.mean(values))
                eta_errors.append(np.std(values, ddof=1) / np.sqrt(len(values)) if len(values) > 1 else 0)
            
            # Configure font sizes ≥20pt according to requirements
            plt.rcParams.update({
                'font.size': 20,
                'axes.labelsize': 22,
                'axes.titlesize': 24,
                'xtick.labelsize': 20,
                'ytick.labelsize': 20,
                'legend.fontsize': 20
            })
            
            fig, ax = plt.subplots(figsize=(12, 9))
            
            # Plot with clear data points and error bars
            ax.errorbar(eta_values, eta_means, yerr=eta_errors, 
                       fmt='o-', color='blue', capsize=8, capthick=3, linewidth=2, markersize=12,
                       ecolor='blue', elinewidth=3, alpha=0.8,
                       label='Datos experimentales')
            
            # Spanish axis labels with proper units
            ax.set_xlabel('Nivel de ruido eta (adimensional)', fontweight='bold')
            ax.set_ylabel('Parámetro de orden promedio va (adimensional)', fontweight='bold')
            ax.set_title('Modelo de Vicsek: Parámetro de Orden vs Nivel de Ruido', 
                        fontweight='bold', pad=25)
            
            # Grid styling
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=1)
            ax.set_ylim(bottom=0, top=1)
            ax.set_xlim(left=min(eta_values) - 0.1, right=max(eta_values) + 0.1)
            
            # Format axes with scientific notation when needed
            from matplotlib.ticker import ScalarFormatter
            formatter = ScalarFormatter(useMathText=True)
            formatter.set_scientific(True)
            formatter.set_powerlimits((-2, 2))
            
            # Add run counts with larger font
            for i, (eta, mean) in enumerate(zip(eta_values, eta_means)):
                n_runs = len(eta_groups[eta])
                ax.annotate(f'n={n_runs}', (eta, mean), xytext=(5, 15), 
                           textcoords='offset points', ha='center', fontsize=18,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
            
            # Add parameter info in Spanish with scientific notation
            total_runs = sum(len(values) for values in eta_groups.values())
            density_val = 2.0
            box_size = 20
            info_text = f'Parámetros fijos:\nDensidad ρ = {density_val:.1f} × 10⁰ (partículas/m²)\nTamaño de caja L = {box_size:.0f} × 10⁰ (m)\nTotal de corridas: {total_runs}'
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                   verticalalignment='top', horizontalalignment='left',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9),
                   fontsize=18)
            
            plt.tight_layout(pad=2.0)
            
            eta_filename = output_dir / "eta_vs_va_final.png"
            plt.savefig(eta_filename, dpi=300, bbox_inches='tight', facecolor='white')
            plt.show()
            plot_files.append(eta_filename)
            print(f"✓ Eta plot saved: {eta_filename}")
        
        # Create separate Rho plot
        if rho_groups:
            rho_values = sorted(rho_groups.keys())
            rho_means = []
            rho_errors = []
            
            for rho in rho_values:
                values = rho_groups[rho]
                rho_means.append(np.mean(values))
                rho_errors.append(np.std(values, ddof=1) / np.sqrt(len(values)) if len(values) > 1 else 0)
            
            # Configure font sizes ≥20pt according to requirements
            plt.rcParams.update({
                'font.size': 20,
                'axes.labelsize': 22,
                'axes.titlesize': 24,
                'xtick.labelsize': 20,
                'ytick.labelsize': 20,
                'legend.fontsize': 20
            })
            
            fig, ax = plt.subplots(figsize=(12, 9))
            
            # Plot with clear data points and error bars (square markers for distinction)
            ax.errorbar(rho_values, rho_means, yerr=rho_errors,
                       fmt='s-', color='red', capsize=8, capthick=3, linewidth=2, markersize=12,
                       ecolor='red', elinewidth=3, alpha=0.8,
                       label='Datos experimentales')
            
            # Spanish axis labels with proper MKS units
            ax.set_xlabel('Densidad rho (partículas/m²)', fontweight='bold')
            ax.set_ylabel('Parámetro de orden promedio va (adimensional)', fontweight='bold')
            ax.set_title('Modelo de Vicsek: Parámetro de Orden vs Densidad', 
                        fontweight='bold', pad=25)
            
            # Grid styling
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=1)
            ax.set_ylim(bottom=0, top=1)
            ax.set_xlim(left=min(rho_values) - 0.1, right=max(rho_values) + 0.1)
            
            # Format axes with scientific notation when needed
            from matplotlib.ticker import ScalarFormatter
            formatter = ScalarFormatter(useMathText=True)
            formatter.set_scientific(True)
            formatter.set_powerlimits((-2, 2))
            
            # Add run counts with larger font
            for i, (rho, mean) in enumerate(zip(rho_values, rho_means)):
                n_runs = len(rho_groups[rho])
                ax.annotate(f'n={n_runs}', (rho, mean), xytext=(5, 15), 
                           textcoords='offset points', ha='center', fontsize=18,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
            
            # Add parameter info in Spanish with scientific notation
            total_runs = sum(len(values) for values in rho_groups.values())
            noise_val = 1.0
            box_size = 20
            info_text = f'Parámetros fijos:\nRuido η = {noise_val:.1f} × 10⁰ (adimensional)\nTamaño de caja L = {box_size:.0f} × 10⁰ (m)\nTotal de corridas: {total_runs}'
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
                   verticalalignment='top', horizontalalignment='left',
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9),
                   fontsize=18)
            
            plt.tight_layout(pad=2.0)
            
            rho_filename = output_dir / "rho_vs_va_final.png"
            plt.savefig(rho_filename, dpi=300, bbox_inches='tight', facecolor='white')
            plt.show()
            plot_files.append(rho_filename)
            print(f"✓ Rho plot saved: {rho_filename}")
        
        # Print summary
        print(f"\n{'='*60}")
        print("FINAL RESULTS SUMMARY")
        print(f"{'='*60}")
        
        if eta_groups:
            print("ETA STUDY:")
            for eta in sorted(eta_groups.keys()):
                values = eta_groups[eta]
                mean_val = np.mean(values)
                std_val = np.std(values, ddof=1) if len(values) > 1 else 0
                stderr_val = std_val / np.sqrt(len(values)) if len(values) > 1 else 0
                print(f"  η = {eta:4.1f}: ⟨v_a⟩ = {mean_val:.4f} ± {stderr_val:.4f} (σ = {std_val:.4f}, n={len(values)})")
        
        if rho_groups:
            print("\nRHO STUDY:")
            for rho in sorted(rho_groups.keys()):
                values = rho_groups[rho]
                mean_val = np.mean(values)
                std_val = np.std(values, ddof=1) if len(values) > 1 else 0
                stderr_val = std_val / np.sqrt(len(values)) if len(values) > 1 else 0
                print(f"  ρ = {rho:4.1f}: ⟨v_a⟩ = {mean_val:.4f} ± {stderr_val:.4f} (σ = {std_val:.4f}, n={len(values)})")
        
        print(f"\nTotal processed runs: {len(self.results)}")
        print(f"Plots saved: {len(plot_files)}")
        for pf in plot_files:
            print(f"  - {pf}")
        print(f"{'='*60}")
        
        return plot_files
    
    def main_workflow(self):
        """Execute the complete workflow."""
        print("=== INDIVIDUAL RUN WORKFLOW ===")
        print("This workflow processes each simulation run individually:")
        print("1. Run simulation")
        print("2. Display v_a evolution plot")
        print("3. Ask for manual cutoff point")
        print("4. Calculate steady-state average")
        print("5. Generate final aggregated plots\n")
        
        # Load existing results
        self.load_existing_results()
        
        # Check if user wants to plot existing results instead of running simulations
        if self.results:
            print(f"\n📊 Found {len(self.results)} existing processed results")
            plot_now = input("Generate final plots from existing data? [y/n]: ").lower().strip()
            if plot_now in ['y', 'yes']:
                self.generate_final_plots()
                print("\n✅ Plotting complete. Exiting...")
                return
        
        # Get all config files
        config_files = self.get_config_files()
        
        if not config_files:
            print("No configuration files found!")
            print("Run generate_configs.py first to create them.")
            return
        
        print(f"Found {len(config_files)} configuration files to process")
        
        # Show what's already done
        processed_configs = {r.config_file for r in self.results}
        remaining_configs = [c for c in config_files if c not in processed_configs]
        
        if processed_configs:
            print(f"✓ Already processed: {len(processed_configs)} runs")
        if remaining_configs:
            print(f"⏳ Remaining: {len(remaining_configs)} runs")
        
        # Process remaining configs
        if remaining_configs:
            print(f"\nStarting automatic processing of {len(remaining_configs)} configurations...")
            
            for i, config_file in enumerate(remaining_configs, 1):
                print(f"\n>>> Run {i}/{len(remaining_configs)} <<<")
                
                success = self.process_single_run(config_file)
                if not success:
                    print("Run processing failed - continuing with next run...")
        
        # Generate final plots
        if self.results:
            print(f"\nGenerating final plots from {len(self.results)} processed runs...")
            generate_final = input("Generate final parameter study plots? [y/n]: ").lower().strip()
            if generate_final in ['y', 'yes']:
                self.generate_final_plots()
        else:
            print("No results available for final plots")


def main():
    """Main entry point."""
    try:
        workflow = IndividualRunWorkflow()
        workflow.main_workflow()
    except KeyboardInterrupt:
        print("\nWorkflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()