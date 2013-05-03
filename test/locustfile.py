from locust import Locust, TaskSet


url = '/crime/stats/%s'

with open('data/portland_coordinates.txt') as f:
    coords = [l for l in f.read().split('\n') if l]
    tasks = {lambda l: l.client.get(url % coord) for coord in coords}


class ApiTasks(TaskSet):
    tasks = tasks


class ApiLocust(Locust):
    task_set = ApiTasks
