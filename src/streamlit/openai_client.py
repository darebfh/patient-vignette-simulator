from openai import OpenAI
import constants


def set_up_patient_vignette():
    return "You are a 25-year-old woman who has been experiencing a persistent cough for the past 3 weeks."


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI()
        self.patient_vignette = set_up_patient_vignette()

    def simulate_anamnesis(self, history):
        history = history.insert(0, self.patient_vignette)
        completion = self.client.chat.completions.create(
            seed=constants.SEED,
            model="gpt-4",
            messages=history
        )
        return completion.choices[0].message.content

