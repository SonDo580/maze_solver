import time
import random
from tkinter import Tk, BOTH, Canvas

BG_COLOR = 'white'
WALL_COLOR = 'black'
PATH_COLOR = 'red'
UNDO_PATH_COLOR = 'gray'

LINE_WIDTH = 2


class Window:
    def __init__(self, width, height):
        self.__root = Tk()
        self.__root.title('Maze Solver')

        self.__canvas = Canvas(self.__root, bg=BG_COLOR,
                               width=width, height=height)
        self.__canvas.pack(fill=BOTH, expand=True)

        self.__running = False
        self.__root.protocol('WM_DELETE_WINDOW', self.close)

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.__running = True

        while self.__running:
            self.redraw()

    def close(self):
        self.__running = False

    def draw_line(self, line, color):
        line.draw(self.__canvas, color)


# x = 0: left of window
# y = 0: top of window
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# Start and End are Point instances
class Line:
    def __init__(self, start, end):
        self.__start = start
        self.__end = end

    def draw(self, canvas, color):
        canvas.create_line(self.__start.x, self.__start.y,
                           self.__end.x, self.__end.y, fill=color, width=LINE_WIDTH)
        canvas.pack(fill=BOTH, expand=True)


# x1, y1: top-left
# x2, y2: bottom-right
class Cell:
    def __init__(self, x1, y1, x2, y2, window):
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self.__x1 = x1
        self.visited = False
        self.__x2 = x2
        self.__y1 = y1
        self.__y2 = y2
        self.__window = window

    def draw(self):
        top_left = Point(self.__x1, self.__y1)
        bottom_left = Point(self.__x1, self.__y2)
        top_right = Point(self.__x2, self.__y1)
        bottom_right = Point(self.__x2, self.__y2)

        if self.has_left_wall:
            self.__window.draw_line(Line(top_left, bottom_left), WALL_COLOR)
        else:
            self.__window.draw_line(Line(top_left, bottom_left), BG_COLOR)

        if self.has_right_wall:
            self.__window.draw_line(Line(top_right, bottom_right), WALL_COLOR)
        else:
            self.__window.draw_line(
                Line(top_right, bottom_right), BG_COLOR)

        if self.has_top_wall:
            self.__window.draw_line(Line(top_left, top_right), WALL_COLOR)
        else:
            self.__window.draw_line(Line(top_left, top_right), BG_COLOR)

        if self.has_bottom_wall:
            self.__window.draw_line(
                Line(bottom_left, bottom_right), WALL_COLOR)
        else:
            self.__window.draw_line(
                Line(bottom_left, bottom_right), BG_COLOR)

    def get_center(self):
        return Point((self.__x1 + self.__x2) / 2, (self.__y1 + self.__y2) / 2)

    def draw_move(self, to_cell, undo=False):
        color = PATH_COLOR
        if undo:
            color = UNDO_PATH_COLOR

        self.__window.draw_line(
            Line(self.get_center(), to_cell.get_center()), color)


# x1, y1: top-left corner
class Maze:
    def __init__(
        self,
        x1,
        y1,
        num_rows,
        num_cols,
        cell_size,
        window,
    ):
        self.__x1 = x1
        self.__y1 = y1
        self.__num_rows = num_rows
        self.__num_cols = num_cols
        self.__cell_size = cell_size
        self.__window = window
        self.__cells = []
        self.__create_cells()

    def __create_cells(self):
        for i in range(self.__num_rows):
            self.__cells.append([])
            top_y = self.__y1 + self.__cell_size * i
            bottom_y = self.__y1 + self.__cell_size * (i + 1)

            for j in range(self.__num_cols):
                left_x = self.__x1 + self.__cell_size * j
                right_x = self.__x1 + self.__cell_size * (j + 1)

                new_cell = Cell(left_x, top_y, right_x,
                                bottom_y, self.__window)
                self.__cells[i].append(new_cell)

        self.__draw_cells()
        self.__break_entrance_and_exit()
        self.__break_walls(0, 0)
        self.__reset_cells_visited()

    def __draw_cells(self):
        for row in self.__cells:
            for cell in row:
                self.__draw_cell(cell)

    def __draw_cell(self, cell):
        cell.draw()
        self.__animate()

    def __animate(self):
        self.__window.redraw()
        time.sleep(0.01)

    def __break_entrance_and_exit(self):
        entrance_cell = self.__cells[0][0]
        exit_cell = self.__cells[self.__num_rows-1][self.__num_cols-1]

        entrance_cell.has_top_wall = False
        exit_cell.has_bottom_wall = False

        self.__draw_cell(entrance_cell)
        self.__draw_cell(exit_cell)

    # row, col: indexes of current cell
    def __break_walls(self, row, col):
        self.__cells[row][col].visited = True
        while True:
            next_indexes = []

            # move left
            if col > 0 and not self.__cells[row][col - 1].visited:
                next_indexes.append((row, col - 1))

            # move right
            if col < self.__num_cols - 1 and not self.__cells[row][col + 1].visited:
                next_indexes.append((row, col + 1))

            # move up
            if row > 0 and not self.__cells[row - 1][col].visited:
                next_indexes.append((row - 1, col))

            # move down
            if row < self.__num_rows - 1 and not self.__cells[row + 1][col].visited:
                next_indexes.append((row + 1, col))

            # no where to go from here
            if len(next_indexes) == 0:
                self.__draw_cell(self.__cells[row][col])
                return

            # randomly choose a direction
            next_index = next_indexes[random.randrange(len(next_indexes))]

            # remove wall between current cell and next cell
            # move left
            if next_index[1] == col - 1:
                self.__cells[row][col].has_left_wall = False
                self.__cells[row][col - 1].has_right_wall = False

            # move right
            if next_index[1] == col + 1:
                self.__cells[row][col].has_right_wall = False
                self.__cells[row][col + 1].has_left_wall = False

            # move up
            if next_index[0] == row - 1:
                self.__cells[row][col].has_top_wall = False
                self.__cells[row - 1][col].has_bottom_wall = False

            # move down
            if next_index[0] == row + 1:
                self.__cells[row][col].has_bottom_wall = False
                self.__cells[row + 1][col].has_top_wall = False

            # move to the next cell and continue breaking walls
            self.__break_walls(next_index[0], next_index[1])

    def __reset_cells_visited(self):
        for row in self.__cells:
            for cell in row:
                cell.visited = False
