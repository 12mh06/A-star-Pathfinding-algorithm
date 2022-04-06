import math
import pygame
import sys
from pygame.locals import *
import tkinter.messagebox

ORANGE = (255, 140, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 255, 255)
VIOLET = (138, 43, 226)
YELLOW = (255, 255, 0)
PINK = (205, 50, 120)
GREY = (161, 166, 182)

ROWS = 50
COLS = 50
SQUARE_DISTANCE = 1
DIAGONAL_SQUARE = SQUARE_DISTANCE * math.sqrt(2)

pygame.init()
DISPLAY = pygame.display.set_mode((600, 600), 0, 32)
pygame.display.set_caption('A* Pathfinder')
DISPLAY.fill(WHITE)

BOARD_HEIGHT = DISPLAY.get_size()[1] - 20
BOARD_WIDTH = BOARD_HEIGHT
SQUARES_SIZE = BOARD_HEIGHT / COLS

BOARD_PLACE_X = (DISPLAY.get_size()[0] - BOARD_WIDTH) / 2
BOARD_PLACE_Y = 10


# speichert die Distanz zum Startknoten (G) und zum Endknoten (H) für jeden Knoten
class Tile:

    def __init__(self, row, col):
        self.g = float('inf')
        self.h = float('inf')
        self.is_barrier = False
        self.was_explored = False
        self.is_solution = False
        self.previous = None
        self.place = [row, col]

    def get_f(self):
        return self.g + self.h

    # returns true if diagonal neighbour and false if horizontal/vertical
    # neighbour variable MUST be a neighbour for correct result
    def is_diagonal_neighbour(self, neighbour):
        if not self.check_if_neighbour(neighbour):
            raise Exception('Not a neighbour! false neighbour: ' + str(neighbour.place))

        return self.place[0] != neighbour.place[0] and self.place[1] != neighbour.place[1]

    def check_if_neighbour(self, neighbour):
        distance_x = abs(neighbour.place[0] - self.place[0])
        distance_y = abs(neighbour.place[1] - self.place[1])

        return distance_x <= 1 and distance_y <= 1

    def get_color(self, board):
        color = GREY
        if self.is_barrier:
            color = RED
        elif self.is_solution:
            color = VIOLET
        elif board.start is self or board.end is self:
            color = ORANGE
        elif self.was_explored:
            color = GREEN
        elif self.g != float('inf') and self.h != float('inf'):
            color = BLUE

        return color

    def draw(self, board):
        pygame.draw.rect(DISPLAY, self.get_color(board), (BOARD_PLACE_X + self.place[1] * SQUARES_SIZE,
                                                          BOARD_PLACE_Y + self.place[0] * SQUARES_SIZE,
                                                          SQUARES_SIZE, SQUARES_SIZE))

        pygame.draw.rect(DISPLAY, WHITE, (BOARD_PLACE_X + self.place[1] * SQUARES_SIZE,
                                          BOARD_PLACE_Y + self.place[0] * SQUARES_SIZE,
                                          SQUARES_SIZE, SQUARES_SIZE), 1)

    def is_over(self, mouse_position):
        tile_x = BOARD_PLACE_X + self.place[1] * SQUARES_SIZE
        tile_y = BOARD_PLACE_Y + self.place[0] * SQUARES_SIZE
        if tile_x < mouse_position[0] < tile_x + SQUARES_SIZE:
            if tile_y < mouse_position[1] < tile_y + SQUARES_SIZE:
                return True

        return False

    def change_after_click(self, board):
        if board.choosing_start:
            board.set_start(self)
            board.choosing_start = False
            board.choosing_end = True

        elif board.choosing_end:
            board.set_end(self)
            board.choosing_end = False
            board.choosing_barrier = True

        elif board.choosing_barrier and self is not board.start and self is not board.end:
            self.is_barrier = True


