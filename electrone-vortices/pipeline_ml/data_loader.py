"""
Module for data extraction, preprocessing, and dataset generation.
Builds the PyTorch Dataset for the Machine Learning model.
"""
import tarfile
import logging
import torch
import numpy as np
from pathlib import Path
from typing import Tuple
from torch.utils.data import Dataset

class GrapheneFireballDataset(Dataset):
    def __init__(self, archive_path: str, extract_dir: str):
        self.archive_path = Path(archive_path)
        self.extract_dir = Path(extract_dir)

        self.features = None
        self.targets = None

        self._prepare_data()

    def _prepare_data(self) -> None:
        self._extract_archive()
        self._parse_files()
        self._normalize_features()

    def _extract_archive(self) -> None:
        if self.archive_path.exists() and not self.extract_dir.exists():
            self.extract_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"Extracting {self.archive_path} to {self.extract_dir}...")
            with tarfile.open(self.archive_path, "r:gz") as tar:
                tar.extractall(path=self.extract_dir)

    def _parse_files(self) -> None:
        logging.info("Parsing outputs to construct X and Y spaces...")

        # MOCK DATA (Zastąpić parsowaniem fizycznych plików w przyszłości)
        num_samples = 200
        x_list, y_list = [], []

        for _ in range(num_samples):
            d1, d2, d3 = np.random.normal(1.42, 0.05, 3)
            v_f = np.random.normal(1e6, 0.1e6)
            d_ef = np.random.normal(0.02, 0.005)

            x_list.append([d1, d2, d3, v_f, d_ef])
            nu = (v_f ** 2) * d_ef * 1e-12 # Model fizyczny
            y_list.append([nu])

        self.features = torch.tensor(x_list, dtype=torch.float32)
        self.targets = torch.tensor(y_list, dtype=torch.float32)

    def _normalize_features(self) -> None:
        """
        Z-score Normalization (x - mean) / std.
        Krytyczny krok matematyczny dla optymalizacji gradientowej (MLP).
        Ratuje model przed zdominowaniem przez prędkość Fermiego (10^6).
        """
        self.x_mean = self.features.mean(dim=0)
        self.x_std = self.features.std(dim=0) + 1e-8 # epsilon by uniknąć dzielenia przez 0

        self.features = (self.features - self.x_mean) / self.x_std
        logging.info("Features normalized successfully to mean=0, std=1.")

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.features[idx], self.targets[idx]
