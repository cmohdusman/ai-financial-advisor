import os
import yaml
import json
import logging
from typing import Dict, Any

from crewai import Agent, Task, Crew, Process

# =========================
# LOGGING SETUP
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# =========================
# CONFIG LOADER
# =========================
def load_config(path: str = "agents/configs.yaml") -> Dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    if not config or "agents" not in config or "tasks" not in config:
        raise ValueError("Invalid config structure")

    logger.info("Config loaded successfully")
    return config


# =========================
# SAFE JSON PARSER
# =========================
def safe_parse(output: Any) -> Dict:
    try:
        if hasattr(output, "raw"):
            return json.loads(output.raw)

        if isinstance(output, str):
            return json.loads(output)

        if isinstance(output, dict):
            return output

    except Exception as e:
        logger.warning(f"Failed to parse output: {e}")

    return {}


# =========================
# AGENT BUILDER
# =========================
def build_agents(config: Dict) -> Dict[str, Agent]:
    agents = {}

    for name, details in config["agents"].items():
        try:
            agents[name] = Agent(
                role=details["role"],
                goal=details["goal"],
                backstory=details["backstory"],
                verbose=details.get("verbose", False)
            )
        except KeyError as e:
            logger.error(f"Missing agent config key: {e}")
            continue

    return agents


# =========================
# TASK BUILDER
# =========================
def build_tasks(config: Dict, agents: Dict[str, Agent]) -> Dict[str, Task]:
    tasks = {}

    for name, details in config["tasks"].items():
        try:
            agent_name = details["agent"]
            if agent_name not in agents:
                raise ValueError(f"Agent '{agent_name}' not found")

            tasks[name] = Task(
                description=details["description"],
                agent=agents[agent_name],
                expected_output=details["expected_output"]
            )

        except Exception as e:
            logger.error(f"Error building task '{name}': {e}")

    return tasks


# =========================
# CREW BUILDER
# =========================
def build_crew(crew_name: str, config: Dict, agents: Dict, tasks: Dict) -> Crew:
    if crew_name not in config["crews"]:
        raise ValueError(f"Crew '{crew_name}' not found in config")

    crew_cfg = config["crews"][crew_name]

    selected_agents = [agents[a] for a in crew_cfg["agents"] if a in agents]
    selected_tasks = [tasks[t] for t in crew_cfg["tasks"] if t in tasks]

    return Crew(
        agents=selected_agents,
        tasks=selected_tasks,
        process=Process.sequential,
        verbose=crew_cfg.get("verbose", True)
    )


# =========================
# INITIALIZATION (LOAD ONCE)
# =========================
config = load_config()

agents = build_agents(config)
tasks = build_tasks(config, agents)


ANALYSIS_CREW_NAME = "financial_analysis_crew"
QA_CREW_NAME = "financial_qa_crew"

financial_crew = build_crew(ANALYSIS_CREW_NAME, config, agents, tasks)
financial_qa_crew = build_crew(QA_CREW_NAME, config, agents, tasks)


# =========================
# PIPELINE FUNCTION
# =========================
async def run_pipeline(data: Dict, profile: Dict) -> Dict:
    try:
        response = await financial_crew.kickoff_async(inputs={
            "transactions": data,
            "profile": profile
        })

        parsed = safe_parse(response)

        return {
            "categories": parsed.get("categories", []),
            "values": parsed.get("values", []),
            "insights": parsed.get("insights", []),
            "risk_profile": parsed.get("risk_profile", "Unknown"),
            "justification": parsed.get("justification", "Unknown"),
            "advice": parsed.get("advice", [])
        }

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        return {}


# =========================
# QA FUNCTION
# =========================
async def run_qa_query(query: str, profile: Dict) -> str:
    try:
        response = await financial_qa_crew.kickoff_async(inputs={
            "query": query,
            "age": profile.get("age"),
            "salary": profile.get("salary"),
            "investments": profile.get("investments"),
            "loans": profile.get("loans"),
            "analysis-data": profile.get("analysis", {})
        })

        return getattr(response, "raw", str(response))

    except Exception as e:
        logger.error(f"QA execution failed: {e}")
        return "Unable to process your request at the moment."
