import serial
import matplotlib.pyplot as plt

# Configure serial port
print('Opening serial port...')
ser = serial.Serial('/dev/cu.usbserial-02278833', 115200)  # Adjust port and baud rate accordingly
print('Serial port opened')

# Define the anchors
anchors = []
def add_anchor(name, x, y, distance):
    anchors.append({"name": name, "x": x, "y": y, "distance": distance})

# Trilateration function
def trilaterate(x1, y1, r1, x2, y2, r2, x3, y3, r3):
    # Coefficients for equations
    A = -2 * x1 + 2 * x2
    B = -2 * y1 + 2 * y2
    C = -2 * x2 + 2 * x3
    D = -2 * y2 + 2 * y3
    
    # Constants
    E = r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2
    F = r2**2 - r3**2 - x2**2 + x3**2 - y2**2 + y3**2
    
    # Solve the system of equations
    det = A * D - B * C
    if det == 0:
        return None  # No unique solution
    
    # Calculate coordinates
    x = (E * D - B * F) / det
    y = (A * F - E * C) / det
    
    return x, y


# Add anchors
add_anchor("1201", -3.0988, 4.6482, 0) # Anchor 1
add_anchor("7687", 1.0922, 5.5118, 0) # Anchor 2
add_anchor("5645", 3.556, 2.1844, 0) # Anchor 3
counter = 0
plt.ion()

try:
    while True:
        # Read data from serial port
        data = ser.readline().decode().strip()
        counter += 1
        data = data.split()
        name = data[1][0:-1]
        distance = float(data[3])

        # Update the distance of the anchor
        for anchor in anchors:
            if anchor["name"] == name:
                if (abs(distance - float(anchor["distance"])) < 2 or anchor["distance"] == 0):  # Adjust threshold as needed
                    anchor["distance"] = distance
                break
        
        # Trilaterate if all distances are available
        if all(anchor["distance"] != 0 for anchor in anchors):
            if counter % 3 == 0:
                tag_coordinates = trilaterate(anchors[0]["x"], anchors[0]["y"], float(anchors[0]["distance"]), anchors[1]["x"], anchors[1]["y"], float(anchors[1]["distance"]), anchors[2]["x"], anchors[2]["y"], float(anchors[2]["distance"]))
                print("Tag Coordinates: ", round(tag_coordinates[0], 2), round(tag_coordinates[1], 2))

                plt.clf()
                anchor_x = [anchor["x"] for anchor in anchors]
                anchor_y = [anchor["y"] for anchor in anchors]
                plt.scatter(anchor_x, anchor_y, color='red', label='Anchors')
                plt.scatter(tag_coordinates[0], tag_coordinates[1], color='blue', label='Tag')
                plt.xlabel('X (m)')
                plt.ylabel('Y (m)')
                plt.title('Anchor and Tag Coordinates')
                plt.legend()
                plt.grid(True)
                plt.gca().set_aspect('equal', adjustable='box')
                plt.pause(0.01)  # Pause to allow the plot to update

except KeyboardInterrupt:
    pass
ser.close()
print('Serial port closed')
