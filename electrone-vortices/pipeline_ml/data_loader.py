"""
Module for data extraction, preprocessing, and dataset generation.
Builds the PyTorch Dataset for the Machine Learning model.
"""
import tarfile
import logging
import csv
import torch
import numpy as np
from pathlib import Path
from typing import Tuple
from torch.utils.data import Dataset

class GrapheneFireballDataset(Dataset):
    def __init__(self, data_path: str):
        self.data_dir = Path(data_path)
        self.features = None
        self.targets = None
        self._prepare_data()

    def _prepare_data(self) -> None:
        # Zakładamy, że nie musimy już rozpakowywać, plik summary.csv jest generowany na bieżąco
        summary_file = self.data_dir / "summary.csv"

        if not summary_file.exists():
            raise FileNotFoundError(f"Could not find {summary_file}. Run run_fireball.sh first.")

        x_list, y_list = [], []

        with open(summary_file, 'r') as f:
            reader = csv.DictReader(f)

            for row in reader:
                a = float(row['a'])
                v_f = float(row['v_F'])
                d_ef = float(row['D_EF'])

                # Zniekształcenie wiązań (w modelu trójkątnym d = a / sqrt(3))
                d_cc = a / np.sqrt(3.0)

                # Obliczenie lepkości z fizycznego równania Chapmana-Enskoga
                # nu = C * v_F^4 * D(E_F). Usuwamy ekstremalne rzędy wielkości by ustabilizować PyTorch
                nu = (v_f**4) * d_ef * 1e-26

                x_list.append([d_cc, d_cc, d_cc, v_f, d_ef])
                y_list.append([nu])

        self.features = torch.tensor(x_list, dtype=torch.float32)
        self.targets = torch.tensor(y_list, dtype=torch.float32)
        logging.info(f"Loaded {len(self.features)} physical samples from DFT runs.")

        self._normalize_data()

    def _normalize_data(self) -> None:
        """
        Z-score Normalization for BOTH Features (X) and Targets (Y).
        This eliminates Exploding Gradients and keeps MSE ~ O(1).
        """
        self.x_mean = self.features.mean(dim=0)
        self.x_std = self.features.std(dim=0) + 1e-8
        self.features = (self.features - self.x_mean) / self.x_std

        self.y_mean = self.targets.mean(dim=0)
        self.y_std = self.targets.std(dim=0) + 1e-8
        self.targets = (self.targets - self.y_mean) / self.y_std

        logging.info("Features and Targets normalized successfully to mean=0, std=1.")

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.features[idx], self.targets[idx]
