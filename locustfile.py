from uuid import uuid4
from locust import HttpUser, task, between
from faker import Faker
from random import choices, randint


class LoadTest(HttpUser):
    toy_data = {}
    wait_time = between(1, 5)

    @task(100)
    def get_toys(self):
        response = self.client.get("/toys")
        print(response.json())

    @task(100)
    def get_users(self):
        response = self.client.get("/users")
        print(response.json())

    @task(50)
    def create_toys(self):
        toy_name = Faker().name()

        response = self.client.post("/toys", json={"name": toy_name})
        print(response.json())
        new_toy_data = response.json()

        print(new_toy_data["id"])
        new_toy_resp = self.client.get(f"/toys/{new_toy_data['id']}")
        toy = new_toy_resp.json()
        toy_name = toy["name"]
        toy_id = toy["id"]
        self.toy_data[toy_name] = toy_id

    @task(25)
    def create_user(self):
        user_name = Faker().name()
        local_data = self.toy_data.copy()
        toys_ids = list(local_data.values())
        print(toys_ids)
        num_ids = randint(1, len(toys_ids))

        toys = choices(toys_ids, k=num_ids)
        response = self.client.post("/users", json={"name": user_name, "toys": toys})
        new_user_data = response.json()
        user_id = new_user_data["id"]
        user_response = self.client.get(f"/users/{user_id}")
        print(user_response.json())