class Board:

    def __init__(self):
        self.shape = [[Tile(x, y) for y in range(ROWS)] for x in range(COLS)]
        self.start = None
        self.end = None
        self.choosing_start, self.choosing_end, self.choosing_barrier = True, False, False

    def explore(self, tile):
        tile.was_explored = True
        print('\n\nexplored tile: ' + str(tile.place))

        for neighbour in self.get_neighbours(tile):
            print('\n-   neighbour: ' + str(neighbour.place))

            self.calc_values(tile, neighbour)
            print('-   new neighbour g-value: ' + str(neighbour.g) + '  |  new neighbour h-value: ' + str(neighbour.h))

    def calc_values(self, previous, neighbour):
        distance_to_prev = SQUARE_DISTANCE
        if previous.is_diagonal_neighbour(neighbour):
            distance_to_prev = DIAGONAL_SQUARE

        new_g_distance = previous.g + distance_to_prev

        x_end = self.end.place[0]
        y_end = self.end.place[1]
        new_h_distance = math.sqrt(
            SQUARE_DISTANCE * ((neighbour.place[0] - x_end) ** 2 + (neighbour.place[1] - y_end) ** 2))

        if new_g_distance + new_h_distance < neighbour.g + neighbour.h:
            neighbour.g = new_g_distance
            neighbour.h = new_h_distance
            neighbour.previous = previous

    def find_smallest_f_value(self):
        result = None
        for row in self.shape:
            for tile in row:
                if not tile.was_explored and not tile.is_barrier:
                    if result is None or tile.get_f() < result.get_f():
                        result = tile

        return result

    def set_start(self, start):
        self.start = start
        start.g = 0

    def set_end(self, end):
        self.end = end
        d1 = self.start.place[0] - self.end.place[0]
        d2 = self.start.place[1] - self.end.place[1]
        self.start.h = math.sqrt(SQUARE_DISTANCE * (d1 ** 2 + d2 ** 2))

    def set_start_end(self, start, end):
        self.set_start(start)
        self.set_end(end)

    def get_neighbours(self, tile):
        min_row = max(0, tile.place[0] - 1)
        max_row = min(len(self.shape) - 1, tile.place[0] + 1)
        min_col = max(0, tile.place[1] - 1)
        max_col = min(len(self.shape[0]) - 1, tile.place[1] + 1)

        result = []
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                neighbour = self.shape[row][col]
                if not neighbour.is_barrier and neighbour is not tile:
                    result.append(neighbour)

        return result

    def result_found(self, tile):
        return tile.check_if_neighbour(self.end)

    def solve_path(self):
        if self.start is None or self.end is None:
            raise Exception('\nStart or end not defined!')
        else:
            self.choosing_barrier = False
            tile = self.start
            while not self.result_found(tile) and not self.check_no_solutions():
                self.explore(tile)
                tile = self.find_smallest_f_value()
                self.draw()
                pygame.display.flip()

            if self.check_no_solutions():
                message_box('Result', 'there is no valid solution')
                print('\nthere is no valid solution')
            else:
                shortest_path_distance = self.show_shortest_path(tile, self.end)
                self.draw()
                pygame.display.flip()
                message_box('Result', 'path found, shortest distance: {}'.format(shortest_path_distance))
                print('\nresult found')

    def check_no_solutions(self):
        if self.find_smallest_f_value().g == float('inf'):
            return True

        return False

    def show_shortest_path(self, tile, next_tile):
        shortest_path_distance = 0
        while tile is not None:
            added_distance = SQUARE_DISTANCE
            if tile.is_diagonal_neighbour(next_tile):
                added_distance = DIAGONAL_SQUARE

            shortest_path_distance += added_distance
            if tile is not self.start:
                tile.is_solution = True
            next_tile = tile
            tile = tile.previous
            self.draw()
            pygame.display.flip()

        return shortest_path_distance

    def draw(self):
        for i, row in enumerate(self.shape):
            for j, tile in enumerate(row):
                tile.draw(self)


def message_box(title, text):
    window = tkinter.Tk()
    window.wm_withdraw()
    return tkinter.messagebox.showinfo(title=title, message=text)


def main():
    BOARD = Board()
    mouse_hold_counter = 0
    while True:
        BOARD.draw()
        pygame.display.flip()

        # enables user to draw the barrier (red) tiles holding down the mouse button
        mouse_position = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            mouse_hold_counter += 12
        else:
            mouse_hold_counter = 0
        if BOARD.choosing_barrier and mouse_hold_counter >= 60:
            for row in BOARD.shape:
                for tile in row:
                    if tile.is_over(mouse_position):
                        tile.change_after_click(BOARD)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for row in BOARD.shape:
                    for tile in row:
                        if tile.is_over(mouse_position):
                            tile.change_after_click(BOARD)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and BOARD.choosing_barrier:
                    BOARD.solve_path()
                # restarts (clears) the board
                if event.key == pygame.K_BACKSPACE:
                    BOARD = Board()


if __name__ == '__main__':
    main()


