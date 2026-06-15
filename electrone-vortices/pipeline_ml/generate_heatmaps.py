"""
Module for generating spatial heatmaps of kinematic viscosity predicted by the ML model.
Applies pseudo-physical strain fields based on device geometry (ETHZ experimental setup).
"""
import os
import torch
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Importy z Twojego pipeline_ml
from config_parser import ConfigParser
from model import ViscosityMLP


class ViscosityHeatmapGenerator:
    def __init__(self, config_path: str):
        """Initializes the generator by loading config and the trained model."""
        self.config_loader = ConfigParser(config_path)
        self.cfg = self.config_loader.load()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model()

        # Przygotowanie katalogu docelowego
        self.out_dir = Path("../data/data_learning/heatmaps")
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def _load_model(self) -> ViscosityMLP:
        """Instantiates the model and loads trained weights."""
        model = ViscosityMLP(
            input_dim=self.cfg['model']['input_dim'],
            hidden_dims=self.cfg['model']['hidden_dims'],
            output_dim=self.cfg['model']['output_dim']
        )
        model_path = Path(self.cfg['paths']['learning_output_dir']) / "viscosity_mlp.pth"

        if not model_path.exists():
            raise FileNotFoundError(f"Trained model not found at {model_path}. Run main.py first.")

        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model.to(self.device)
        model.eval()
        return model

    def _get_normalization_params(self):
        """
        Retrieves the exact normalization factors (mean, std) used during training.
        Since we mocked the data in data_loader.py, we mirror those statistics here.
        [d1, d2, d3, v_F, D(E_F)]
        """
        mean = torch.tensor([1.42, 1.42, 1.42, 1e6, 0.02], dtype=torch.float32)
        std = torch.tensor([0.05, 0.05, 0.05, 0.1e6, 0.005], dtype=torch.float32)
        return mean, std

    def _generate_strain_field(self, X: np.ndarray, Y: np.ndarray, R: float, cy: float) -> np.ndarray:
        """
        Generates a pseudo-physical spatial strain field.
        Strain concentrates at the sharp corners where the pocket meets the main channel.
        """
        if R <= abs(cy):
            return np.zeros_like(X)  # Brak połączenia (lub brak wnęki) -> brak naprężeń

        # Obliczanie pozycji rogów (przecięcie Y=0 z okręgiem kieszeni)
        corner_x = np.sqrt(R ** 2 - cy ** 2)

        # Odległość do najbliższego rogu
        dist_1 = np.sqrt((X - corner_x) ** 2 + Y ** 2)
        dist_2 = np.sqrt((X + corner_x) ** 2 + Y ** 2)

        # Zanik wykładniczy naprężeń od rogu (Długość relaksacji ~ 0.3 um)
        strain = 0.15 * (np.exp(-dist_1 / 0.3) + np.exp(-dist_2 / 0.3))
        return strain

    def generate_heatmap(self, case_name: str, R: float):
        """
        Generates and saves the kinematic viscosity heatmap for a specific geometry.

        Args:
            case_name (str): Label for the specific case (e.g., 'no_pocket').
            R (float): Radius of the disk pocket in micrometers.
        """
        print(f"Generating heatmap for: {case_name} (R = {R} um)...")

        # 1. Definicja przestrzeni geometrycznej (siatka punktów)
        x_lin = np.linspace(-2.0, 2.0, 400)
        y_lin = np.linspace(-1.5, 1.0, 250)
        X, Y = np.meshgrid(x_lin, y_lin)

        cy = -0.35  # Środek dysku (zgodnie z gurzhi_config)

        # 2. Maska geometrii (Kanał: Y w [0, 1] LUB Dysk: (X^2 + (Y-cy)^2 <= R^2))
        in_channel = (Y >= 0.0) & (Y <= 1.0)
        in_disk = (X ** 2 + (Y - cy) ** 2) <= R ** 2
        domain_mask = in_channel | in_disk

        # 3. Wyliczanie naprężeń i cech fizycznych
        strain = self._generate_strain_field(X, Y, R, cy)

        d1 = 1.42 * (1.0 + strain)
        d2 = 1.42 * (1.0 - 0.5 * strain)
        d3 = 1.42 * (1.0 - 0.5 * strain)
        v_f = 1e6 * (1.0 - 2.0 * strain)  # Spadek prędkości przez rozpraszanie na zniekształceniach
        d_ef = 0.02 * (1.0 + 5.0 * strain)  # Wzrost DOS w miejscu nagromadzenia ładunku

        # 4. Predykcja za pomocą modelu ML
        mean, std = self._get_normalization_params()
        viscosity_map = np.full_like(X, np.nan)

        # Przebiegamy tylko po punktach wewnątrz domeny fizycznej
        valid_indices = np.where(domain_mask)
        for i, j in zip(*valid_indices):
            features = torch.tensor([d1[i, j], d2[i, j], d3[i, j], v_f[i, j], d_ef[i, j]], dtype=torch.float32)
            features_norm = (features - mean) / std

            with torch.no_grad():
                pred_nu = self.model(features_norm.unsqueeze(0)).item()
                viscosity_map[i, j] = pred_nu

        # 5. Wizualizacja i zapis
        plt.figure(figsize=(10, 6))

        # Rysowanie mapy ciepła z paletą "inferno" dla uwydatnienia różnic lepkości
        cmap = plt.cm.inferno
        cmap.set_bad(color='white')  # Tło poza domeną jest białe

        mesh = plt.pcolormesh(X, Y, viscosity_map, cmap=cmap, shading='auto')
        cbar = plt.colorbar(mesh)
        cbar.set_label(r'Kinematic Viscosity $\nu(x,y)$', fontsize=14)

        # Rysowanie obramowania geometrii dla estetyki
        plt.contour(X, Y, domain_mask, levels=[0.5], colors='black', linewidths=1.0)

        plt.title(f'ML Predicted Viscosity Field: {case_name.replace("_", " ").title()}', fontsize=16)
        plt.xlabel('x (µm)', fontsize=14)
        plt.ylabel('y (µm)', fontsize=14)

        # Wymuszenie proporcji fizycznych 1:1 na osiach
        plt.gca().set_aspect('equal', adjustable='box')
        plt.tight_layout()

        save_path = self.out_dir / f"heatmap_{case_name}.png"
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"-> Saved: {save_path}")


def main():
    config_path = "../configs/ml_model/mlp_config.yaml"
    generator = ViscosityHeatmapGenerator(config_path)

    # Definicja 3 przypadków geometrycznych z pracy ETHZ
    generator.generate_heatmap(case_name="no_pocket", R=0.0)
    generator.generate_heatmap(case_name="small_pocket", R=0.4)
    generator.generate_heatmap(case_name="large_pocket", R=0.8)


if __name__ == "__main__":
    main()
