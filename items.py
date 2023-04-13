import sys
import random
import images_rc
import heapq

from PyQt5.QtGui import QBrush, QPixmap, QPen
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer


CELL_SIZE = 36
NUM_ROWS = 23
NUM_COLS = 23
WINDOW_WIDTH = CELL_SIZE * NUM_COLS + 100
WINDOW_HEIGHT = CELL_SIZE * NUM_ROWS + 100


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(x_start, y_start, x_goal, y_goal, graph):
    graph = [tuple(map(int, p.split('.')[::-1])) if p else None for p in graph]
    start = (int(x_start), int(y_start))
    goal = (int(x_goal), int(y_goal))
    neighbors = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    oheap = []
    heapq.heappush(oheap, (fscore[start], start))

    while oheap:
        current = heapq.heappop(oheap)[1]
        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            data.append(start)
            return ['.'.join(str(coord) for coord in point) for point in data[::-1]]

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            if neighbor not in graph or graph[graph.index(neighbor)] is None:
                continue
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue
            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))
    return None


class Player(QGraphicsRectItem):
    def __init__(self, row, col):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/images/hero_down_middle.png')
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))
        self.row = row
        self.col = col
        self.setZValue(100)

        self.bombs = False
        self.flames = False
        self.speed = False
        self.wallpass = False
        self.detonator = False
        self.bombpass = False
        self.flamepass = False
        self.mystery = False

        self.bombs_collected = False
        self.flames_collected = False
        self.speed_collected = False
        self.wallpass_collected = False
        self.detonator_collected = False
        self.bombpass_collected = False
        self.flamepass_collected = False
        self.mystery_collected = False

        self.explosions = 0
        self.bombs_add = 0

    def change_pic_right(self, count):
        if count == 1:
            pixmap = QPixmap(':/images/hero_right_1.png')
            self.setBrush(QBrush(pixmap))
        elif count == 2:
            pixmap = QPixmap(':/images/hero_right_middle.png')
            self.setBrush(QBrush(pixmap))
        elif count == 3:
            pixmap = QPixmap(':/images/hero_right_2.png')
            self.setBrush(QBrush(pixmap))
        elif count == 4:
            pixmap = QPixmap(':/images/hero_right_middle.png')
            self.setBrush(QBrush(pixmap))

    def change_pic_left(self, count):
        if count == 1:
            pixmap = QPixmap(':/images/hero_left_1.png')
            self.setBrush(QBrush(pixmap))
        elif count == 2:
            pixmap = QPixmap(':/images/hero_left_middle.png')
            self.setBrush(QBrush(pixmap))
        elif count == 3:
            pixmap = QPixmap(':/images/hero_left_2.png')
            self.setBrush(QBrush(pixmap))
        elif count == 4:
            pixmap = QPixmap(':/images/hero_left_middle.png')
            self.setBrush(QBrush(pixmap))

    def change_pic_up(self, count):
        if count == 1:
            pixmap = QPixmap(':/images/hero_up_1.png')
            self.setBrush(QBrush(pixmap))
        elif count == 2:
            pixmap = QPixmap(':/images/hero_up_middle.png')
            self.setBrush(QBrush(pixmap))
        elif count == 3:
            pixmap = QPixmap(':/images/hero_up_2.png')
            self.setBrush(QBrush(pixmap))
        elif count == 4:
            pixmap = QPixmap(':/images/hero_up_middle.png')
            self.setBrush(QBrush(pixmap))

    def change_pic_down(self, count):
        if count == 1:
            pixmap = QPixmap(':/images/hero_down_1.png')
            self.setBrush(QBrush(pixmap))
        elif count == 2:
            pixmap = QPixmap(':/images/hero_down_middle.png')
            self.setBrush(QBrush(pixmap))
        elif count == 3:
            pixmap = QPixmap(':/images/hero_down_2.png')
            self.setBrush(QBrush(pixmap))
        elif count == 4:
            pixmap = QPixmap(':/images/hero_down_middle.png')
            self.setBrush(QBrush(pixmap))

    def change_pic_die(self):
        pixmap = QPixmap(':/images/hero_dead.png')
        self.setBrush(QBrush(pixmap))


