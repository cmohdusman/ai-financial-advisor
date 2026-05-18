from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

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
        return Crew(
            agents=self.agents,   # auto-collected via @agent
            tasks=self.tasks,     # auto-collected via @task
            process=Process.sequential,
            verbose=True
        )
