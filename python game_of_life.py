import tkinter as tk
import random
from abc import ABC, abstractmethod

class Config:
    _instance = None

    def __new__(cls, grid_size=30, cell_size=20, tick_interval=300):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.grid_size = grid_size
            cls._instance.cell_size = cell_size
            cls._instance.tick_interval = tick_interval
        return cls._instance

class GridInitializationStrategy(ABC):
    @abstractmethod
    def initialize(self, grid):
        pass

class RandomInitializationStrategy(GridInitializationStrategy):
    def initialize(self, grid):
        for x in range(len(grid)):
            for y in range(len(grid[0])):
                grid[x][y] = random.choice([0, 1])

class EmptyInitializationStrategy(GridInitializationStrategy):
    def initialize(self, grid):
        for x in range(len(grid)):
            for y in range(len(grid[0])):
                grid[x][y] = 0

class Observable:
    def __init__(self):
        self._observers = []

    def add_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.update()

class Observer(ABC):
    @abstractmethod
    def update(self):
        pass

class LifeModel(Observable):
    def __init__(self):
        super().__init__()
        config = Config()
        self.grid_size = config.grid_size
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]

    def count_neighbors(self, x, y):
        neighbors = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = (x + dx) % self.grid_size, (y + dy) % self.grid_size
                neighbors += self.grid[nx][ny]
        return neighbors

    def next_generation(self):
        new_grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                neighbors = self.count_neighbors(x, y)
                if self.grid[x][y] == 1 and neighbors in [2, 3]:
                    new_grid[x][y] = 1
                elif self.grid[x][y] == 0 and neighbors == 3:
                    new_grid[x][y] = 1
        self.grid = new_grid
        self.notify_observers()

class LifeView(Observer):
    def __init__(self, root, model):
        self.model = model
        self.model.add_observer(self)
        config = Config()
        self.canvas = tk.Canvas(
            root,
            width=config.grid_size * config.cell_size,
            height=config.grid_size * config.cell_size,
            bg="white"
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def update(self):
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        config = Config()
        for x in range(config.grid_size):
            for y in range(config.grid_size):
                if self.model.grid[x][y] == 1:
                    self.canvas.create_rectangle(
                        x * config.cell_size, y * config.cell_size,
                        (x + 1) * config.cell_size, (y + 1) * config.cell_size,
                        fill="black"
                    )

    def on_canvas_click(self, event):
        config = Config()
        x, y = event.x // config.cell_size, event.y // config.cell_size
        self.model.grid[x][y] = 1 - self.model.grid[x][y]
        self.model.notify_observers()

class LifeController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.running = False

    def randomize_grid(self):
        RandomInitializationStrategy().initialize(self.model.grid)
        self.model.notify_observers()

    def clear_grid(self):
        EmptyInitializationStrategy().initialize(self.model.grid)
        self.model.notify_observers()

    def toggle_simulation(self):
        self.running = not self.running
        if self.running:
            self.run_simulation()

    def run_simulation(self):
        if self.running:
            self.model.next_generation()
            root.after(Config().tick_interval, self.run_simulation)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gra w życie (z wzorcami projektowymi)")

    model = LifeModel()
    view = LifeView(root, model)
    controller = LifeController(model, view)

    btn_randomize = tk.Button(root, text="Losuj siatkę", command=controller.randomize_grid)
    btn_randomize.pack(side="left")

    btn_clear = tk.Button(root, text="Wyczyść siatkę", command=controller.clear_grid)
    btn_clear.pack(side="left")

    btn_toggle = tk.Button(root, text="Start/Stop", command=controller.toggle_simulation)
    btn_toggle.pack(side="left")

    root.mainloop()
