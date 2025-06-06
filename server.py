from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import TextElement
from mesa.visualization.UserParam import UserSettableParameter

from model import ParkingModel
from agents import DriverAgent, ParkingSpotAgent, CoordinatorAgent, PoliceAgent

# Custom HTML legend element to display agent color meanings and symbols
class LegendText(TextElement):
    def render(self, model):
        return (
            "<div style='padding: 20px;'>"
            "<h1 style='font-family: Arial, sans-serif; font-size: 28px; color: #2c3e50; text-align: center; margin-bottom: 20px;'>Smart Parking Simulation Dashboard</h1>"
            "<div style='display: flex; flex-direction: row; justify-content: center; align-items: flex-start; gap: 40px;'>"
            "<div style='flex: 1; max-width: 250px;'>"
            "<button onclick=\"toggleLegend()\" style='padding: 6px 12px; font-size: 14px; background-color: #333; color: white; border: none; border-radius: 4px;'>Toggle Legend</button>"
            "<div id='legend' style='display:block; margin-top: 15px; padding: 15px; background-color: #fff; border: 1px solid #ccc; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); font-family: Arial, sans-serif;'>"
            "<h4 style='margin-top: 0; color: #222;'>Legend</h4>"
            "<ul style='list-style-type: none; padding-left: 0; font-size: 14px;'>"
            "<li><span style='color: blue;'>■</span> <b>D</b> – Active Driver (searching)</li>"
            "<li><span style='color: green;'>■</span> <b>D</b> – Parked Driver</li>"
            "<li><span style='color: orange;'>■</span> <b>D</b> – Temporarily Blocked Driver</li>"
            "<li><span style='color: gold;'>■</span> 3, 2, 1 – Parking spots available</li>"
            "<li><span style='color: gray;'>■</span> 0 – Full parking</li>"
            "<li><span style='color: black;'>■</span> P – Police</li>"
            "</ul>"
            "</div>"
            "</div>"
            "<div style='flex: 2;'>"
            "<div id='elements-wrapper'></div>"
            "</div>"
            "</div>"
            "<script>function toggleLegend() { var legend = document.getElementById('legend'); legend.style.display = (legend.style.display === 'none') ? 'block' : 'none'; }</script>"
            "</div>"
        )

# Determines how agents are displayed on the grid
def agent_portrayal(agent):
    portrayal = {"Shape": "circle", "Filled": True, "r": 0.8}

    if isinstance(agent, DriverAgent):
        if agent.blocked:
            portrayal["Color"] = "orange"
        elif agent.parked:
            portrayal["Color"] = "green"
        else:
            portrayal["Color"] = "blue"
        portrayal["Layer"] = 2
        portrayal["text"] = f"D({agent.fine})" # Shows number of fines
        portrayal["text_color"] = "white"

    elif isinstance(agent, ParkingSpotAgent):
        if agent.available_spots == 0:
            portrayal["Color"] = "gray"
        else:
            portrayal["Color"] = "yellow"
        portrayal["Layer"] = 1
        portrayal["text"] = str(agent.available_spots)
        portrayal["text_color"] = "black"

    elif isinstance(agent, CoordinatorAgent):
        portrayal["Color"] = "red"
        portrayal["Layer"] = 3
        portrayal["text"] = "C"
        portrayal["text_color"] = "white"

    elif isinstance(agent, PoliceAgent):
        portrayal["Color"] = "black"
        portrayal["Layer"] = 4
        portrayal["text"] = "P"
        portrayal["text_color"] = "white"

    return portrayal

# Line chart showing real-time simulation statistics
chart = ChartModule([
    {"Label": "Parked", "Color": "green"},
    {"Label": "Active", "Color": "blue"},
    {"Label": "Waiting", "Color": "orange"},
], data_collector_name='datacollector')

# Grid display configuration (10x10 grid, 500x500 pixel display)
grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
legend = LegendText()

# Create the modular Mesa server with visualization modules
server = ModularServer(
    ParkingModel,
    [legend, grid, chart], # Elements to display
    "Smart Parking Simulation",  # Simulation title
    {
        "num_drivers": UserSettableParameter("slider", "Number of Drivers", 5, 1, 20, 1),
        "num_parking_spots": UserSettableParameter("slider", "Number of Parking Spots", 3, 1, 10, 1),
        "width": 10,
        "height": 10
    }
)

server.port = 8521
server.launch()