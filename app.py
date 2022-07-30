import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from time import time
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import collections

G = 0.05


class Plotter:
    def plot(self, i):

        # clear axis
        self.ax1.cla()
        self.ax2.cla()
        # plot cpu
        # for name, data in self.data.items():
        #     self.ax.plot(data, label=name)

        if "error" in self.data:
            self.ax1.plot(self.data["error"], label="error")
        if "thrust" in self.data:
            self.ax2.plot(self.data["thrust"], label="thrust")

        self.ax1.legend(loc="best")
        self.ax2.legend(loc="best")

    def add(self, name, datapoint):
        if name not in self.data:
            self.data[name] = collections.deque(np.zeros(5000))
        self.data[name].popleft()
        self.data[name].append(datapoint)

    def __init__(self) -> None:
        self.data = {}

        # define and adjust figure
        fig = plt.figure(figsize=(6, 6), facecolor="#DEDEDE")

        canvas = FigureCanvasTkAgg(fig, master=tk.Toplevel())
        canvas.get_tk_widget().grid(column=0, row=1)

        self.ax1 = plt.subplot(211)
        self.ax2 = plt.subplot(212)
        self.ax1.set_facecolor("#DEDEDE")
        self.ax2.set_facecolor("#DEDEDE")
        # animate
        self.ani = FuncAnimation(fig, self.plot, interval=1000)


class Rocket:
    def __init__(
        self, canvas: tk.Canvas, start_height, max_thrust: float, target: float
    ):
        self.canvas = canvas
        self.target = target
        self.max_thrust = max_thrust
        start_height = np.clip(start_height, 30, 770)
        self.id = canvas.create_oval(
            370,
            start_height - 30,
            430,
            start_height + 30,
        )

        self.prev_error = None
        self.x = 400
        self.y = 770
        self.vx = 0
        self.vy = 0

    def get_thrust(self):
        return float(np.clip(self.thrust_logic(), -self.max_thrust, 0))

    def thrust_logic(self):
        C = G
        P = 0.07
        D = 2

        error = self.target - self.y
        if self.prev_error is None:
            error_diff = 0
        else:
            error_diff = error - self.prev_error

        self.prev_error = error
        return (self.target - self.y) * P - C + D * error_diff

    def move(self):
        global plotter
        plotter.add("error", self.target - self.y)

        x1, y1, x2, y2 = self.canvas.bbox(self.id)
        self.x = (x1 + x2) // 2
        self.y = (y1 + y2) // 2

        thrust = self.get_thrust()
        plotter.add("thrust", thrust)
        self.vy += thrust
        self.vy += G  # Gravity

        if (x2 > 800 and self.vx > 0) or (x1 < 0 and self.vx < 0):
            self.vx = 0
        if (y2 > 800 and self.vy > 0) or (y1 < 0 and self.vy < 0):
            self.vy = 0

        # print(self.vy)

        self.x += self.vx
        self.y += self.vy

        self.canvas.delete(self.id)
        self.id = self.canvas.create_oval(
            int(self.x - 30),
            int(self.y - 30),
            int(self.x + 30),
            int(self.y + 30),
        )


class Environment:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(self.master, width=800, height=800)
        self.start_height = 0
        self.target_height = 400
        self.canvas.create_line(0, self.target_height, 800, self.target_height)
        self.canvas.pack()
        self.rocket = Rocket(
            self.canvas, self.start_height, 0.1, target=self.target_height
        )
        self.canvas.pack()
        self.master.after(0, self.animation)

    def animation(self):
        self.rocket.move()
        self.master.after(12, self.animation)


root = tk.Tk()
plotter = Plotter()
app = Environment(root)


tk.mainloop()
