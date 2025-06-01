from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from agents import DriverAgent, ParkingSpotAgent, CoordinatorAgent, PoliceAgent
import random
import pandas as pd

class ParkingModel(Model):
    def __init__(self, num_drivers, num_parking_spots, width=10, height=10):
        super().__init__()
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)

        self.datacollector = DataCollector(
            model_reporters={
                "Parked": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, DriverAgent) and a.parked),
                "Active": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, DriverAgent) and not a.parked and not a.blocked),
                "Waiting": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, DriverAgent) and a.blocked)
            }
        )

        for i in range(num_parking_spots):
            spot = ParkingSpotAgent(i, self)
            x, y = random.randrange(width), random.randrange(height)
            self.grid.place_agent(spot, (x, y))
            self.schedule.add(spot)

        for i in range(num_parking_spots, num_parking_spots + num_drivers):
            driver = DriverAgent(i, self)
            x, y = random.randrange(width), random.randrange(height)
            self.grid.place_agent(driver, (x, y))
            self.schedule.add(driver)

        coord_id = num_parking_spots + num_drivers
        coord = CoordinatorAgent(coord_id, self)
        self.schedule.add(coord)

        police = PoliceAgent(coord_id + 1, self)
        self.grid.place_agent(police, (0, 0))
        self.schedule.add(police)

        self.running = True

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

        active = sum(1 for a in self.schedule.agents if isinstance(a, DriverAgent) and not a.parked and not a.blocked)
        if active == 0:
            print("Simulation ended automatically.")
            self.running = False

    def export_data(self, filename="simulation_data.csv"):
        df = self.datacollector.get_model_vars_dataframe()
        df.to_csv(filename)
        print(f"Data saved to {filename}")
