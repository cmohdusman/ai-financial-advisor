from fastapi import FastAPI, UploadFile, Depends
import pandas as pd
from agents.crew import run_pipeline
from agents.crew import run_qa_query

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
async def qa(user_input: dict):
    print(user_input)
    profile = {
        "age": user_input["age"],
        "salary": user_input["salary"],
        "investments": user_input["investments"],
        "loans": user_input["loans"],
        "analysis": user_input["analysis"]
    }
    return run_qa_query(user_input["query"], profile)