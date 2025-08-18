import numpy as np
import os
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class StatisticsSummary:
    parameter_value: float
    mean_va: float
    std_va: float
    stderr_va: float
    runs_count: int
    steady_state_mean: float
    steady_state_std: float

class ParameterStudyAnalyzer:
    def __init__(self, base_path: str = "results", steady_state_fraction: float = 0.2):
        self.base_path = base_path
        self.steady_state_fraction = steady_state_fraction
    
    def analyze_eta_study(self) -> Dict[float, StatisticsSummary]:
        """Analyze eta (noise) parameter study results."""
        eta_path = os.path.join(self.base_path, "eta_study", "raw_data")
        return self._analyze_parameter_study(eta_path, "eta")
    
    def analyze_rho_study(self) -> Dict[float, StatisticsSummary]:
        """Analyze rho (density) parameter study results."""
        rho_path = os.path.join(self.base_path, "rho_study", "raw_data")
        return self._analyze_parameter_study(rho_path, "rho")
    
    def _analyze_parameter_study(self, study_path: str, parameter_type: str) -> Dict[float, StatisticsSummary]:
        """Generic method to analyze parameter study results."""
        if not os.path.exists(study_path):
            print(f"Warning: Study path {study_path} does not exist")
            return {}
        
        # Group runs by parameter value
        parameter_runs = {}
        pattern = rf"{parameter_type}_(\d+\.?\d*)_run_(\d+)"
        
        for run_dir in os.listdir(study_path):
            match = re.match(pattern, run_dir)
            if match:
                param_value = float(match.group(1))
                run_number = int(match.group(2))
                
                if param_value not in parameter_runs:
                    parameter_runs[param_value] = []
                
                order_file = self._find_order_parameter_file(os.path.join(study_path, run_dir))
                if order_file:
                    parameter_runs[param_value].append(order_file)
        
        # Analyze each parameter value
        results = {}
        for param_value, order_files in parameter_runs.items():
            print(f"Analyzing {parameter_type} = {param_value} with {len(order_files)} runs")
            results[param_value] = self._analyze_parameter_value(param_value, order_files)
        
        return results
    
    def _find_order_parameter_file(self, run_dir: str) -> str:
        """Find the order parameter file in a run directory."""
        order_dir = os.path.join(run_dir, "order_parameter")
        if not os.path.exists(order_dir):
            return None
        
        for file in os.listdir(order_dir):
            if file.endswith(".txt"):
                return os.path.join(order_dir, file)
        return None
    
    def _analyze_parameter_value(self, param_value: float, order_files: List[str]) -> StatisticsSummary:
        """Analyze multiple runs for a single parameter value."""
        all_va_values = []
        steady_state_values = []
        
        for order_file in order_files:
            va_series = self._load_order_parameter_series(order_file)
            if va_series is not None and len(va_series) > 0:
                all_va_values.extend(va_series)
                
                # Extract steady-state portion (skip first 20% of simulation)
                skip_steps = int(len(va_series) * self.steady_state_fraction)
                steady_state = va_series[skip_steps:] if skip_steps < len(va_series) else va_series
                steady_state_values.extend(steady_state)
        
        if not all_va_values:
            print(f"Warning: No valid data found for parameter {param_value}")
            return StatisticsSummary(param_value, 0.0, 0.0, 0.0, 0, 0.0, 0.0)
        
        all_va_array = np.array(all_va_values)
        steady_state_array = np.array(steady_state_values) if steady_state_values else all_va_array
        
        mean_va = np.mean(all_va_array)
        std_va = np.std(all_va_array)
        stderr_va = std_va / np.sqrt(len(all_va_array))
        
        steady_mean = np.mean(steady_state_array)
        steady_std = np.std(steady_state_array)
        
        return StatisticsSummary(
            parameter_value=param_value,
            mean_va=mean_va,
            std_va=std_va,
            stderr_va=stderr_va,
            runs_count=len(order_files),
            steady_state_mean=steady_mean,
            steady_state_std=steady_std
        )
    
    def _load_order_parameter_series(self, filepath: str) -> np.ndarray:
        """Load order parameter time series from file."""
        try:
            with open(filepath, 'r') as f:
                values = [float(line.strip()) for line in f if line.strip()]
            return np.array(values) if values else None
        except (FileNotFoundError, ValueError) as e:
            print(f"Error loading {filepath}: {e}")
            return None
    
    def save_processed_results(self, results: Dict[float, StatisticsSummary], 
                             output_file: str, parameter_name: str):
        """Save processed statistics to file."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(f"# {parameter_name} vs Order Parameter Statistics\n")
            f.write(f"# {parameter_name}\tMean_va\tStd_va\tStderr_va\tRuns\tSteady_mean\tSteady_std\n")
            
            for param_value in sorted(results.keys()):
                stats = results[param_value]
                f.write(f"{stats.parameter_value:.3f}\t{stats.mean_va:.6f}\t"
                       f"{stats.std_va:.6f}\t{stats.stderr_va:.6f}\t{stats.runs_count}\t"
                       f"{stats.steady_state_mean:.6f}\t{stats.steady_state_std:.6f}\n")

if __name__ == "__main__":
    analyzer = ParameterStudyAnalyzer()
    
    # Analyze eta study
    print("Analyzing eta (noise) study...")
    eta_results = analyzer.analyze_eta_study()
    analyzer.save_processed_results(
        eta_results, 
        "results/eta_study/processed/eta_statistics.txt", 
        "eta"
    )
    
    # Analyze rho study  
    print("Analyzing rho (density) study...")
    rho_results = analyzer.analyze_rho_study()
    analyzer.save_processed_results(
        rho_results,
        "results/rho_study/processed/rho_statistics.txt",
        "rho"
    )
    
    print("Statistical analysis completed!")