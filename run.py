from model import ParkingModel

model = ParkingModel(num_soferi=5, num_parcari=3)

for i in range(10):
    print(f"--- Step {i+1} ---")
    model.step()