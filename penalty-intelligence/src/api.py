from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .intelligence import PenaltyIntelligenceEngine
from .adapters import CSVAdapter
import os

app = FastAPI(title="Penalty Intelligence API")
engine = PenaltyIntelligenceEngine()
data_path = os.path.join(os.path.dirname(__file__), "../data/demo_penalties.csv")
adapter = CSVAdapter(data_path)

class StrategyRequest(BaseModel):
    keeper_name: str
    shooter_foot: str
    pressure_context: str

@app.get("/keepers")
def list_keepers():
    return adapter.fetch_penalties()['goalkeeper'].unique().tolist()

@app.get("/profile/{keeper_name}")
def get_profile(keeper_name: str):
    df = adapter.fetch_penalties()
    if keeper_name not in df['goalkeeper'].unique(): raise HTTPException(status_code=404, detail="Not found")
    return engine.analyze_goalkeeper(df, keeper_name)

@app.post("/strategy")
def get_strategy(request: StrategyRequest):
    df = adapter.fetch_penalties()
    if request.keeper_name not in df['goalkeeper'].unique(): raise HTTPException(status_code=404, detail="Not found")
    profile = engine.analyze_goalkeeper(df, request.keeper_name)
    return engine.generate_shooter_strategy(profile, request.shooter_foot, request.pressure_context)