class Moving_Enemy(QGraphicsRectItem):
    def __init__(self, row, col, coords_explode, coords_double_explode, how_fast):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/images/enemy_up.png')
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))
        self.setZValue(50)
        self.how_fast = how_fast

        self.timer = QTimer()
        self.col = col
        self.row = row
        self.timer.timeout.connect(self.move)
        if how_fast == 1:
            self.timer.start(300)
        elif how_fast == 2:
            self.timer.start(600)
        elif how_fast == 3:
            self.timer.start(900)
        self.change_direction()
        self.coords_explode = coords_explode
        self.coords_double_explode = coords_double_explode

    def move(self):
        if self.direction == "down":
            pixmap = QPixmap(':/images/enemy_up.png')
            self.setBrush(QBrush(pixmap))
            if self.row < (NUM_COLS - 2) and self.col % 2 == 1:
                z = (str(self.row + 1) + '.' + str(self.col))
                if not self.check_collision(z):
                    self.moveBy(0, CELL_SIZE)
                    self.row += 1
                else:
                    self.moveBy(0, 0)
            self.change_direction()
        elif self.direction == "up":
            pixmap = QPixmap(':/images/enemy_down.png')
            self.setBrush(QBrush(pixmap))
            if self.row >= 2 and self.col % 2 == 1:
                z = (str(self.row - 1) + '.' + str(self.col))
                if not self.check_collision(z):
                    self.moveBy(0, -CELL_SIZE)
                    self.row -= 1
                else:
                    self.moveBy(0, 0)
            self.change_direction()
        elif self.direction == "right":
            pixmap = QPixmap(':/images/enemy_up.png')
            self.setBrush(QBrush(pixmap))
            if self.col < (NUM_ROWS - 2) and self.row % 2 == 1:
                z = (str(self.row) + '.' + str(self.col + 1))
                if not self.check_collision(z):
                    self.moveBy(CELL_SIZE, 0)
                    self.col += 1
            self.change_direction()
        elif self.direction == "left":
            pixmap = QPixmap(':/images/enemy_down.png')
            self.setBrush(QBrush(pixmap))
            if self.col >= 2 and self.row % 2 == 1:
                z = (str(self.row) + '.' + str(self.col - 1))
                if not self.check_collision(z):
                    self.moveBy(-CELL_SIZE, 0)
                    self.col -= 1
            self.change_direction()

    def change_pic_die(self):
        pixmap = QPixmap(':/images/enemy_dead.png')
        self.setBrush(QBrush(pixmap))

    def change_direction(self):
        self.direction = random.choice(["up", "down", "left", "right"])

    def check_collision(self, z):
        if z in self.coords_explode or z in self.coords_double_explode:
            return True
        return False


class Static_Enemy(QGraphicsRectItem):
    def __init__(self, row, col, coords_explode, coords_double_explode, how_fast):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/images/enemy_up2.png')
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))
        self.setZValue(50)
        self.how_fast = how_fast

        self.timer = QTimer()
        self.col = col
        self.row = row
        self.timer.timeout.connect(self.move)

        if how_fast == 1:
            self.timer.start(300)
        elif how_fast == 2:
            self.timer.start(600)
        elif how_fast == 3:
            self.timer.start(900)

        self.change_direction()
        self.coords_explode = coords_explode
        self.coords_double_explode = coords_double_explode

    def move(self):
        if self.direction == "right":
            pixmap = QPixmap(':/images/enemy_up2.png')
            self.setBrush(QBrush(pixmap))
            if self.col < (NUM_ROWS - 2) and self.row % 2 == 1:
                z = (str(self.row) + '.' + str(self.col + 1))
                if not self.check_collision(z):
                    self.moveBy(CELL_SIZE, 0)
                    self.col += 1
            self.change_direction()
        elif self.direction == "left":
            pixmap = QPixmap(':/images/enemy_down2.png')
            self.setBrush(QBrush(pixmap))
            if self.col >= 2 and self.row % 2 == 1:
                z = (str(self.row) + '.' + str(self.col - 1))
                if not self.check_collision(z):
                    self.moveBy(-CELL_SIZE, 0)
                    self.col -= 1
            self.change_direction()

    def change_direction(self):
        self.direction = random.choice(["left", "right"])

    def check_collision(self, z):
        if z in self.coords_explode or z in self.coords_double_explode:
            return True
        return False


