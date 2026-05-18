from fastapi import FastAPI, UploadFile, Depends
import pandas as pd
from agents.crew import run_pipeline
from database import SessionLocal
from models import UserProfile

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

    result = run_pipeline(df.to_dict(), profile)
    return result


@app.post("/qa/")
async def qa(query: str):
    from agents.qa_agent import qa_agent
    return qa_agent.run(query)
