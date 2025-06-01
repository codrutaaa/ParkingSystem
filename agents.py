from mesa import Agent
import math

class DriverAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.parked = False
        self.destination = None
        self.fine = 0
        self.blocked_steps = 0
        self.blocked = False
        self.wait_steps = 0

    def step(self):
        if self.parked:
            return

        if self.blocked:
            self.wait_steps += 1
            if self.wait_steps >= 5:
                self.blocked = False
                self.blocked_steps = 0
                self.wait_steps = 0
                self.destination = None
            return

        if self.destination:
            x, y = self.pos
            dx = self.destination[0] - x
            dy = self.destination[1] - y
            move_x = x + (1 if dx > 0 else -1 if dx < 0 else 0)
            move_y = y + (1 if dy > 0 else -1 if dy < 0 else 0)
            new_pos = (move_x, move_y)
            self.model.grid.move_agent(self, new_pos)

            if new_pos == self.destination:
                cell = self.model.grid.get_cell_list_contents([new_pos])
                for agent in cell:
                    if isinstance(agent, ParkingSpotAgent) and agent.available_spots > 0:
                        agent.available_spots -= 1
                        self.parked = True
                        return
            self.blocked_steps += 1
        else:
            self.blocked_steps += 1

        if self.blocked_steps > 10:
            self.destination = None
            self.blocked = True
            new_pos = self.random.choice(list(self.model.grid.empties))
            self.model.grid.move_agent(self, new_pos)

class ParkingSpotAgent(Agent):
    def __init__(self, unique_id, model, capacity=3):
        super().__init__(unique_id, model)
        self.capacity = capacity
        self.available_spots = capacity

    def step(self):
        pass

class CoordinatorAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        for agent in self.model.schedule.agents:
            if isinstance(agent, DriverAgent) and not agent.parked and not agent.blocked and agent.destination is None:
                min_dist = math.inf
                best_spot = None
                for parking in self.model.schedule.agents:
                    if isinstance(parking, ParkingSpotAgent) and parking.available_spots > 0:
                        dist = abs(agent.pos[0] - parking.pos[0]) + abs(agent.pos[1] - parking.pos[1])
                        if dist < min_dist:
                            min_dist = dist
                            best_spot = parking.pos
                agent.destination = best_spot

class PoliceAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        for agent in self.model.schedule.agents:
            if isinstance(agent, DriverAgent) and agent.parked:
                cell = self.model.grid.get_cell_list_contents([agent.pos])
                correctly_parked = any(isinstance(a, ParkingSpotAgent) for a in cell)
                if not correctly_parked:
                    agent.fine += 1
                    agent.parked = False
                    agent.destination = None
                    agent.blocked_steps = 0
                    new_pos = self.random.choice(list(self.model.grid.empties))
                    self.model.grid.move_agent(agent, new_pos)