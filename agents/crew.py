
from crewai import Agent, Task, Crew, Process
import yaml

import os
print(os.getcwd())



with open("agents/configs.yaml", "r") as f:
    config = yaml.safe_load(f)

agents = {}

for name, details in config["agents"].items():
    agents[name] = Agent(
        role=details["role"],
        goal=details["goal"],
        backstory=details["backstory"],
        verbose=details.get("verbose", False)
    )



tasks = {}

for name, details in config["tasks"].items():
    tasks[name] = Task(
        description=details["description"],
        agent=agents[details["agent"]],
        expected_output=details["expected_output"]
    )


crew_name = "fianncial_analysis_crew"   # ✅ change this to any crew from YAML

crew_config = config["crews"][crew_name]

selected_agents = [agents[a] for a in crew_config["agents"]]
selected_tasks = [tasks[t] for t in crew_config["tasks"]]

## QA Crew
crew_qa_name = "fianncial_qa_crew"   # ✅ change this to any crew from YAML
crew_qa_config = config["crews"][crew_qa_name]
selected_qa_agents = [agents[a] for a in crew_qa_config["agents"]]
selected_qa_tasks = [tasks[t] for t in crew_qa_config["tasks"]]


# =========================
# RUN PIPELINE FUNCTION ✅
# =========================
def run_pipeline(data, profile):

    import json

    def safe_parse(x):
        # ✅ Convert CrewOutput → string → dict
        if hasattr(x, "raw"):
            try:
                return json.loads(x.raw)
            except:
                return {}
        
        if isinstance(x, str):
            try:
                return json.loads(x)
            except:
                return {}

        return x

    financial_crew = Crew(
    agents=selected_agents,
    tasks=selected_tasks,
    process=Process.sequential,  # or parallel
    verbose=crew_config.get("verbose", True)
)
    

    review_result = financial_crew.kickoff(inputs={
        "transactions": data,
        "profile": profile
    })

    review_result = safe_parse(review_result)

    # ✅ Final response
    return {
        "categories": review_result.get("categories", []),
        "values": review_result.get("values", []),
        "insights": review_result.get("insights", []),
        "risk_profile": review_result.get("risk_profile", "Unknown"),
        "advice": review_result.get("advice", [])
    }

def run_qa_query(query: str, profile: dict):
    financial_qa_crew = Crew(
    agents=selected_qa_agents,
    tasks=selected_qa_tasks,
    process=Process.sequential,  # or parallel
    verbose=crew_config.get("verbose", True)
    )

    query_result = financial_qa_crew.kickoff(inputs={
        "query": query,
        "age": profile["age"],
        "salary": profile["salary"],
        "investments": profile["investments"],
        "loans": profile["loans"],
        "analysis-data": profile["analysis"]

    })
    return query_result


