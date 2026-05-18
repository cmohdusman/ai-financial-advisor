from fastapi import FastAPI, UploadFile
import pandas as pd
from agents.crew import run_pipeline
from agents.crew import FinancialAdvisorCrew
from pydantic import BaseModel
import re
from backend.reward_engine import RewardEngine

reward_engine = RewardEngine()

class QueryRequest(BaseModel):
    query: str
    age: int
    salary: float
    investments: float
    loans: float
    analysis: dict 


class FeedbackRequest(BaseModel):
    query: str
    response: str
    correct_decision: bool
    compliant: bool
    fraud_detected: bool
    safe_reasoning: bool

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



@app.post("/qa/")
async def qa(request: QueryRequest):

    crew_instance = FinancialAdvisorCrew()
    from crewai import Crew, Process

    qa_crew = Crew(
        agents=[crew_instance.qa_agent()],
        tasks=[crew_instance.qa_task()],
        process=Process.sequential
    )

    result = qa_crew.kickoff(inputs={
        "query": request.query,
        "age": request.age,
        "salary": request.salary,
        "investments": request.investments,
        "loans": request.loans,
        "analysis": request.analysis 
    })

    # ✅ extract raw output
    if hasattr(result, "raw"):
        clean_response = result.raw
    else:
        clean_response = str(result)

    # ✅ FIX TEXT FORMATTING
        clean_response = clean_response.replace("$", " USD ")
        clean_response = clean_response.replace("*", "")
        clean_response = clean_response.replace("_", "")
        clean_response = clean_response.replace("`", "")
        clean_response = re.sub(r'\s+', ' ', clean_response)
        clean_response = clean_response.replace(". ", ".\n\n")

    return {"response": clean_response}


@app.post("/feedback/")
async def feedback(request: FeedbackRequest):

    # ✅ calculate reward
    reward = reward_engine.calculate_reward(request.dict())

    print("\n=== HUMAN FEEDBACK ===")
    print(request.dict())
    print("Reward Score:", reward)

    return {"reward": reward}
