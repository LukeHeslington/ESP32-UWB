import serial
import matplotlib.pyplot as plt

def add_anchor(name, x, y, distance):
    anchors.append({"name": name, "x": x, "y": y, "distance": distance})
    
# Configure serial port
print('Opening serial port...')
ser = serial.Serial('/dev/cu.usbserial-02278833', 115200)
print('Serial port opened')

# Definitions
anchors = []
points = [
    [0, 0], [0, 277], [171, 277], [171,479], [0, 479], [0, 664], [171, 664], [171, 190], 
    [404.5, 190], [404.5, 242], [448, 242], [448, 223.5], [448, 304.5], [492.5, 304.5], [590.5, 304.5], 
    [590.5, 400], [404.5, 400], [404.5, 664], [590.5, 664], [590.5, 245.5], [492.5, 245.5], 
    [492.5, 304.5], [492.5, 165.5],[590.5, 165.5], [590.5, 0], [448, 0], [448, 190], [448, 0], [0, 0]
]

# Convert points to meters by dividing each coordinate by 39.37
points_inches = [[x / 39.37, y / 39.37] for x, y in points]
counter = 0

# Add anchors
add_anchor("1201", 181 / 39.37, 327 / 39.37, 0) # Anchor 1
add_anchor("7687", 50 / 39.37, 10 / 39.37, 0) # Anchor 2
add_anchor("5645", 586 / 39.37, 92 / 39.37, 0) # Anchor 3

plt.ion()

try:
    while True:
        # Read data from serial port
        data = ser.readline().decode().strip()
        data = data.split()
        name = data[1][0:-1]
        distance = float(data[3])
        counter += 1
        if counter % 3 == 0:
            for anchor in anchors:
                anchor["distance"] = 1000

        # Update the distance of the anchor
        for anchor in anchors:
            if anchor["name"] == name:
                anchor["distance"] = distance

        plt.clf()

        # Plot the points
        for anchor in anchors:
            anchor_x = [anchor["x"] for anchor in anchors]
            anchor_y = [anchor["y"] for anchor in anchors]
            plt.scatter(anchor_x, anchor_y, color='red', label='Anchors')

        # Determine the closest anchor
        closest_anchor = min(filter(lambda anchor: anchor["distance"] > 0, anchors), key=lambda anchor: anchor["distance"])
        print("Closest Anchor: ", closest_anchor["name"])

        # Draw a circle around the closest anchor.
        circle = plt.Circle((closest_anchor["x"], closest_anchor["y"]), closest_anchor["distance"], color='blue', fill=False)
        plt.gca().add_artist(circle)

        # Plot the points
        plt.plot([point[0] for point in points_inches], [point[1] for point in points_inches], color='black', marker='')

        for i in range(len(points_inches)):
            plt.plot([points_inches[i][0], points_inches[(i + 1) % len(points_inches)][0]], 
                    [points_inches[i][1], points_inches[(i + 1) % len(points_inches)][1]], 
                    color='black', linewidth=2)

        # Find the min and max x and y coordinates
        min_x = min(point[0] for point in points_inches)
        max_x = max(point[0] for point in points_inches)
        min_y = min(point[1] for point in points_inches)
        max_y = max(point[1] for point in points_inches)

        plt.plot([min_x, max_x, max_x, min_x, min_x], [min_y, min_y, max_y, max_y, min_y], color='black', marker='', linewidth=2)

        # Set plot properties
        plt.xlabel('X (m)')
        plt.ylabel('Y (m)')
        plt.title('Anchor and Tag Coordinates')
        plt.xlim(min_x - 2, max_x + 2)  # Lock x-axis limits
        plt.ylim(min_y - 2 , max_y + 2)  # Lock y-axis limits
        plt.xticks(range(int(min_x), int(max_x) + 1))  # Set x-axis ticks
        plt.yticks(range(int(min_y), int(max_y) + 1))  # Set y-axis ticks
        plt.gca().set_aspect('equal', adjustable='box')
        plt.pause(0.01)  # Pause to allow the plot to update

except KeyboardInterrupt:
    pass
ser.close()
print('Serial port closed')