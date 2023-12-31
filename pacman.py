import pygame
import sys
import random
from pygame.math import Vector2 as vec

# Constants
START = 0
PLAY = 1
GAMEOVER = 2
WIN = 3

# Settings
WIDTH = 610
HEIGHT = 670
GAP = 50
MAZE_WIDTH = WIDTH - GAP
MAZE_HEIGHT = HEIGHT - GAP
ROWS = 30
COLS = 28
FONT_SIZE = 16
FONT_NAME = "arial black"

# Colours
BLACK = (0, 0, 0)
RED = (208, 22, 22)
GRAY = (107, 107, 107)
BLUE = (64, 64, 255)
GREEN = (64, 255, 128)
ORANGE = (215, 159, 33)
WHITE = (255, 255, 255)
PLAYER_COLOUR = (190, 194, 15)

# Enemy Personality
DIZZY = 1
SLOW = 2
SCARE = 3
FAST = 4

pygame.init()
pygame.display.set_caption("Pac-Man")
programIcon = pygame.image.load("pacman.png")
pygame.display.set_icon(programIcon)

###########################################################
#                         App Class                       #
###########################################################
class App:
    def __init__(self):
        self.Screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.Clock = pygame.time.Clock()
        self.RUNNING = True
        self.STATE = START
        self.CELL_WIDTH = MAZE_WIDTH // COLS
        self.CELL_HEIGHT = MAZE_HEIGHT // ROWS
        self.Walls = []
        self.Coins = []
        self.Enemies = []
        self.EnemyPos = []
        self.PlayerPos = None
        self.Load()
        self.player = Player(self, vec(self.PlayerPos))
        self.MakeEnemy()

    def RunGame(self):
        while self.RUNNING:
            if self.STATE == START:
                self.StartGame()
                self.StartDraw()
            elif self.STATE == PLAY:
                self.Play()
                self.PlayUpdate()
                self.PlayDraw()
            elif self.STATE == GAMEOVER:
                self.GameOver()
                self.GameOverDraw()
            elif self.STATE == WIN:
                self.Win()
                self.WinDraw()
            else:
                self.RUNNING = False
            self.Clock.tick(60)
        pygame.quit()
        sys.exit()

    def DrawText(self, words, screen, pos, size, colour, font_name, centered=False):
        Font = pygame.font.SysFont(font_name, size)
        Text = Font.render(words, False, colour)
        TextSize = Text.get_size()
        if centered:
            pos[0] = pos[0] - TextSize[0] // 2
            pos[1] = pos[1] - TextSize[1] // 2
        screen.blit(Text, pos)

    def Load(self):
        self.BG = pygame.image.load("maze.png")
        self.BG = pygame.transform.scale(self.BG, (MAZE_WIDTH, MAZE_HEIGHT))
        with open("walls.txt", "r") as f:
            for y, l in enumerate(f):
                for x, c in enumerate(l):
                    if c == "1":
                        self.Walls.append(vec(x, y))
                    elif c == "C":
                        self.Coins.append(vec(x, y))
                    elif c == "P":
                        self.PlayerPos = [x, y]
                    elif c in ["2", "3", "4", "5"]:
                        self.EnemyPos.append([x, y])
                    elif c == "B":
                        pygame.draw.rect(
                            self.BG,
                            BLACK,
                            (
                                x * self.CELL_WIDTH,
                                y * self.CELL_HEIGHT,
                                self.CELL_WIDTH,
                                self.CELL_HEIGHT,
                            )
                        )

    def MakeEnemy(self):
        for i, p in enumerate(self.EnemyPos):
            self.Enemies.append(Enemy(self, vec(p), i))

    def ResetGame(self):
        self.player.Heart = 3
        self.player.Score = 0
        self.player.GridPos = vec(self.player.StartPos)
        self.player.PixPos = self.player.GetPos()
        self.player.Dir *= 0
        for enemy in self.Enemies:
            enemy.GridPos = vec(enemy.StartPos)
            enemy.PixPos = enemy.GetPos()
            enemy.Dir *= 0
        self.Coins = []
        with open("walls.txt", "r") as f:
            for y, l in enumerate(f):
                for x, c in enumerate(l):
                    if c == "C":
                        self.Coins.append(vec(x, y))
        self.STATE = PLAY

    def StartGame(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUNNING = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.STATE = PLAY

    def StartDraw(self):
        self.Screen.fill(BLACK)
        self.DrawText(
            "PRESS SPACE TO START",
            self.Screen,
            [WIDTH // 2, HEIGHT // 2],
            FONT_SIZE,
            GREEN,
            FONT_NAME,
            centered=True
        )
        pygame.display.update()

    def Play(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUNNING = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.Move(vec(-1, 0))
                if event.key == pygame.K_RIGHT:
                    self.player.Move(vec(1, 0))
                if event.key == pygame.K_UP:
                    self.player.Move(vec(0, -1))
                if event.key == pygame.K_DOWN:
                    self.player.Move(vec(0, 1))

    def PlayUpdate(self):
        self.player.PlayerUpdate()
        for enemy in self.Enemies:
            enemy.EnemyUpdate()
        for enemy in self.Enemies:
            if enemy.GridPos == self.player.GridPos:
                self.RemoveHeart()
        if len(self.Coins) == 0:
            self.STATE = WIN

    def PlayDraw(self):
        self.Screen.fill(BLACK)
        self.Screen.blit(self.BG, (GAP // 2, GAP // 2))
        self.DrawCoin()
        self.DrawText(
            "SCORE: {}".format(self.player.Score),
            self.Screen,
            [10, 0],
            FONT_SIZE,
            WHITE,
            FONT_NAME,
        )        
        self.DrawText(
            "COINS: {}".format(len(self.Coins)),
            self.Screen,
            [250, 0],
            FONT_SIZE,
            WHITE,
            FONT_NAME,
        )
        
        self.player.DrawPlayer()
        for enemy in self.Enemies:
            enemy.DrawEnemy()
        pygame.display.update()

    def RemoveHeart(self):
        self.player.Heart -= 1
        if self.player.Heart == 0:
            self.STATE = GAMEOVER
        else:
            self.player.GridPos = vec(self.player.StartPos)
            self.player.PixPos = self.player.GetPos()
            self.player.Dir *= 0
            for enemy in self.Enemies:
                enemy.GridPos = vec(enemy.StartPos)
                enemy.PixPos = enemy.GetPos()
                enemy.Dir *= 0

    def DrawCoin(self):
        for coin in self.Coins:
            pygame.draw.circle(
                self.Screen,
                GRAY,
                (
                    int(coin.x * self.CELL_WIDTH) + self.CELL_WIDTH // 2 + GAP // 2,
                    int(coin.y * self.CELL_HEIGHT) + self.CELL_HEIGHT // 2 + GAP // 2,
                ),
                5
            )

    def GameOver(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUNNING = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.ResetGame()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.RUNNING = False

    def Win(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUNNING = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.ResetGame()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.RUNNING = False

    def WinDraw(self):
        self.Screen.fill(BLACK)
        self.DrawText(
            "YOU WIN!",
            self.Screen,
            [WIDTH // 2, 100],
            FONT_SIZE * 2,
            GREEN,
            FONT_NAME,
            centered=True,
        )
        self.DrawText(
            "Press SPACE to Start",
            self.Screen,
            [WIDTH // 2, HEIGHT // 2],
            FONT_SIZE,
            WHITE,
            FONT_NAME,
            centered=True,
        )
        self.DrawText(
            "Press the ESC to Exit",
            self.Screen,
            [WIDTH // 2, HEIGHT // 1.5],
            FONT_SIZE,
            WHITE,
            FONT_NAME,
            centered=True,
        )
        pygame.display.update()
        
    def GameOverDraw(self):
        self.Screen.fill(BLACK)
        self.DrawText(
            "GAME OVER",
            self.Screen,
            [WIDTH // 2, 100],
            FONT_SIZE * 2,
            RED,
            FONT_NAME,
            centered=True,
        )
        self.DrawText(
            "Press SPACE to Start",
            self.Screen,
            [WIDTH // 2, HEIGHT // 2],
            FONT_SIZE,
            WHITE,
            FONT_NAME,
            centered=True,
        )
        self.DrawText(
            "Press the ESC to Exit",
            self.Screen,
            [WIDTH // 2, HEIGHT // 1.5],
            FONT_SIZE,
            WHITE,
            FONT_NAME,
            centered=True,
        )
        pygame.display.update()


###########################################################
#                       Player Class                      #
###########################################################
class Player:
    def __init__(self, app, pos):
        self.app = app
        self.StartPos = [pos.x, pos.y]
        self.GridPos = pos
        self.PixPos = self.GetPos()
        self.Dir = vec(1, 0)
        self.SaveDir = None
        self.Movable = True
        self.Score = 0
        self.Speed = 2
        self.Heart = 3

    def PlayerUpdate(self):
        if self.Movable:
            self.PixPos += self.Dir * self.Speed
        if self.TimeToMove():
            if self.SaveDir != None:
                self.Dir = self.SaveDir
            self.Movable = self.CanMove()
        self.GridPos[0] = (
            self.PixPos[0] - GAP + self.app.CELL_WIDTH // 2
        ) // self.app.CELL_WIDTH + 1
        self.GridPos[1] = (
            self.PixPos[1] - GAP + self.app.CELL_HEIGHT // 2
        ) // self.app.CELL_HEIGHT + 1
        if self.OnCoin():
            self.EatCoin()

    def DrawPlayer(self):
        pygame.draw.circle(
            self.app.Screen,
            PLAYER_COLOUR,
            (int(self.PixPos.x), int(self.PixPos.y)),
            self.app.CELL_WIDTH // 2 - 2,
        )
        for x in range(self.Heart):
            pygame.draw.circle(
                self.app.Screen, PLAYER_COLOUR, (30 + 20 * x, HEIGHT - 15), 7
            )

    def OnCoin(self):
        if self.GridPos in self.app.Coins:
            if int(self.PixPos.x + GAP // 2) % self.app.CELL_WIDTH == 0:
                if self.Dir == vec(1, 0) or self.Dir == vec(-1, 0):
                    return True
            if int(self.PixPos.y + GAP // 2) % self.app.CELL_HEIGHT == 0:
                if self.Dir == vec(0, 1) or self.Dir == vec(0, -1):
                    return True
        return False

    def EatCoin(self):
        self.app.Coins.remove(self.GridPos)
        self.Score += 1

    def Move(self, dir):
        self.SaveDir = dir

    def GetPos(self):
        return vec(
            (self.GridPos[0] * self.app.CELL_WIDTH)
            + GAP // 2
            + self.app.CELL_WIDTH // 2,
            (self.GridPos[1] * self.app.CELL_HEIGHT)
            + GAP // 2
            + self.app.CELL_HEIGHT // 2,
        )

    def TimeToMove(self):
        if int(self.PixPos.x + GAP // 2) % self.app.CELL_WIDTH == 0:
            if self.Dir == vec(1, 0) or self.Dir == vec(-1, 0) or self.Dir == vec(0, 0):
                return True
        if int(self.PixPos.y + GAP // 2) % self.app.CELL_HEIGHT == 0:
            if self.Dir == vec(0, 1) or self.Dir == vec(0, -1) or self.Dir == vec(0, 0):
                return True

    def CanMove(self):
        for i in self.app.Walls:
            if vec(self.GridPos + self.Dir) == i:
                return False
        return True


###########################################################
#                         Enamy Class                     #
###########################################################
class Enemy:
    def __init__(self, app, pos, number):
        self.app = app
        self.GridPos = pos
        self.StartPos = [pos.x, pos.y]
        self.PixPos = self.GetPos()
        self.Number = number
        self.Colour = self.EnemyColor()
        self.Dir = vec(0, 0)
        self.Kind = self.EnemyKind()
        self.Target = None
        self.Speed = self.SetSpeed()

    def EnemyUpdate(self):
        self.Target = self.SetTarget()
        if self.Target != self.GridPos:
            self.PixPos += self.Dir * self.Speed
            if self.TimeToMove():
                self.Move()
        self.GridPos[0] = (
            self.PixPos[0] - GAP + self.app.CELL_WIDTH // 2
        ) // self.app.CELL_WIDTH + 1
        self.GridPos[1] = (
            self.PixPos[1] - GAP + self.app.CELL_HEIGHT // 2
        ) // self.app.CELL_HEIGHT + 1

    def DrawEnemy(self):
        pygame.draw.circle(
            self.app.Screen,
            self.Colour,
            (int(self.PixPos.x), int(self.PixPos.y)),
            (int(self.app.CELL_WIDTH // 2.3)),
        )

    def SetSpeed(self):
        if self.Kind in [FAST, SCARE]:
            return 2
        else:
            return 1

    def SetTarget(self):
        if self.Kind == FAST or self.Kind == SLOW:
            return self.app.player.GridPos
        else:
            if (
                self.app.player.GridPos[0] > COLS // 2
                and self.app.player.GridPos[1] > ROWS // 2
            ):
                return vec(1, 1)
            if (
                self.app.player.GridPos[0] > COLS // 2
                and self.app.player.GridPos[1] < ROWS // 2
            ):
                return vec(1, ROWS - 2)
            if (
                self.app.player.GridPos[0] < COLS // 2
                and self.app.player.GridPos[1] > ROWS // 2
            ):
                return vec(COLS - 2, 1)
            else:
                return vec(COLS - 2, ROWS - 2)

    def TimeToMove(self):
        if int(self.PixPos.x + GAP // 2) % self.app.CELL_WIDTH == 0:
            if self.Dir == vec(1, 0) or self.Dir == vec(-1, 0) or self.Dir == vec(0, 0):
                return True
        if int(self.PixPos.y + GAP // 2) % self.app.CELL_HEIGHT == 0:
            if self.Dir == vec(0, 1) or self.Dir == vec(0, -1) or self.Dir == vec(0, 0):
                return True
        return False

    def Move(self):
        if self.Kind == DIZZY:
            self.Dir = self.GetRandomDir()
        if self.Kind == SLOW:
            self.Dir = self.GetPathDir(self.Target)
        if self.Kind == SCARE:
            self.Dir = self.GetPathDir(self.Target)
        if self.Kind == FAST:
            self.Dir = self.GetPathDir(self.Target)

    def GetPathDir(self, target):
        NextCell = self.FindNextCell(target)
        x = NextCell[0] - self.GridPos[0]
        y = NextCell[1] - self.GridPos[1]
        return vec(x, y)

    def FindNextCell(self, target):
        Path = self.FindShortestPath(
            [int(self.GridPos.x), int(self.GridPos.y)], [int(target[0]), int(target[1])]
        )
        return Path[1]

    def FindShortestPath(self, start, target):
        Grid = [[0 for x in range(28)] for x in range(30)]
        for i in self.app.Walls:
            if i.x < 28 and i.y < 30:
                Grid[int(i.y)][int(i.x)] = 1
        Queue = [start]
        Path = []
        Visited = []
        while Queue:
            Current = Queue[0]
            Queue.remove(Queue[0])
            Visited.append(Current)
            if Current == target:
                break
            else:
                Neighbour = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for i in Neighbour:
                    if i[0] + Current[0] >= 0 and i[0] + Current[0] < len(Grid[0]):
                        if i[1] + Current[1] >= 0 and i[1] + Current[1] < len(Grid):
                            Next = [
                                i[0] + Current[0],
                                i[1] + Current[1],
                            ]
                            if Next not in Visited:
                                if Grid[Next[1]][Next[0]] != 1:
                                    Queue.append(Next)
                                    Path.append({"Current": Current, "Next": Next})
        ShortPath = [target]
        while target != start:
            for i in Path:
                if i["Next"] == target:
                    target = i["Current"]
                    ShortPath.insert(0, i["Current"])
        return ShortPath

    def GetRandomDir(self):
        while True:
            n = random.randint(-2, 1)
            if n == -2:
                x = 1
                y = 0
            elif n == -1:
                x = 0
                y = 1
            elif n == 0:
                x = -1
                y = 0
            else:
                x = 0
                y = -1
            NextPos = vec(self.GridPos.x + x, self.GridPos.y + y)
            if NextPos not in self.app.Walls:
                break
        return vec(x, y)

    def GetPos(self):
        return vec(
            (self.GridPos.x * self.app.CELL_WIDTH)
            + GAP // 2
            + self.app.CELL_WIDTH // 2,
            (self.GridPos.y * self.app.CELL_HEIGHT)
            + GAP // 2
            + self.app.CELL_HEIGHT // 2,
        )

    def EnemyColor(self):
        if self.Number == 0:
            return BLUE
        if self.Number == 1:
            return GREEN
        if self.Number == 2:
            return ORANGE
        if self.Number == 3:
            return RED

    def EnemyKind(self):
        if self.Number == 0:
            return FAST
        elif self.Number == 1:
            return SLOW
        elif self.Number == 2:
            return SCARE
        else:
            return DIZZY


app = App()
app.RunGame()
