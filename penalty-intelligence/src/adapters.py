from abc import ABC, abstractmethod
import pandas as pd
import os
from .intelligence import PenaltyIntelligenceEngine

class DataAdapter(ABC):
    @abstractmethod
    def fetch_penalties(self, goalkeeper_name: str = None) -> pd.DataFrame:
        pass

class StatsBombAdapter(DataAdapter):
    def fetch_penalties(self, goalkeeper_name: str = None) -> pd.DataFrame:
        df = PenaltyIntelligenceEngine().generate_demo_dataset()
        if goalkeeper_name: df = df[df['goalkeeper'] == goalkeeper_name]
        return df

class CSVAdapter(DataAdapter):
    def __init__(self, filepath: str):
        self.filepath = filepath
    def fetch_penalties(self, goalkeeper_name: str = None) -> pd.DataFrame:
        if not os.path.exists(self.filepath):
            df = PenaltyIntelligenceEngine().generate_demo_dataset()
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            df.to_csv(self.filepath, index=False)
        df = pd.read_csv(self.filepath)
        if goalkeeper_name: df = df[df['goalkeeper'] == goalkeeper_name]
        return df

class OptaAdapter(DataAdapter):
    def fetch_penalties(self, goalkeeper_name: str = None) -> pd.DataFrame:
        df = PenaltyIntelligenceEngine().generate_demo_dataset()
        if goalkeeper_name: df = df[df['goalkeeper'] == goalkeeper_name]
        return df
