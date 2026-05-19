
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
    # # ✅ Run analysis
    # analysis_crew = Crew(
    #     agents=[crew_instance.analysis_agent()],
    #     tasks=[crew_instance.analysis_task()],
    #     process=Process.sequential
    # )

    # analysis_result = analysis_crew.kickoff(inputs={
    #     "transactions": data
    # })

    # analysis_result = safe_parse(analysis_result)

    # # ✅ Run risk
    # risk_crew = Crew(
    #     agents=[crew_instance.risk_agent()],
    #     tasks=[crew_instance.risk_task()],
    #     process=Process.sequential
    # )

    # risk_result = risk_crew.kickoff(inputs={
    #     "profile": profile
    # })

    # risk_result = safe_parse(risk_result)

    # # ✅ Run advisory (NOW FIXED ✅)
    # advisory_crew = Crew(
    #     agents=[crew_instance.advisory_agent()],
    #     tasks=[crew_instance.advisory_task()],
    #     process=Process.sequential
    # )

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