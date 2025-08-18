import matplotlib.pyplot as plt
import numpy as np
import os
from typing import Dict, Tuple, List
from statistics import ParameterStudyAnalyzer, StatisticsSummary

class CurvePlotter:
    def __init__(self, base_path: str = "results"):
        self.base_path = base_path
        self.analyzer = ParameterStudyAnalyzer(base_path)
        
        # Set up matplotlib for publication-quality plots
        plt.rcParams.update({
            'font.size': 12,
            'axes.linewidth': 1.2,
            'xtick.major.size': 6,
            'ytick.major.size': 6,
            'xtick.minor.size': 4,
            'ytick.minor.size': 4,
            'legend.frameon': True,
            'legend.fancybox': True,
            'legend.shadow': True
        })
    
    def plot_eta_vs_va(self, save_path: str = None, show: bool = True):
        """Plot noise (η) vs order parameter (va) curve."""
        print("Generating η vs va curve...")
        
        eta_results = self.analyzer.analyze_eta_study()
        if not eta_results:
            print("No eta study results found")
            return
        
        # Extract data for plotting
        eta_values, va_means, va_errors = self._extract_plotting_data(eta_results)
        
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Main curve with error bars
        ax.errorbar(eta_values, va_means, yerr=va_errors, 
                   marker='o', markersize=8, linewidth=2, capsize=5,
                   color='blue', ecolor='darkblue', capthick=2,
                   label='Order Parameter ($v_a$)')
        
        # Styling
        ax.set_xlabel('Noise Level (η)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Order Parameter ($v_a$)', fontsize=14, fontweight='bold')
        ax.set_title('Order Parameter vs Noise Level\n(Off-lattice Flocking Model)', 
                    fontsize=16, fontweight='bold', pad=20)
        
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=12)
        
        # Set reasonable axis limits
        ax.set_xlim(min(eta_values) - 0.2, max(eta_values) + 0.2)
        ax.set_ylim(-0.05, max(va_means) + 0.1)
        
        # Add parameter info text box
        textstr = f'Fixed: ρ = 2.0 particles/unit²\nL = 20.0, N = 800\nRuns per point: 5'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Eta curve saved to {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_rho_vs_va(self, save_path: str = None, show: bool = True):
        """Plot density (ρ) vs order parameter (va) curve."""
        print("Generating ρ vs va curve...")
        
        rho_results = self.analyzer.analyze_rho_study()
        if not rho_results:
            print("No rho study results found")
            return
        
        # Extract data for plotting
        rho_values, va_means, va_errors = self._extract_plotting_data(rho_results)
        
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Main curve with error bars
        ax.errorbar(rho_values, va_means, yerr=va_errors,
                   marker='s', markersize=8, linewidth=2, capsize=5,
                   color='red', ecolor='darkred', capthick=2,
                   label='Order Parameter ($v_a$)')
        
        # Styling
        ax.set_xlabel('Density (ρ) [particles/unit²]', fontsize=14, fontweight='bold')
        ax.set_ylabel('Order Parameter ($v_a$)', fontsize=14, fontweight='bold') 
        ax.set_title('Order Parameter vs Density\n(Off-lattice Flocking Model)',
                    fontsize=16, fontweight='bold', pad=20)
        
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=12)
        
        # Set reasonable axis limits
        ax.set_xlim(min(rho_values) - 0.2, max(rho_values) + 0.2)
        ax.set_ylim(-0.05, max(va_means) + 0.1)
        
        # Add parameter info text box
        textstr = f'Fixed: η = 1.0\nL = 20.0, R = 1.0\nRuns per point: 5'
        props = dict(boxstyle='round', facecolor='lightblue', alpha=0.5)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Rho curve saved to {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_combined_study(self, save_path: str = None, show: bool = True):
        """Plot both studies in a combined figure."""
        print("Generating combined parameter study plots...")
        
        eta_results = self.analyzer.analyze_eta_study()
        rho_results = self.analyzer.analyze_rho_study()
        
        if not eta_results and not rho_results:
            print("No study results found")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Eta plot
        if eta_results:
            eta_values, va_means_eta, va_errors_eta = self._extract_plotting_data(eta_results)
            ax1.errorbar(eta_values, va_means_eta, yerr=va_errors_eta,
                        marker='o', markersize=8, linewidth=2, capsize=5,
                        color='blue', ecolor='darkblue', capthick=2)
            
            ax1.set_xlabel('Noise Level (η)', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Order Parameter ($v_a$)', fontsize=12, fontweight='bold')
            ax1.set_title('(a) Order Parameter vs Noise', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.set_xlim(min(eta_values) - 0.2, max(eta_values) + 0.2)
            ax1.set_ylim(-0.05, max(va_means_eta) + 0.1)
        
        # Rho plot  
        if rho_results:
            rho_values, va_means_rho, va_errors_rho = self._extract_plotting_data(rho_results)
            ax2.errorbar(rho_values, va_means_rho, yerr=va_errors_rho,
                        marker='s', markersize=8, linewidth=2, capsize=5,
                        color='red', ecolor='darkred', capthick=2)
            
            ax2.set_xlabel('Density (ρ) [particles/unit²]', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Order Parameter ($v_a$)', fontsize=12, fontweight='bold')
            ax2.set_title('(b) Order Parameter vs Density', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3, linestyle='--')
            ax2.set_xlim(min(rho_values) - 0.2, max(rho_values) + 0.2)
            ax2.set_ylim(-0.05, max(va_means_rho) + 0.1)
        
        plt.suptitle('Off-lattice Flocking Model: Parameter Study Results', 
                    fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Combined plot saved to {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def _extract_plotting_data(self, results: Dict[float, StatisticsSummary]) -> Tuple[List[float], List[float], List[float]]:
        """Extract data for plotting from results dictionary."""
        param_values = sorted(results.keys())
        va_means = [results[p].steady_state_mean for p in param_values]
        va_errors = [results[p].steady_state_std for p in param_values]
        
        return param_values, va_means, va_errors
    
    def generate_all_plots(self):
        """Generate all plots and save them."""
        print("Generating all parameter study plots...")
        
        # Create output directories
        os.makedirs("results/plots", exist_ok=True)
        
        # Generate individual plots
        self.plot_eta_vs_va("results/plots/eta_vs_va.png", show=False)
        self.plot_rho_vs_va("results/plots/rho_vs_va.png", show=False)
        self.plot_combined_study("results/plots/combined_study.png", show=False)
        
        print("All plots generated and saved to results/plots/")

if __name__ == "__main__":
    plotter = CurvePlotter()
    plotter.generate_all_plots()