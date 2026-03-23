from locust import HttpUser, task, between

class ToxicUser(HttpUser):
    wait_time = between(1, 3)

    texts = [
        "nee saavu da 😂",
        "I strongly disagree with your opinion.",
        "k1ll urself",
        "This is nice",
        "un moonji romba kevalam"
    ]

    @task
    def predict(self):
        import random
        self.client.post(
            "/predict",
            json={"text": random.choice(self.texts)}
        )