from crew import FinancialAdvisorCrew

if __name__ == "__main__":
    crew_instance = FinancialAdvisorCrew().crew()
    result = crew_instance.kickoff(
        inputs={
            "transactions": "sample transaction data",
            "profile": {
                "age": 30,
                "salary": 100000,
                "investments": 20000,
                "loans": 50000
            },
            "query": "Can I afford a home loan?"
        }
    )

    print(result)
