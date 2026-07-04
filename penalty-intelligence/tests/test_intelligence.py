import pytest
import pandas as pd
from src.intelligence import PenaltyIntelligenceEngine
@pytest.fixture
def engine(): return PenaltyIntelligenceEngine()
def test_classify_zone(engine):
    assert engine.classify_zone(-3.0, 2.0) == "TL"
    assert engine.classify_zone(0, 0.5) == "BC"
def test_analyze_goalkeeper(engine):
    df = engine.generate_demo_dataset()
    p = engine.analyze_goalkeeper(df, "Alisson")
    assert p.name == "Alisson"
    assert p.total_penalties > 0
