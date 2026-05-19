from fastapi import FastAPI, UploadFile, Depends
import pandas as pd
from agents.crew import run_pipeline

app = FastAPI()

@app.post("/analyze/")
async def analyze(file: UploadFile, age:int, salary:float,
   investments:float, loans:float, goals:str):

    df = pd.read_csv(file.file)

    profile = {
        "age": age,
        "salary": salary,
        "investments": investments,
        "loans": loans,
        "goals": goals
    }

    result = run_pipeline(df.to_dict(orient="records"), profile)

    return result