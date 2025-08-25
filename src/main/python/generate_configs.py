#!/usr/bin/env python3
"""
Configuration file generator for eta and rho parameter studies.

This script generates all configuration files needed for systematic parameter studies
based on the ranges used in Vicsek model literature.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

def create_eta_configs(base_config: Dict[str, Any], eta_values: List[float], 
                      runs_per_eta: int, output_dir: str, expected_n: int = 1000) -> None:
    """Generate configuration files for eta (noise) study."""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generating eta study configs in {output_dir}")
    
    for eta in eta_values:
        for run in range(1, runs_per_eta + 1):
            config = base_config.copy()
            config["noise"] = eta
            
            # Adjust particle count based on density and box size
            # For eta study: maintain density rho = 2.0
            rho = expected_n / (base_config["l"] ** 2);
            L = config["l"]
            config["n"] = int(rho * L * L)
            
            filename = f"eta_{eta:.1f}_run_{run}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(config, f, indent=2)
    
    print(f"✓ Generated {len(eta_values) * runs_per_eta} eta study configurations")

def create_rho_configs(base_config: Dict[str, Any], rho_values: List[float], 
                      runs_per_rho: int, output_dir: str) -> None:
    """Generate configuration files for rho (density) study."""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generating rho study configs in {output_dir}")
    
    for rho in rho_values:
        for run in range(1, runs_per_rho + 1):
            config = base_config.copy()
            
            # Calculate particle count based on density
            L = config["l"]
            config["n"] = int(rho * L * L)
            
            # For rho study: fix noise at eta = 1.0
            config["noise"] = 1.0
            
            filename = f"rho_{rho:.1f}_run_{run}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(config, f, indent=2)
    
    print(f"✓ Generated {len(rho_values) * runs_per_rho} rho study configurations")

def main():
    """Generate all configuration files for parameter studies."""
    
    # Base configuration (common parameters)
    base_config = {
        "r": 1.0,           # Interaction radius
        "v": 0.03,          # Particle velocity
        "l": 20.0,          # Box length
        "steps": 100000,      # Simulation steps
        "interaction": "average",
        "show_animation": False,
        "save_animation": False
    }
    
    # Parameter ranges based on Vicsek model literature
    eta_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.8, 1.2, 1.6, 2.0, 2.5, 3.0, 4.0, 5.0]  # Noise levels
    rho_values = []                 # Density values
    
    # fixed values 
    fixed_n = 1000 # fixed n for eta study
    fixed_noise = 1.0 # fixed noise for rho study
    
    runs_per_parameter = 5  # Number of independent runs per parameter value
    
    # Create output directories
    project_root = Path(__file__).parent.parent.parent.parent
    eta_configs_dir = project_root / "src" / "main" / "resources" / "c" / "eta_study" / "configs"
    rho_configs_dir = project_root / "src" / "main" / "resources" / "c" / "rho_study" / "configs"
    
    print("Generating configuration files for parameter studies...")
    print(f"Base configuration: {base_config}")
    print(f"Eta values: {eta_values}")
    print(f"Rho values: {rho_values}")
    print(f"Runs per parameter: {runs_per_parameter}")
    
    # Generate eta study configurations
    create_eta_configs(base_config, eta_values, runs_per_parameter, str(eta_configs_dir), expected_n=fixed_n)
    
    # Generate rho study configurations  
    create_rho_configs(base_config, rho_values, runs_per_parameter, str(rho_configs_dir))
    
    print("\n✓ All configuration files generated successfully!")
    print(f"Total files created: {(len(eta_values) + len(rho_values)) * runs_per_parameter}")
    print("\nNext steps:")
    print("1. Run simulations using the generated config files")
    print("2. Generate v_a evolution plots to determine steady-state start points")
    print("3. Run statistical analysis with user-defined start points")

if __name__ == "__main__":
    main()