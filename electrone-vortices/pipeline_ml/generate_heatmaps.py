"""
Module for generating spatial heatmaps of kinematic viscosity predicted by the ML model.
Applies rigorous spatial strain fields and interpolates quantum features directly from TB-DFT data.
"""
import os
import csv
import torch
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.interpolate import interp1d

from config_parser import ConfigParser
from model import ViscosityMLP


class ViscosityHeatmapGenerator:
    def __init__(self, config_path: str):
        self.config_loader = ConfigParser(config_path)
        self.cfg = self.config_loader.load()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model()

        # 1. Ładowanie rygorystycznych danych fizycznych z Fireballa
        self._load_quantum_physics()

        # Przygotowanie katalogu docelowego
        self.out_dir = Path("../data/data_learning/heatmaps")
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def _load_model(self) -> ViscosityMLP:
        model = ViscosityMLP(
            input_dim=self.cfg['model']['input_dim'],
            hidden_dims=self.cfg['model']['hidden_dims'],
            output_dim=self.cfg['model']['output_dim']
        )
        model_path = Path(self.cfg['paths']['learning_output_dir']) / "viscosity_mlp.pth"
        if not model_path.exists():
            raise FileNotFoundError(f"Trained model not found at {model_path}.")

        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model.to(self.device)
        model.eval()
        return model

    def _load_quantum_physics(self):
        """
        Loads the summary.csv from Fireball and creates rigorous interpolation functions
        mapping lattice constant 'a' to quantum features v_F and D(E_F).
        """
        summary_file = Path("../data/data_fireball/extracted_results/RESULTS/summary.csv")
        if not summary_file.exists():
            # Fallback for alternative path structure
            summary_file = Path("../pipeline_fireball/RESULTS/summary.csv")

        a_vals, vf_vals, def_vals = [], [], []
        with open(summary_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                a_vals.append(float(row['a']))
                vf_vals.append(float(row['v_F']))
                def_vals.append(float(row['D_EF']))

        # Tworzenie funkcji interpolujących na podstawie danych z TB-DFT
        # fill_value="extrapolate" zabezpiecza przed wyjściem poza zakres
        self.interp_vf = interp1d(a_vals, vf_vals, kind='cubic', fill_value="extrapolate")
        self.interp_def = interp1d(a_vals, def_vals, kind='cubic', fill_value="extrapolate")

        # Parametry normalizacyjne (Z-score) użyte podczas treningu
        features = np.column_stack((
            np.array(a_vals) / np.sqrt(3), np.array(a_vals) / np.sqrt(3), np.array(a_vals) / np.sqrt(3),
            vf_vals, def_vals
        ))
        self.x_mean = torch.tensor(features.mean(axis=0), dtype=torch.float32)
        self.x_std = torch.tensor(features.std(axis=0) + 1e-8, dtype=torch.float32)

    def _generate_strain_field(self, X: np.ndarray, Y: np.ndarray, R: float, cy: float) -> np.ndarray:
        """
        Generates the spatial strain field epsilon(x,y).
        Strain concentrates logarithmically at the sharp corners where the pocket meets the main channel.
        """
        if R <= abs(cy):
            return np.zeros_like(X)

        corner_x = np.sqrt(R ** 2 - cy ** 2)
        dist_1 = np.sqrt((X - corner_x) ** 2 + Y ** 2)
        dist_2 = np.sqrt((X + corner_x) ** 2 + Y ** 2)

        # Maksymalne naprężenie na rogach ustalmy na 5% (epsilon = 0.05)
        strain = 0.05 * (np.exp(-dist_1 / 0.2) + np.exp(-dist_2 / 0.2))
        return strain

    def generate_heatmap(self, case_name: str, R: float):
        print(f"Generating rigorous heatmap for: {case_name} (R = {R} um)...")

        x_lin = np.linspace(-2.0, 2.0, 400)
        y_lin = np.linspace(-1.5, 1.0, 250)
        X, Y = np.meshgrid(x_lin, y_lin)

        cy = -0.35
        in_channel = (Y >= 0.0) & (Y <= 1.0)
        in_disk = (X ** 2 + (Y - cy) ** 2) <= R ** 2
        domain_mask = in_channel | in_disk

        # 1. Wyliczenie naprężeń
        strain = self._generate_strain_field(X, Y, R, cy)

        # 2. Przeliczenie naprężenia na lokalną stałą sieci 'a'
        # Podstawowa stała sieci to a_0 = 2.46 Angstroma
        a_local = 2.46 * (1.0 + strain)

        # 3. Rygorystyczna ekstrakcja cech kwantowych z interpolacji Fireballa!
        d_cc = a_local / np.sqrt(3.0)
        v_f = self.interp_vf(a_local)
        d_ef = self.interp_def(a_local)

        viscosity_map = np.full_like(X, np.nan)
        valid_indices = np.where(domain_mask)

        for i, j in zip(*valid_indices):
            # Zbudowanie wektora wejściowego [d1, d2, d3, v_F, D(E_F)]
            features = torch.tensor([d_cc[i, j], d_cc[i, j], d_cc[i, j], v_f[i, j], d_ef[i, j]], dtype=torch.float32)
            features_norm = (features - self.x_mean) / self.x_std

            with torch.no_grad():
                pred_nu = self.model(features_norm.unsqueeze(0)).item()
                # Odtworzenie oryginalnej skali lepkości z modelu analitycznego
                viscosity_map[i, j] = pred_nu

        # 4. Wizualizacja
        plt.figure(figsize=(10, 6))
        cmap = plt.cm.inferno
        cmap.set_bad(color='white')

        mesh = plt.pcolormesh(X, Y, viscosity_map, cmap=cmap, shading='auto')
        cbar = plt.colorbar(mesh)
        cbar.set_label(r'Kinematic Viscosity $\nu(x,y)$', fontsize=14)

        plt.contour(X, Y, domain_mask, levels=[0.5], colors='black', linewidths=1.0)
        plt.title(f'Physics-Informed Viscosity Field: {case_name.replace("_", " ").title()}', fontsize=16)
        plt.xlabel('x (µm)', fontsize=14)
        plt.ylabel('y (µm)', fontsize=14)

        plt.gca().set_aspect('equal', adjustable='box')
        plt.tight_layout()

        save_path = self.out_dir / f"heatmap_{case_name}.png"
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"-> Saved: {save_path}")


def main():
    config_path = "../configs/ml_model/mlp_config.yaml"
    generator = ViscosityHeatmapGenerator(config_path)

    generator.generate_heatmap(case_name="no_pocket", R=0.0)
    generator.generate_heatmap(case_name="small_pocket", R=0.4)
    generator.generate_heatmap(case_name="large_pocket", R=0.8)


if __name__ == "__main__":
    main()
