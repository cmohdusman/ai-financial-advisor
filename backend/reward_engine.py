class RewardEngine:

    def calculate_reward(self, human_feedback):

        score = 0

        if human_feedback.get("correct_decision"):
            score += 0.4

        if human_feedback.get("compliant"):
            score += 0.3

        if human_feedback.get("fraud_detected"):
            score += 0.2

        if human_feedback.get("safe_reasoning"):
            score += 0.1

        return round(score, 2)