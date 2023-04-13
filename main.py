import sys
import random
import images_rc
import items

from PyQt5.QtGui import QBrush, QPixmap, QPen
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer

CELL_SIZE = 36
NUM_ROWS = 23
NUM_COLS = 23
WINDOW_WIDTH = CELL_SIZE * NUM_COLS + 100
WINDOW_HEIGHT = CELL_SIZE * NUM_ROWS + 100


class Game(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        dark_green = QtGui.QColor(0, 100, 15)
        my_dark_green = QtGui.QBrush(dark_green)
        self.setBackgroundBrush(my_dark_green)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.player = None

        self.bricks = []
        self.fences = []
        self.bricks_to_remove = []
        self.str = []
        self.no_bricks = []
        self.no_bricks_for_static = []
        self.bricks_still = []
        self.enemies = []
        self.powerups = []
        self.bombs_on_board = []
        self.lines = []

        self.moves_right = 0
        self.moves_left = 0
        self.moves_up = 0
        self.moves_down = 0

        self.last_move = 0

        self.last_choice = None
        self.choice_bombs = items.Choice(-1.2, 0)
        self.choice_flames = items.Choice(-1.2, 1)
        self.choice_speed = items.Choice(-1.2, 2)
        self.choice_wallpass = items.Choice(-1.2, 3)
        self.choice_detonator = items.Choice(-1.2, 4)
        self.choice_bombpass = items.Choice(-1.2, 5)
        self.choice_flamepass = items.Choice(-1.2, 6)
        self.choice_mystery = items.Choice(-1.2, 7)

        self.path_for_player = None

        self.player = items.Player(1, 1)
        self.scene.addItem(self.player)

        self.begin_x = 0
        self.begin_y = 0
        self.end_x = 0
        self.end_y = 0

        for col in range(NUM_COLS):
            fence = items.Fence(0, col)
            fence_2 = items.Fence(NUM_ROWS - 1, col)
            self.fences.append(fence)
            self.fences.append(fence_2)
            self.scene.addItem(fence)
            self.scene.addItem(fence_2)

        for row in range(1, NUM_ROWS - 1):
            fence = items.Fence(row, 0)
            fence_2 = items.Fence(row, NUM_COLS - 1)
            self.fences.append(fence)
            self.fences.append(fence_2)
            self.scene.addItem(fence)
            self.scene.addItem(fence_2)

        self.coords_normal = []
        self.coords_explode = []
        self.coords_double_explode = []
        self.coords = []

        for x in range(1, NUM_ROWS - 1):
            for y in range(1, NUM_COLS - 1):
                zz = (str(x) + '.' + str(y))
                self.no_bricks.append(zz)
                if y % 2 == 0 and x % 2 != 0:
                    self.no_bricks_for_static.append(zz)
                if x % 2 == 0 and y % 2 == 0:
                    brick = items.Brick(x, y)
                    self.scene.addItem(brick)
                    self.bricks.append(brick)
                    z = (str(x) + '.' + str(y))
                    self.str.append(z)
                    self.coords_normal.append([x, y])
                    self.bricks_still.append(z)
                    self.coords.append([x, y])
                    self.no_bricks.remove(zz)
                elif random.random() < 0.3 and x > 2 and y > 2 and x < NUM_COLS - 1 and y < NUM_COLS - 1 \
                        and not (x % 2 != 0 and y % 2 != 0):
                    brick = items.Brick_Explode(x, y)
                    self.bricks.append(brick)
                    self.scene.addItem(brick)
                    z = (str(x) + '.' + str(y))
                    self.str.append(z)
                    self.coords_explode.append(z)
                    self.coords.append([x, y])
                    self.no_bricks.remove(z)
                elif random.random() < 0.15 and x > 2 and y > 2 and x < NUM_COLS - 1 and y < NUM_COLS - 1 \
                        and not (x % 2 != 0 and y % 2 != 0):
                    brick = items.Brick_Double_Explode(x, y)
                    self.bricks.append(brick)
                    self.scene.addItem(brick)
                    z = (str(x) + '.' + str(y))
                    self.str.append(z)
                    self.coords_double_explode.append(z)
                    self.coords.append([x, y])
                    self.no_bricks.remove(z)

        for i in range(3):
            z = random.choice(self.no_bricks)
            x, y = z.split('.')
            x = int(x)
            y = int(y)
            enemy = items.Moving_Enemy(x, y, self.coords_explode, self.coords_double_explode, i + 1)
            self.no_bricks.remove(z)
            self.scene.addItem(enemy)
            self.enemies.append(enemy)

        for i in range(1, 9):
            z = random.choice(self.no_bricks)
            x, y = z.split('.')
            x = int(x)
            y = int(y)
            powerup = items.Powerup(x, y, i)
            self.scene.addItem(powerup)
            self.powerups.append(powerup)

        for i in range(3):
            z = random.choice(self.no_bricks_for_static)
            x, y = z.split('.')
            x = int(x)
            y = int(y)
            enemy = items.Static_Enemy(x, y, self.coords_explode, self.coords_double_explode, i + 1)
            self.no_bricks_for_static.remove(z)
            self.scene.addItem(enemy)
            self.enemies.append(enemy)

        for i in range(3):
            z = random.choice(self.no_bricks)
            x, y = z.split('.')
            x = int(x)
            y = int(y)
            self.no_bricks.remove(z)
            enemy = items.Tracking_Enemy(x, y, self.no_bricks, self.player, i + 1)
            self.scene.addItem(enemy)
            self.enemies.append(enemy)

        self.timer_check_if_die_enemy = QTimer()
        self.timer_check_if_die_enemy.timeout.connect(self.check_if_die_from_enemy)
        self.timer_check_if_die_enemy.start(10)

    def add_explosion(self, bomb):
        row = int(bomb.row)
        col = int(bomb.col)

        if self.player.flames:
            add = self.player.explosions

        else:
            add = 0

        for i in range(row, row + 2 + add):
            j = col
            z = (str(i) + '.' + str(j))
            if (i == row or j == col) and i > 0 and j > 0 and i != NUM_COLS - 1 and j != NUM_ROWS - 1 \
                    and (i % 2 != 0 or j % 2 != 0):
                explosion = items.Explosion(i, j)
                self.scene.addItem(explosion)
                if self.check_if_die(explosion, self.player) and (
                        not self.player.flamepass and not self.player.mystery):
                    reply = QMessageBox.question(self, "Game over", "Bomb exploded on you!", QMessageBox.Ok,
                                                 QMessageBox.Ok)
                    if reply == QMessageBox.Ok:
                        QApplication.quit()

                QTimer.singleShot(2000, lambda item=explosion: self.scene.removeItem(item))

                if self.check_if_enemy_dies(explosion) != 0:
                    enemy = self.check_if_enemy_dies(explosion)
                    QTimer.singleShot(2000, lambda item=enemy: self.scene.removeItem(item))
                    self.enemies.remove(enemy)

                if z in self.coords_explode:
                    idx = self.str.index(z)
                    brick_to_remove = self.bricks[idx]
                    QTimer.singleShot(2500, lambda item=brick_to_remove: self.scene.removeItem(item))
                    self.bricks.pop(idx)
                    self.str.pop(idx)
                    self.coords_explode.remove(z)
                    self.coords.remove([i, j])

                elif z in self.coords_double_explode:
                    idx = self.str.index(z)
                    brick_to_remove = self.bricks[idx]
                    QTimer.singleShot(2500, lambda item=brick_to_remove: self.scene.removeItem(item))
                    self.bricks.pop(idx)
                    self.str.pop(idx)
                    self.coords_double_explode.remove(z)
                    self.coords.remove([i, j])

                    new_brick = items.Brick_Explode(i, j)
                    self.scene.addItem(new_brick)
                    self.bricks.append(new_brick)
                    self.str.append(z)
                    self.coords_explode.append(z)
                    self.coords.append([i, j])
            else:
                break

        for i in range(row, row - add - 2, -1):
            j = col
            if (i == row or j == col) and i > 0 and j > 0 and i != NUM_COLS - 1 and j != NUM_ROWS - 1 \
                    and (i % 2 != 0 or j % 2 != 0):
                explosion = items.Explosion(i, j)
                self.scene.addItem(explosion)
                if self.check_if_die(explosion, self.player) and (
                        not self.player.flamepass and not self.player.mystery):
                    reply = QMessageBox.question(self, "Game over", "Bomb exploded on you!", QMessageBox.Ok,
                                                 QMessageBox.Ok)
                    if reply == QMessageBox.Ok:
                        QApplication.quit()

                QTimer.singleShot(2000, lambda item=explosion: self.scene.removeItem(item))

                if self.check_if_enemy_dies(explosion) != 0:
                    enemy = self.check_if_enemy_dies(explosion)
                    QTimer.singleShot(2000, lambda item=enemy: self.scene.removeItem(item))
                    self.enemies.remove(enemy)

                z = (str(i) + '.' + str(j))
                if z in self.coords_explode:
                    idx = self.str.index(z)
                    brick_to_remove = self.bricks[idx]
                    QTimer.singleShot(2500, lambda item=brick_to_remove: self.scene.removeItem(item))
                    self.bricks.pop(idx)
                    self.str.pop(idx)
                    self.coords_explode.remove(z)
                    self.coords.remove([i, j])

                elif z in self.coords_double_explode:
                    idx = self.str.index(z)
                    brick_to_remove = self.bricks[idx]
                    QTimer.singleShot(2500, lambda item=brick_to_remove: self.scene.removeItem(item))
                    self.bricks.pop(idx)
                    self.str.pop(idx)
                    self.coords_double_explode.remove(z)
                    self.coords.remove([i, j])

                    new_brick = items.Brick_Explode(i, j)
                    self.scene.addItem(new_brick)
                    self.bricks.append(new_brick)
                    self.str.append(z)
                    self.coords_explode.append(z)
                    self.coords.append([i, j])
            else:
                break

        for j in range(col, col + 2 + add):
            i = row
            if (i == row or j == col) and i > 0 and j > 0 and i != NUM_COLS - 1 and j != NUM_ROWS - 1 \
                    and (i % 2 != 0 or j % 2 != 0):
                explosion = items.Explosion(i, j)
                self.scene.addItem(explosion)
                if self.check_if_die(explosion, self.player) and (
                        not self.player.flamepass and not self.player.mystery):
                    reply = QMessageBox.question(self, "Game over", "Bomb exploded on you!", QMessageBox.Ok,
                                                 QMessageBox.Ok)
                    if reply == QMessageBox.Ok:
                        QApplication.quit()

                QTimer.singleShot(2000, lambda item=explosion: self.scene.removeItem(item))

                if self.check_if_enemy_dies(explosion) != 0:
                    enemy = self.check_if_enemy_dies(explosion)
                    QTimer.singleShot(2000, lambda item=enemy: self.scene.removeItem(item))
                    self.enemies.remove(enemy)

                z = (str(i) + '.' + str(j))
                if z in self.coords_explode:
                    idx = self.str.index(z)
                    brick_to_remove = self.bricks[idx]
                    QTimer.singleShot(2500, lambda item=brick_to_remove: self.scene.removeItem(item))
                    self.bricks.pop(idx)
                    self.str.pop(idx)
                    self.coords_explode.remove(z)
                    self.coords.remove([i, j])

                elif z in self.coords_double_explode:
                    idx = self.str.index(z)
                    brick_to_remove = self.bricks[idx]
                    QTimer.singleShot(2500, lambda item=brick_to_remove: self.scene.removeItem(item))
                    self.bricks.pop(idx)
                    self.str.pop(idx)
                    self.coords_double_explode.remove(z)
                    self.coords.remove([i, j])

                    new_brick = items.Brick_Explode(i, j)
                    self.scene.addItem(new_brick)
                    self.bricks.append(new_brick)
                    self.str.append(z)
                    self.coords_explode.append(z)
                    self.coords.append([i, j])
            else:
                break

        for j in range(col, col - add - 2, -1):
            i = row
            if (i == row or j == col) and i > 0 and j > 0 and i != NUM_COLS - 1 and j != NUM_ROWS - 1 \
                    and (i % 2 != 0 or j % 2 != 0):
                explosion = items.Explosion(i, j)
                self.scene.addItem(explosion)
                if self.check_if_die(explosion, self.player) and (
                        not self.player.flamepass and not self.player.mystery):
                    reply = QMessageBox.question(self, "Game over", "Bomb exploded on you!", QMessageBox.Ok,
                                                 QMessageBox.Ok)
                    if reply == QMessageBox.Ok:
                        QApplication.quit()

                QTimer.singleShot(2000, lambda item=explosion: self.scene.removeItem(item))

                if self.check_if_enemy_dies(explosion) != 0:
                    enemy = self.check_if_enemy_dies(explosion)
                    QTimer.singleShot(2000, lambda item=enemy: self.scene.removeItem(item))
                    self.enemies.remove(enemy)

                z = (str(i) + '.' + str(j))
                if z in self.coords_explode:
                    idx = self.str.index(z)
                    brick_to_remove = self.bricks[idx]
                    QTimer.singleShot(2500, lambda item=brick_to_remove: self.scene.removeItem(item))
                    self.bricks.pop(idx)
                    self.str.pop(idx)
                    self.coords_explode.remove(z)
                    self.coords.remove([i, j])

                elif z in self.coords_double_explode:
                    idx = self.str.index(z)
                    brick_to_remove = self.bricks[idx]
                    QTimer.singleShot(2500, lambda item=brick_to_remove: self.scene.removeItem(item))
                    self.bricks.pop(idx)
                    self.str.pop(idx)
                    self.coords_double_explode.remove(z)
                    self.coords.remove([i, j])

                    new_brick = items.Brick_Explode(i, j)
                    self.scene.addItem(new_brick)
                    self.bricks.append(new_brick)
                    self.str.append(z)
                    self.coords_explode.append(z)
                    self.coords.append([i, j])
            else:
                break

    def keyPressEvent(self, event):
        row = self.player.y() / 36
        col = self.player.x() / 36
        x_pos = self.player.pos().x()
        y_pos = self.player.pos().y()
        self.bomb = items.Bomb(int(row) + 1, int(col) + 1)

        speed = 18

        if self.player.speed and (row.is_integer() and col.is_integer()):
            speed = 36
        elif self.player.speed and (not row.is_integer() and not col.is_integer()):
            speed = 54

        QTimer.singleShot(1, self.check_if_powerups)
        QTimer.singleShot(1, self.check_if_won)

        if self.player.bombpass and bool(self.bombs_on_board):
            self.bombs_on_board.clear()

        if event.key() == Qt.Key_Left and col >= 0.5:
            self.last_move = 1
            if not self.check_collision(x_pos - CELL_SIZE, y_pos) and \
                    not self.check_collision_with_bomb(x_pos - CELL_SIZE, y_pos):
                if self.moves_left % 4 == 0:
                    self.player.change_pic_left(1)

                elif self.moves_left % 4 == 1:
                    self.player.change_pic_left(2)

                elif self.moves_left % 4 == 2:
                    self.player.change_pic_left(3)

                elif self.moves_left % 4 == 3:
                    self.player.change_pic_left(4)

                self.player.moveBy(-speed, 0)
                self.moves_left = self.moves_left + 1

        elif event.key() == Qt.Key_Left and col < 0.5:
            self.last_move = 1
            self.player.moveBy(CELL_SIZE * NUM_COLS - 3 * CELL_SIZE, 0)

        elif event.key() == Qt.Key_Right and col < NUM_COLS - 3:
            self.last_move = 2
            if not self.check_collision(x_pos + CELL_SIZE, y_pos) and \
                    not self.check_collision_with_bomb(x_pos + CELL_SIZE, y_pos):
                if self.moves_right % 4 == 0:
                    self.player.change_pic_right(1)

                elif self.moves_right % 4 == 1:
                    self.player.change_pic_right(2)

                elif self.moves_right % 4 == 2:
                    self.player.change_pic_right(3)

                elif self.moves_right % 4 == 3:
                    self.player.change_pic_right(4)

                self.player.moveBy(speed, 0)
                self.moves_right = self.moves_right + 1

        elif event.key() == Qt.Key_Right and col == NUM_COLS - 3:
            self.last_move = 2
            self.player.moveBy(- CELL_SIZE * NUM_COLS + 3 * CELL_SIZE, 0)

        elif event.key() == Qt.Key_Up and row >= 0.5:
            self.last_move = 3
            if not self.check_collision(x_pos, y_pos - CELL_SIZE) and \
                    not self.check_collision_with_bomb(x_pos, y_pos - CELL_SIZE):
                if self.moves_up % 4 == 0:
                    self.player.change_pic_up(1)

                elif self.moves_up % 4 == 1:
                    self.player.change_pic_up(2)

                elif self.moves_up % 4 == 2:
                    self.player.change_pic_up(3)

                elif self.moves_up % 4 == 3:
                    self.player.change_pic_up(4)

                self.player.moveBy(0, -speed)
                self.moves_up = self.moves_up + 1

        elif event.key() == Qt.Key_Up and row < 0.5:
            self.last_move = 3
            self.player.moveBy(0, CELL_SIZE * NUM_ROWS - 3 * CELL_SIZE)

        elif event.key() == Qt.Key_Down and row < NUM_ROWS - 3:
            self.last_move = 4
            if not self.check_collision(x_pos, y_pos + CELL_SIZE) and \
                    not self.check_collision_with_bomb(x_pos, y_pos + CELL_SIZE):
                if self.moves_down % 4 == 0:
                    self.player.change_pic_down(1)

                elif self.moves_down % 4 == 1:
                    self.player.change_pic_down(2)

                elif self.moves_down % 4 == 2:
                    self.player.change_pic_down(3)

                elif self.moves_down % 4 == 3:
                    self.player.change_pic_down(4)

                self.player.moveBy(0, speed)
                self.moves_down = self.moves_down + 1

        elif event.key() == Qt.Key_Down and row == NUM_ROWS - 3:
            self.last_move = 4
            self.player.moveBy(0, - CELL_SIZE * NUM_ROWS + 3 * CELL_SIZE)

        elif event.key() == Qt.Key_Space:
            if not self.player.bombs:
                self.scene.addItem(self.bomb)
                QTimer.singleShot(1500, lambda item=self.bomb: self.bombs_on_board.append(item))
                if not self.player.detonator and not self.player.bombpass:
                    QTimer.singleShot(3000, lambda item=self.bomb: self.bombs_on_board.remove(item))
                    QTimer.singleShot(3000, lambda item=self.bomb: self.scene.removeItem(item))
                    QTimer.singleShot(3000, lambda item=self.bomb: self.add_explosion(item))

                elif not self.player.detonator and self.player.bombpass:
                    QTimer.singleShot(3000, lambda item=self.bomb: self.scene.removeItem(item))
                    QTimer.singleShot(3000, lambda item=self.bomb: self.add_explosion(item))

            elif self.player.bombs:
                if self.last_move == 1:
                    for i in range(int(col) + 1, int(col) + 1 + self.player.bombs_add):
                        self.one_of_bombs = items.Bomb(row + 1, i)
                        QTimer.singleShot(1, lambda item=self.one_of_bombs: self.bomb_explosion(item))

                elif self.last_move == 2:
                    for i in range(int(col) + 1, int(col) + 1 - self.player.bombs_add, -1):
                        self.one_of_bombs = items.Bomb(row + 1, i)
                        QTimer.singleShot(1, lambda item=self.one_of_bombs: self.bomb_explosion(item))

                elif self.last_move == 3:
                    for i in range(int(row) + 1, int(row) + 1 + self.player.bombs_add):
                        self.one_of_bombs =items. Bomb(i, col + 1)
                        QTimer.singleShot(1, lambda item=self.one_of_bombs: self.bomb_explosion(item))

                if self.last_move == 4:
                    for i in range(int(row) + 1, int(row) + 1 - self.player.bombs_add, -1):
                        self.one_of_bombs = items.Bomb(i, col + 1)
                        QTimer.singleShot(1, lambda item=self.one_of_bombs: self.bomb_explosion(item))

        elif event.key() == Qt.Key_B and self.player.detonator and bool(self.bombs_on_board):
            bomb = self.bombs_on_board[-1]
            if len(self.bombs_on_board) != 0:
                QTimer.singleShot(1000, lambda item=bomb: self.bombs_on_board.remove(item))
            QTimer.singleShot(1000, lambda item=bomb: self.scene.removeItem(item))
            QTimer.singleShot(1000, lambda item=bomb: self.add_explosion(item))

        if self.check_collision(self.player.x(), self.player.y()):
            self.player.setPos(x_pos, y_pos)

        if self.check_collision_with_bomb(self.player.x(), self.player.y()):
            self.player.setPos(x_pos, y_pos)

    def mousePressEvent(self, event):
        x = int((event.pos().x() - 50) / CELL_SIZE)
        y = int((event.pos().y() - 50) / CELL_SIZE)
        self.begin_x = x
        self.begin_y = y

        if y <= 0:
            if x == 0 and self.player.bombs_collected:
                self.player.bombs = True
                if self.last_choice == self.choice_bombs:
                    self.player.bombs = False
                    self.last_choice = None
                    self.scene.removeItem(self.choice_bombs)
                else:
                    self.scene.addItem(self.choice_bombs)
                    if self.last_choice is not None:
                        self.scene.removeItem(self.last_choice)
                    self.last_choice = self.choice_bombs

                self.player.flames = False
                self.player.speed = False
                self.player.wallpass = False
                self.player.detonator = False
                self.player.bombpass = False
                self.player.flamepass = False
                self.player.mystery = False

            elif x == 1 and self.player.flames_collected:
                self.player.bombs = False

                self.player.flames = True

                if self.last_choice == self.choice_flames:
                    self.player.flames = False
                    self.last_choice = None
                    self.scene.removeItem(self.choice_flames)
                else:
                    self.scene.addItem(self.choice_flames)
                    if self.last_choice is not None:
                        self.scene.removeItem(self.last_choice)
                    self.last_choice = self.choice_flames

                self.player.speed = False
                self.player.wallpass = False
                self.player.detonator = False
                self.player.bombpass = False
                self.player.flamepass = False
                self.player.mystery = False

            elif x == 2 and self.player.speed_collected:
                self.player.bombs = False
                self.player.flames = False

                self.player.speed = True
                if self.last_choice == self.choice_speed:
                    self.player.speed = False
                    self.last_choice = None
                    self.scene.removeItem(self.choice_speed)
                else:
                    self.scene.addItem(self.choice_speed)
                    if self.last_choice is not None:
                        self.scene.removeItem(self.last_choice)
                    self.last_choice = self.choice_speed

                self.player.wallpass = False
                self.player.detonator = False
                self.player.bombpass = False
                self.player.flamepass = False
                self.player.mystery = False

            elif x == 3 and self.player.wallpass_collected:
                self.player.bombs = False
                self.player.flames = False
                self.player.speed = False

                self.player.wallpass = True
                if self.last_choice == self.choice_wallpass:
                    self.player.wallpass = False
                    self.last_choice = None
                    self.scene.removeItem(self.choice_wallpass)
                else:
                    self.scene.addItem(self.choice_wallpass)
                    if self.last_choice is not None:
                        self.scene.removeItem(self.last_choice)
                    self.last_choice = self.choice_wallpass

                self.player.detonator = False
                self.player.bombpass = False
                self.player.flamepass = False
                self.player.mystery = False

            elif x == 4 and self.player.detonator_collected:
                self.player.bombs = False
                self.player.flames = False
                self.player.speed = False
                self.player.wallpass = False

                self.player.detonator = True
                if self.last_choice == self.choice_detonator:
                    self.player.detonator = False
                    self.last_choice = None
                    self.scene.removeItem(self.choice_detonator)
                else:
                    self.scene.addItem(self.choice_detonator)
                    if self.last_choice is not None:
                        self.scene.removeItem(self.last_choice)
                    self.last_choice = self.choice_detonator

                self.player.bombpass = False
                self.player.flamepass = False
                self.player.mystery = False

            elif x == 5 and self.player.bombpass_collected:
                self.player.bombs = False
                self.player.flames = False
                self.player.speed = False
                self.player.wallpass = False
                self.player.detonator = False

                self.player.bombpass = True
                if self.last_choice == self.choice_bombpass:
                    self.player.bombpass = False
                    self.last_choice = None
                    self.scene.removeItem(self.choice_bombpass)
                else:
                    self.scene.addItem(self.choice_bombpass)
                    if self.last_choice is not None:
                        self.scene.removeItem(self.last_choice)
                    self.last_choice = self.choice_bombpass

                self.player.flamepass = False
                self.player.mystery = False

            elif x == 6 and self.player.flamepass_collected:
                self.player.bombs = False
                self.player.flames = False
                self.player.speed = False
                self.player.wallpass = False
                self.player.detonator = False
                self.player.bombpass = False

                self.player.flamepass = True
                if self.last_choice == self.choice_flamepass:
                    self.player.flamepass = False
                    self.last_choice = None
                    self.scene.removeItem(self.choice_flamepass)
                else:
                    self.scene.addItem(self.choice_flamepass)
                    if self.last_choice is not None:
                        self.scene.removeItem(self.last_choice)
                    self.last_choice = self.choice_flamepass

                self.player.mystery = False

            elif x == 7 and self.player.mystery_collected:
                self.player.bombs = False
                self.player.flames = False
                self.player.speed = False
                self.player.wallpass = False
                self.player.detonator = False
                self.player.bombpass = False
                self.player.flamepass = False

                self.player.mystery = True
                if self.last_choice == self.choice_mystery:
                    self.player.mystery = False
                    self.last_choice = None
                    self.scene.removeItem(self.choice_mystery)
                else:
                    self.scene.addItem(self.choice_mystery)
                    if self.last_choice is not None:
                        self.scene.removeItem(self.last_choice)
                    self.last_choice = self.choice_mystery

        if event.button() == Qt.LeftButton:
            self._start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = event.pos() - self._start
            self._start = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y())
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ArrowCursor)
            x = int((event.pos().x() - 50) / CELL_SIZE)
            y = int((event.pos().y() - 50) / CELL_SIZE)
            self.end_x = x
            self.end_y = y

            p_x = self.player.pos().x() / CELL_SIZE
            p_y = self.player.pos().y() / CELL_SIZE

            if not p_x.is_integer():
                self.player.moveBy(18, 0)
            elif not p_y.is_integer():
                self.player.moveBy(0, 18)

            self.path_for_player = items.a_star(int(self.player.pos().x() / CELL_SIZE) + 1,
                                          int(self.player.pos().y() / CELL_SIZE) + 1, self.end_x, self.end_y,
                                          self.no_bricks)

            pen = QPen(Qt.red, 3)
            if bool(self.path_for_player):
                for i in range(1, len(self.path_for_player)):
                    start_x, start_y = self.path_for_player[i - 1].split('.')
                    start_x = int(start_x)
                    start_y = int(start_y)
                    end_x, end_y = self.path_for_player[i].split('.')
                    end_x = int(end_x)
                    end_y = int(end_y)
                    line = QGraphicsLineItem(start_x * CELL_SIZE + CELL_SIZE / 2,
                                             start_y * CELL_SIZE + CELL_SIZE / 2,
                                             end_x * CELL_SIZE + CELL_SIZE / 2,
                                             end_y * CELL_SIZE + CELL_SIZE / 2)

                    line.setPen(pen)
                    self.scene.addItem(line)
                    self.lines.append(line)

            event.accept()

        self.current_path_index = 1
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_player)
        self.timer.start(500)

    def move_player(self):
        QTimer.singleShot(1, self.check_if_powerups)
        QTimer.singleShot(1, self.check_if_won)
        if self.path_for_player is not None:
            new_x, new_y = self.path_for_player[self.current_path_index].split('.')
            new_x = int(new_x)
            new_y = int(new_y)
            old_x, old_y = self.path_for_player[self.current_path_index - 1].split('.')
            old_x = int(old_x)
            old_y = int(old_y)

            if new_x == old_x:
                if new_y > old_y:
                    if self.moves_down % 4 == 0:
                        self.player.change_pic_down(1)

                    elif self.moves_down % 4 == 1:
                        self.player.change_pic_down(2)

                    elif self.moves_down % 4 == 2:
                        self.player.change_pic_down(3)

                    elif self.moves_down % 4 == 3:
                        self.player.change_pic_down(4)

                    self.player.moveBy(0, CELL_SIZE)
                    self.moves_down = self.moves_down + 1
                else:
                    if self.moves_up % 4 == 0:
                        self.player.change_pic_up(1)

                    elif self.moves_up % 4 == 1:
                        self.player.change_pic_up(2)

                    elif self.moves_up % 4 == 2:
                        self.player.change_pic_up(3)

                    elif self.moves_up % 4 == 3:
                        self.player.change_pic_up(4)

                    self.player.moveBy(0, -CELL_SIZE)
                    self.moves_up = self.moves_up + 1
            elif new_y == old_y:
                if new_x > old_x:
                    if self.moves_right % 4 == 0:
                        self.player.change_pic_right(1)

                    elif self.moves_right % 4 == 1:
                        self.player.change_pic_right(2)

                    elif self.moves_right % 4 == 2:
                        self.player.change_pic_right(3)

                    elif self.moves_right % 4 == 3:
                        self.player.change_pic_right(4)

                    self.player.moveBy(CELL_SIZE, 0)
                    self.moves_right = self.moves_right + 1
                else:
                    if self.moves_left % 4 == 0:
                        self.player.change_pic_left(1)

                    elif self.moves_left % 4 == 1:
                        self.player.change_pic_left(2)

                    elif self.moves_left % 4 == 2:
                        self.player.change_pic_left(3)

                    elif self.moves_left % 4 == 3:
                        self.player.change_pic_left(4)

                    self.player.moveBy(-CELL_SIZE, 0)
                    self.moves_left = self.moves_left + 1

            self.scene.removeItem(self.lines[self.current_path_index - 1])
            self.current_path_index += 1
            if self.current_path_index >= len(self.path_for_player):
                self.timer.stop()
                self.lines.clear()
            else:
                self.timer.start(500)

    def check_collision(self, x, y):
        for brick in self.bricks:
            if brick.collidesWithItem(self.player) and isinstance(brick, items.Brick):
                return True
            if brick.collidesWithItem(self.player) and \
                    (isinstance(brick, items.Brick_Explode) or isinstance(brick, items.Brick_Double_Explode)):
                if self.player.wallpass:
                    return False
                else:
                    return True
        return False

    def check_collision_with_bomb(self, x, y):
        if bool(self.bombs_on_board):
            for bomb in self.bombs_on_board:
                if bomb.sceneBoundingRect().contains(self.player.sceneBoundingRect()):
                    return True
        return False

    def check_if_die(self, explosion, player):
        if explosion.sceneBoundingRect().contains(player.sceneBoundingRect()):
            return True
        else:
            return False

    def check_if_die_from_enemy(self):
        for enemy in self.enemies:
            if enemy.sceneBoundingRect().contains(self.player.sceneBoundingRect()) and not self.player.mystery:
                self.player.change_pic_die()
                reply = QMessageBox.question(self, "Game over", "You touched an enemy!", QMessageBox.Ok,
                                             QMessageBox.Ok)
                if reply == QMessageBox.Ok:
                    QApplication.quit()

    def check_if_enemy_dies(self, explosion):
        for enemy in self.enemies:
            if explosion.sceneBoundingRect().contains(enemy.sceneBoundingRect()):
                return enemy
        return 0

    def bomb_explosion(self, bomb):
        self.scene.addItem(bomb)
        QTimer.singleShot(1500, lambda item=bomb: self.bombs_on_board.append(item))
        QTimer.singleShot(3000, lambda item=bomb: self.bombs_on_board.remove(item))
        QTimer.singleShot(3000, lambda item=bomb: self.scene.removeItem(item))
        QTimer.singleShot(3000, lambda item=bomb: self.add_explosion(item))

    def check_if_won(self):
        y = int(self.player.y() / CELL_SIZE)
        x = int(self.player.x() / CELL_SIZE)

        if x == 22 and y == 22 and not bool(self.enemies):
            reply = QMessageBox.question(self, "Game finished", "You won!", QMessageBox.Ok,
                                         QMessageBox.Ok)
            if reply == QMessageBox.Ok:
                QApplication.quit()

    def check_if_powerups(self):
        for powerup in self.powerups:
            if powerup.sceneBoundingRect().contains(self.player.sceneBoundingRect()):
                if powerup.num == 1:
                    self.player.bombs_collected = True
                    self.scene.removeItem(powerup)
                    self.player.bombs_add = self.player.bombs_add + 1
                    new_powerup = items.Powerup(-1, 0, 1)
                    self.scene.addItem(new_powerup)
                    self.powerups.remove(powerup)

                    z = random.choice(self.no_bricks)
                    x, y = z.split('.')
                    x = int(x)
                    y = int(y)
                    pow = items.Powerup(x, y, 1)
                    self.scene.addItem(pow)
                    self.no_bricks.remove(z)
                    self.powerups.append(pow)
                elif powerup.num == 2:
                    self.player.flames_collected = True
                    self.scene.removeItem(powerup)
                    self.player.explosions = self.player.explosions + 1
                    new_powerup = items.Powerup(-1, 1, 2)
                    self.scene.addItem(new_powerup)
                    self.powerups.remove(powerup)

                    z = random.choice(self.no_bricks)
                    x, y = z.split('.')
                    x = int(x)
                    y = int(y)
                    pow = items.Powerup(x, y, 2)
                    self.scene.addItem(pow)
                    self.no_bricks.remove(z)
                    self.powerups.append(pow)
                elif powerup.num == 3:
                    self.player.speed_collected = True
                    self.scene.removeItem(powerup)
                    self.powerups.remove(powerup)
                    new_powerup = items.Powerup(-1, 2, 3)
                    self.scene.addItem(new_powerup)
                elif powerup.num == 4:
                    self.player.wallpass_collected = True
                    self.scene.removeItem(powerup)
                    self.powerups.remove(powerup)
                    new_powerup = items.Powerup(-1, 3, 4)
                    self.scene.addItem(new_powerup)
                elif powerup.num == 5:
                    self.player.detonator_collected = True
                    self.scene.removeItem(powerup)
                    self.powerups.remove(powerup)
                    new_powerup = items.Powerup(-1, 4, 5)
                    self.scene.addItem(new_powerup)
                elif powerup.num == 6:
                    self.player.bombpass_collected = True
                    self.scene.removeItem(powerup)
                    self.powerups.remove(powerup)
                    new_powerup = items.Powerup(-1, 5, 6)
                    self.scene.addItem(new_powerup)
                elif powerup.num == 7:
                    self.player.flamepass_collected = True
                    self.scene.removeItem(powerup)
                    self.powerups.remove(powerup)
                    new_powerup = items.Powerup(-1, 6, 7)
                    self.scene.addItem(new_powerup)
                elif powerup.num == 8:
                    self.player.mystery_collected = True
                    self.scene.removeItem(powerup)
                    self.powerups.remove(powerup)
                    new_powerup = items.Powerup(-1, 7, 8)
                    self.scene.addItem(new_powerup)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = Game()
    game.show()
    sys.exit(app.exec_())