class Tracking_Enemy(QGraphicsRectItem):
    def __init__(self, row, col, no_bricks, player, how_fast):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/images/enemy_up3.png')
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))
        self.setZValue(50)
        self.col = col
        self.row = row
        self.graph = no_bricks
        self.goals = []
        self.player = player
        self.how_fast = how_fast

        self.path_for_player = None

        self.current_path_index = 1

        self.timer = QTimer()
        self.timer.timeout.connect(self.move_enemy)

        if how_fast == 1:
            self.timer.start(600)
        elif how_fast == 2:
            self.timer.start(1200)
        elif how_fast == 3:
            self.timer.start(2000)

    def move_enemy(self):
        if self.path_for_player is not None:
            new_x, new_y = self.path_for_player[self.current_path_index].split('.')
            new_x = int(new_x)
            new_y = int(new_y)
            new_z = str(new_x) + '.' + str(new_y)

            if new_z == self.goals[-1]:
                x = int(self.player.pos().x() / CELL_SIZE) + 1
                y = int(self.player.pos().y() / CELL_SIZE) + 1
                z = str(x) + '.' + str(y)
                self.path_for_player = a_star(self.col, self.row, x, y, self.graph)
                self.current_path_index = 1
                self.goals.append(z)
                if self.path_for_player is not None:
                    new_x, new_y = self.path_for_player[self.current_path_index].split('.')
                    new_x = int(new_x)
                    new_y = int(new_y)
                else:
                    x = int(self.player.pos().x() / CELL_SIZE) + 1
                    y = int(self.player.pos().y() / CELL_SIZE) + 1
                    z = str(x) + '.' + str(y)
                    self.path_for_player = a_star(self.col, self.row, x, y, self.graph)
                    self.goals.append(z)

            if self.path_for_player is not None:
                old_x, old_y = self.path_for_player[self.current_path_index - 1].split('.')
                old_x = int(old_x)
                old_y = int(old_y)

                if new_x == old_x:
                    if new_y > old_y:
                        self.moveBy(0, CELL_SIZE)
                        self.row += 1
                    else:
                        self.moveBy(0, -CELL_SIZE)
                        self.row -= 1
                elif new_y == old_y:
                    if new_x > old_x:
                        self.moveBy(CELL_SIZE, 0)
                        self.col += 1
                    else:
                        self.moveBy(-CELL_SIZE, 0)
                        self.col -= 1

                self.current_path_index += 1

                if self.current_path_index % 2 == 0:
                    pixmap = QPixmap(':/images/enemy_up3.png')
                    self.setBrush(QBrush(pixmap))
                else:
                    pixmap = QPixmap(':/images/enemy_down3.png')
                    self.setBrush(QBrush(pixmap))

                if self.current_path_index >= len(self.path_for_player):
                    self.timer.stop()
                else:
                    if self.how_fast == 1:
                        self.timer.start(600)
                    elif self.how_fast == 2:
                        self.timer.start(1200)
                    elif self.how_fast == 3:
                        self.timer.start(2000)

        else:
            x = int(self.player.pos().x() / CELL_SIZE) + 1
            y = int(self.player.pos().y() / CELL_SIZE) + 1
            z = str(x) + '.' + str(y)
            self.path_for_player = a_star(self.col, self.row, x, y, self.graph)
            self.goals.append(z)


class Brick(QGraphicsRectItem):
    def __init__(self, row, col):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/images/brick.png')
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))
        self.row = row
        self.col = col


class Brick_Explode(QGraphicsRectItem):
    def __init__(self, row, col):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/images/brick_explode.png')
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))
        self.row = row
        self.col = col


class Brick_Double_Explode(QGraphicsRectItem):
    def __init__(self, row, col):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/images/brick_double_explode.png')
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))
        self.row = row
        self.col = col


class Fence(QGraphicsRectItem):
    def __init__(self, row, col):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/images/brick.png')
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))

        if row == NUM_ROWS - 2 and col == NUM_COLS - 1:
            pixmap = QPixmap(':/images/door.png')
            self.setBrush(QBrush(pixmap))


class Bomb(QGraphicsRectItem):
    def __init__(self, row, col):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/images/bomb.png')
        pixmap = pixmap.scaled(36, 36)
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))
        self.row = row
        self.col = col


class Explosion(QGraphicsRectItem):
    def __init__(self, row, col):
        super().__init__(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pixmap = QPixmap(':/images/fire.png')
        pixmap = pixmap.scaled(36, 36)
        self.setBrush(QBrush(pixmap))
        self.setPen(QPen(Qt.NoPen))


class Powerup(QGraphicsRectItem):
    def __init__(self, row, col, num):
        super().__init__()
        self.setRect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        self.setPen(QPen(Qt.NoPen))
        self.num = num

        if num == 1:
            pixmap = QPixmap(':/images/bombs.png')
            self.setBrush(QBrush(pixmap))

        elif num == 2:
            pixmap = QPixmap(':/images/flames.png')
            self.setBrush(QBrush(pixmap))

        elif num == 3:
            pixmap = QPixmap(':/images/speed.png')
            self.setBrush(QBrush(pixmap))

        elif num == 4:
            pixmap = QPixmap(':/images/wallpass.png')
            self.setBrush(QBrush(pixmap))

        elif num == 5:
            pixmap = QPixmap(':/images/detonator.png')
            self.setBrush(QBrush(pixmap))

        elif num == 6:
            pixmap = QPixmap(':/images/bombpass.png')
            self.setBrush(QBrush(pixmap))

        elif num == 7:
            pixmap = QPixmap(':/images/flamepass.png')
            self.setBrush(QBrush(pixmap))

        elif num == 8:
            pixmap = QPixmap(':/images/mystery.png')
            self.setBrush(QBrush(pixmap))


class Choice(QGraphicsRectItem):
    def __init__(self, row, col):
        super().__init__()
        self.setRect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, 5)
        self.setPen(QPen(Qt.NoPen))
        self.setBrush(Qt.red)
