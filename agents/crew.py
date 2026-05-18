from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

import os
import yaml

# ✅ Load config properly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")

with open(os.path.join(CONFIG_DIR, "agents.yaml"), "r") as f:
    agents_config = yaml.safe_load(f)

with open(os.path.join(CONFIG_DIR, "tasks.yaml"), "r") as f:
    tasks_config = yaml.safe_load(f)

# =========================
# CREW CLASS
# =========================

@CrewBase
class FinancialAdvisorCrew:

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # -------------------------
    # AGENTS
    # -------------------------

    @agent
    def data_agent(self) -> Agent:
        return Agent(
            config = self.agents_config["data_agent"]
        )

    @agent
    def analysis_agent(self) -> Agent:
        return Agent(
           config = self.agents_config["analysis_agent"]
        )

    @agent
    def risk_agent(self) -> Agent:
        return Agent(
            config = self.agents_config["risk_agent"]
        )

    @agent
    def advisory_agent(self) -> Agent:
        return Agent(
            config = self.agents_config["advisory_agent"]
        )

    @agent
    def qa_agent(self) -> Agent:
        return Agent(
            config = self.agents_config["qa_agent"]
        )

    # -------------------------
    # TASKS
    # -------------------------

    @task
    def data_task(self) -> Task:
        return Task(
            config = self.tasks_config["data_task"]
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config = self.tasks_config["analysis_task"]
        )

    @task
    def risk_task(self) -> Task:
        return Task(
            config = self.tasks_config["risk_task"]
        )

    @task
    def advisory_task(self) -> Task:
        return Task(
            config = self.tasks_config["advisory_task"]
        )

    @task
    def qa_task(self) -> Task:
        return Task(
            config = self.tasks_config["qa_task"]
        )

    # -------------------------
    # CREW
    # -------------------------

    def crew(self) -> Crew:

        # ✅ manually create agents
        data_agent = self.data_agent()
        analysis_agent = self.analysis_agent()
        risk_agent = self.risk_agent()
        advisory_agent = self.advisory_agent()

        # ✅ manually create tasks
        data_task = self.data_task()
        analysis_task = self.analysis_task()
        risk_task = self.risk_task()
        advisory_task = self.advisory_task()

        return Crew(
            agents=[
                data_agent,
                analysis_agent,
                risk_agent,
                advisory_agent
            ],
            tasks=[
                data_task,
                analysis_task,
                risk_task,
                advisory_task
            ],
            process=Process.sequential,
            verbose=True
    )


# =========================
# RUN PIPELINE FUNCTION ✅
# =========================
def run_pipeline(data, profile):

    crew_instance = FinancialAdvisorCrew()

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

    # ✅ Run analysis
    analysis_crew = Crew(
        agents=[crew_instance.analysis_agent()],
        tasks=[crew_instance.analysis_task()],
        process=Process.sequential
    )

    analysis_result = analysis_crew.kickoff(inputs={
        "transactions": data
    })

    analysis_result = safe_parse(analysis_result)

    # ✅ Run risk
    risk_crew = Crew(
        agents=[crew_instance.risk_agent()],
        tasks=[crew_instance.risk_task()],
        process=Process.sequential
    )

    risk_result = risk_crew.kickoff(inputs={
        "profile": profile
    })

    risk_result = safe_parse(risk_result)

    # ✅ Run advisory (NOW FIXED ✅)
    advisory_crew = Crew(
        agents=[crew_instance.advisory_agent()],
        tasks=[crew_instance.advisory_task()],
        process=Process.sequential
    )

    advisory_result = advisory_crew.kickoff(inputs={
        "analysis": analysis_result,   # ✅ now dict
        "risk": risk_result           # ✅ now dict
    })

    advisory_result = safe_parse(advisory_result)

    # ✅ Final response
    return {
        "categories": analysis_result.get("categories", []),
        "values": analysis_result.get("values", []),
        "insights": analysis_result.get("insights", []),
        "risk_profile": risk_result.get("risk_profile", "Unknown"),
        "advice": advisory_result.get("advice", [])
    }