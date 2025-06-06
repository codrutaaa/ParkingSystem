from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from agents import DriverAgent, ParkingSpotAgent, CoordinatorAgent, PoliceAgent
import random
import pandas as pd

# Defines the main simulation model for smart parking
class ParkingModel(Model):
    def __init__(self, num_drivers, num_parking_spots, width=10, height=10):
        super().__init__()
        self.grid = MultiGrid(width, height, torus=False) # 2D grid where agents are placed
        self.schedule = RandomActivation(self)# Scheduler to activate agents randomly

        # Data collector to track the number of parked, active, and waiting drivers
        self.datacollector = DataCollector(
            model_reporters={
                "Parked": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, DriverAgent) and a.parked),
                "Active": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, DriverAgent) and not a.parked and not a.blocked),
                "Waiting": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, DriverAgent) and a.blocked)
            }
        )

        # Create parking spots and place them randomly on the grid
        for i in range(num_parking_spots):
            spot = ParkingSpotAgent(i, self)
            x, y = random.randrange(width), random.randrange(height)
            self.grid.place_agent(spot, (x, y))
            self.schedule.add(spot)

        # Create driver agents and place them randomly
        for i in range(num_parking_spots, num_parking_spots + num_drivers):
            driver = DriverAgent(i, self)
            x, y = random.randrange(width), random.randrange(height)
            self.grid.place_agent(driver, (x, y))
            self.schedule.add(driver)

        # Create one coordinator agent
        coord_id = num_parking_spots + num_drivers
        coord = CoordinatorAgent(coord_id, self)
        self.schedule.add(coord)

        # Create one police agent and place it in the corner of the grid
        police = PoliceAgent(coord_id + 1, self)
        self.grid.place_agent(police, (0, 0))
        self.schedule.add(police)

        self.running = True # Control flag for the simulation

    # Executes one step of the simulation
    def step(self):
        self.schedule.step() # Activate all agents
        self.datacollector.collect(self) # Collect data for the current step

        # End simulation if no drivers are left searching for parking
        active = sum(1 for a in self.schedule.agents if isinstance(a, DriverAgent) and not a.parked and not a.blocked)
        if active == 0:
            print("Simulation ended automatically.")
            self.running = False

    # Exports collected data to a CSV file
    def export_data(self, filename="simulation_data.csv"):
        df = self.datacollector.get_model_vars_dataframe()
        df.to_csv(filename)
        print(f"Data saved to {filename}")
