import pygame

from sys import exit
from random import choice
from sqlite3 import connect
from os.path import join, isfile


SIZE = HEIGHT, WIDTH = (900, 1000)
DATA_BASE = 'static.sqlite'
FPS = 60
clock = pygame.time.Clock()
screen = pygame.display.set_mode(SIZE)
pygame.init()


def load_image(filename: str, colorkey: int | None = None) -> pygame.surface.Surface:

    '''Функция для загрузки спрайтов'''

    fullname = join('data', filename)

    if not isfile(fullname):

        print(f'Нет доступа к файлу по пути: {fullname}')
        exit()

    image = pygame.image.load(fullname)

    if colorkey is not None:

        image = image.convert()

        if colorkey == -1:

            colorkey = image.get_at((0, 0))

        image.set_colorkey(colorkey)

    else:

        image = image.convert_alpha()

    return image


def terminate() -> None:

    '''Функция для выхода из игры'''

    pygame.quit()
    exit()


class StartWindow:

    '''Класс для заставки'''

    IMAGE_START_WINDOW = load_image('fon.png')
    INTRO_TEXT = ['                                           Добро пожаловать !',
                  'Правила игры очень просты:',
                  '     1. Твоя цель как можно больше набрать очков',
                  '     2. Для этого тебе нужно шариком попадать в разрушаемые стенки',
                  '         P.S. в игре также есть неразрушаемые стенки',
                  '',
                  '                     Нажмите на любую кнопку - чтобы начать игру']

    def __init__(self):

        self.image = self.IMAGE_START_WINDOW
        self.intro_text = self.INTRO_TEXT
        self.color_font = pygame.Color('white')

    def start_window(self) -> bool:

        fon = pygame.transform.scale(self.image, SIZE)
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord_y = 300

        for line in self.intro_text:

            string_rendered = font.render(line, 1, self.color_font)
            intro_rect = string_rendered.get_rect()
            text_coord_y += 30
            intro_rect.top = text_coord_y
            intro_rect.x = 75
            text_coord_y += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        running = True

        while running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    terminate()
                    running = False
                    return False

                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:

                    running = False
                    return True

            pygame.display.flip()
            clock.tick(FPS)


class Border(pygame.sprite.Sprite):

    '''Класс для описания стенок поля'''

    def __init__(self, x1: int, y1: int, x2: int, y2: int, *groups) -> None:

        super().__init__(groups)
        self.color = pygame.color.Color('white')

        if x1 == x2:

            self.add(GamePole.vertical_borders_col)
            self.image = pygame.Surface((1, y2 - y1))
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)

        else:

            self.add(GamePole.horizontal_borders_col)
            self.image = pygame.Surface((x2 - x1, 1))
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)

        self.image.fill(self.color)


class Frame(pygame.sprite.Sprite):

    '''Класс для описания рамки поля'''

    def __init__(self, coords: tuple[int, int], height: int, width: int,  *groups):

        super().__init__(groups)
        self.coords = coords
        self.height = height
        self.width = width

        self.color = pygame.color.Color('white')
        self.borders = [Border(self.coords[0], self.coords[1],
                               self.coords[0] + self.height, self.coords[1]),
                        Border(self.coords[0], self.coords[1] + self.width,
                               self.coords[0] + self.height, self.coords[1] + self.width),
                        Border(self.coords[0], self.coords[1],
                               self.coords[0], self.coords[1] + self.width),
                        Border(self.coords[0] + self.height,
                               self.coords[1], self.coords[0] + self.height, self.coords[1] + self.width)]

    def update_borders(self) -> None:

        for border in self.borders:

            screen.blit(border.image, border.rect)


class Player(pygame.sprite.Sprite):

    '''Класс для описание модельки игрока'''

    HEIGHT = 100
    WIDTH = 20
    SPEED = 10

    def __init__(self, coords: tuple[int, int], *groups) -> None:

        super().__init__(groups)

        coords = coords
        height = self.HEIGHT
        width = self.WIDTH

        self.speed = self.SPEED
        self.color = pygame.color.Color('white')

        self.image = pygame.Surface((height, width))
        self.image.fill(self.color)
        self.rect = pygame.Rect(*coords, height, width)
        self.add(GamePole.player_col)

    def set_coords(self, coords: tuple[int, int]) -> None:

        height = self.HEIGHT

        if pygame.sprite.spritecollideany(self, game_pole.vertical_borders_col):

            if self.rect.x > coords[0] + height:

                self.rect = self.rect.move(-15, 0)

            else:

                self.rect = self.rect.move(15, 0)

            return None

        self.rect = self.rect.move(coords)

    def get_coords(self) -> tuple[int, int]:

        return (self.rect.x, self.rect.y)

    def get_speed(self) -> int:

        return self.speed

    def update_player(self) -> None:

        screen.blit(self.image, self.get_coords())


class Wall(pygame.sprite.Sprite):

    '''Общий класс для описание объектов находящихся на игровом поле'''

    HEIGHT = 40
    WIDTH = 20

    def __init__(self, coords: tuple[int, int], color: str | tuple[int, int, int], *groups) -> None:

        super().__init__(groups)

        height = self.HEIGHT
        width = self.WIDTH

        self.coords = coords
        self.color = color
        self.is_life = True

        self.image = pygame.Surface((height, width))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.coords

    def get_coords(self) -> tuple[int, int]:

        return (self.rect.x, self.rect.y)

    def update_wall(self) -> None:

        screen.blit(self.image, self.get_coords())


class InvulWall(Wall):

    '''Класс для описание неразрушаймых стен'''

    def __init__(self, coords: tuple[int, int], color: str | tuple[int, int, int], *groups) -> None:

        super().__init__(coords, color, groups)
        self.add(GamePole.invulwall_col)


class ScoreWall(Wall):

    '''Класс для описание стен, которые будут давать очки'''

    def __init__(self, coords: tuple[int, int], score: int, color: str | tuple[int, int, int], *groups) -> None:

        super().__init__(coords, color, groups)
        self.score = score
        self.add(GamePole.wall_col)

    def destroyed(self) -> None:

        game_pole.score.add_score(self.score)
        self.remove(GamePole.wall_col)


class Ball(pygame.sprite.Sprite):

    '''Класс для описание мяча'''

    SPEED = 5
    RADIUS = 8

    def __init__(self, start_coords: tuple[int, int], *groups) -> None:

        super().__init__(groups)

        self.speed = self.SPEED
        self.speed_x = True
        self.speed_y = True
        radius = self.RADIUS

        self.image = pygame.Surface((radius, radius))
        self.color = pygame.color.Color('white')
        pygame.draw.circle(self.image, self.color, (radius // 2, radius // 2), radius // 2)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = start_coords

        self.add(GamePole.ball_col)

    def get_coords(self) -> tuple[int, int]:

        return (self.rect.x, self.rect.y)

    def set_coords(self, coords: tuple[int, int]) -> None:

        self.rect.x, self.rect.y = coords

    def set_speed_x(self) -> None:

        self.speed_x = not self.speed_x

    def set_speed_y(self) -> None:

        self.speed_y = not self.speed_y

    def update_ball(self) -> None:

        screen.blit(self.image, (self.rect.x, self.rect.y))

        if pygame.sprite.spritecollideany(self, GamePole.horizontal_borders_col):

            self.set_speed_y()

        elif pygame.sprite.spritecollideany(self, GamePole.vertical_borders_col):

            self.set_speed_x()

        elif pygame.sprite.spritecollideany(self, GamePole.player_col):

            if GamePole.START_POS_PLAYER[1] < self.get_coords()[1] < GamePole.START_POS_PLAYER[1] + Player.WIDTH:

                self.set_speed_x()

            else:

                self.set_speed_y()

        elif wall := pygame.sprite.spritecollideany(self, GamePole.invulwall_col):

            if wall.get_coords()[1] < self.get_coords()[1] < wall.get_coords()[1] + InvulWall.WIDTH:

                self.set_speed_x()

            else:

                self.set_speed_y()

        elif wall := pygame.sprite.spritecollideany(self, GamePole.wall_col):

            if wall.get_coords()[1] < self.get_coords()[1] < wall.get_coords()[1] + ScoreWall.WIDTH:

                self.set_speed_x()

            else:

                self.set_speed_y()

            wall.destroyed()
            game_pole.remove_wall(wall)


class Score:

    '''Класс для опсания игрового счёта'''

    START_COORDS_SCORE = (20, 20)

    def __init__(self) -> None:

        self.score = 0
        self.font = pygame.font.Font(None, 30)
        self.color_font = pygame.color.Color('white')
        self.text = 'SCORE: '

    def update_score(self) -> None:

        x, y = self.START_COORDS_SCORE

        string_rendered = self.font.render(self.text + str(self.score), 1, self.color_font)
        intro_rect = string_rendered.get_rect()
        intro_rect.x = x
        intro_rect.top = y
        screen.blit(string_rendered, intro_rect)

    def add_score(self, score: int) -> None:

        self.score += score
        self.update_score()


class GamePole(pygame.sprite.Sprite):

    '''Класс для описание игрового поля и процессов в нём'''

    IMAGE_FON = load_image('fon.png')

    horizontal_borders_col = pygame.sprite.Group()
    vertical_borders_col = pygame.sprite.Group()
    ball_col = pygame.sprite.Group()
    player_col = pygame.sprite.Group()
    invulwall_col = pygame.sprite.Group()
    wall_col = pygame.sprite.Group()

    LEVELS = ('yandex.txt', 'love.txt')
    INTRO_TEXT = ['LEVEL ']

    START_POS_BALL = (450, 750)
    START_POS_PLAYER = (400, 800)

    def __init__(self, frame: Frame, score: Score, player: Player, ball: Ball, *groups) -> None:

        self.image_fon = self.IMAGE_FON

        self.frame = frame
        self.score = score
        self.player = player
        self.ball = ball

        self.count_level = 1
        self.color_font = pygame.color.Color('white')
        self.walls = []

        super().__init__(groups)

    def update_frame(self) -> None:

        '''Обновляет весь фон игрового поля'''

        fon = pygame.transform.scale(self.image_fon, SIZE)
        intro_text = self.INTRO_TEXT[0] + str(self.count_level)
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)

        string_rendered = font.render(intro_text, 1, self.color_font)
        intro_rect = string_rendered.get_rect()
        intro_rect.top = 25
        intro_rect.x = 400
        screen.blit(string_rendered, intro_rect)
        self.frame.update_borders()

    def update_walls(self) -> None:

        for wall in self.walls:

            wall.update_wall()

    def remove_wall(self, wall: Wall | InvulWall) -> None:

        if wall in self.walls:

            self.walls.remove(wall)

    def add_wall(self, wall: Wall | InvulWall) -> None:

        if wall not in self.walls:

            self.walls.append(wall)

    def update_all(self) -> None:

        screen.fill((0, 0, 0))
        screen.blit(self.image_fon, (0, 0))

        self.update_frame()
        self.score.update_score()
        self.player.update_player()
        self.move_ball()
        self.ball.update_ball()
        self.update_walls()

        pygame.display.flip()
        clock.tick(FPS)

    def move_ball(self) -> None:

        '''Передвижение мяча'''

        x, y = 0, 0

        if self.ball.speed_x:

            x += self.ball.speed

        else:

            x -= self.ball.speed

        if self.ball.speed_y:

            y += self.ball.speed

        else:

            y -= self.ball.speed

        self.ball.rect = self.ball.rect.move(x, y)

    def create_level(self) -> None:

        level = Level(choice(self.LEVELS))
        self.walls = level.parse_level()
        self.ball.set_coords(self.START_POS_BALL)

    def check_win(self) -> bool:

        '''Проверяет за разрушение всего разрушаемого'''

        return True if len([wall for wall in self.walls if type(wall) is not InvulWall]) == 0 else False

    def check_lose(self) -> bool:

        '''Проверяет на выход мяча за нижную барьер'''

        if pygame.sprite.spritecollideany(self.ball, GamePole.horizontal_borders_col)\
           and self.ball.get_coords()[1] > self.START_POS_BALL[1]:

            return True

        return False


class Level:

    '''Класс для описания парсера уровня'''

    COLORS = ('R', 'B', 'G', 'Y')
    SCORES = (50, 100, 200)

    def __init__(self, filename: str) -> None:

        fullname = join('levels', filename)

        if not isfile(fullname):

            print(f'Нету уровня по пути: {fullname}')
            exit()

        self.structure = []

        with open(fullname) as file:

            for line in file.readlines():

                list_simbol = []

                for simbol in line:

                    list_simbol.append(simbol)

                self.structure.append(list_simbol)

    def parse_level(self) -> list[list[ScoreWall | InvulWall]]:

        '''Парсит структуру уровня'''

        coord_y = 100
        self.walls = []

        for line in self.structure:

            coord_x = 100

            for simbol in line:

                if simbol in self.COLORS:

                    color = self.get_color(simbol)
                    wall = ScoreWall((coord_x, coord_y),
                                     choice(self.SCORES),
                                     color)

                elif simbol == '#':

                    wall = InvulWall((coord_x, coord_y), 'grey')

                elif simbol == ' ' or simbol == '\n':

                    coord_x += 50
                    continue

                else:

                    print('Не правильно написан уровень')
                    exit()

                self.walls.append(wall)
                coord_x += 50

            coord_y += 40

        return self.walls

    @staticmethod
    def get_color(string: str) -> str:

        if string == 'R':

            return 'red'

        elif string == 'B':

            return 'blue'

        elif string == 'G':

            return 'green'

        elif string == 'Y':

            return 'yellow'


class EndWindow:

    '''Класс для экрана окончания игры'''

    IMAGE_START_WINDOW = load_image('fon.png')
    INTRO_TEXT = ['                 К сожалению вы проиграли, вас счёт составляет: ',
                  '         Данные вашего прохождения будут занесены в базу данных',
                  '',
                  '                         Чтобы выйти - нажмите на любую кнопку']

    def __init__(self, score: Score) -> None:

        self.image = self.IMAGE_START_WINDOW
        self.intro_text = self.INTRO_TEXT
        self.score = score.score
        self.intro_text[0] += str(self.score)
        self.color_font = pygame.Color('white')

    def end_window(self) -> bool:

        '''Установка экрана окончания'''

        self.write_score_in_sqltable()

        fon = pygame.transform.scale(self.image, SIZE)
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord_y = 300

        for line in self.intro_text:

            string_rendered = font.render(line, 1, self.color_font)
            intro_rect = string_rendered.get_rect()
            text_coord_y += 30
            intro_rect.top = text_coord_y
            intro_rect.x = 75
            text_coord_y += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        running = True

        while running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    terminate()
                    running = False
                    return False

                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:

                    running = False
                    return True

            pygame.display.flip()

    def write_score_in_sqltable(self) -> None:

        '''Добавление рекорда в БД'''

        with connect(DATA_BASE) as con:

            cursor = con.cursor()
            cursor.execute(f'''INSERT INTO Static (Score) VALUES ({self.score})''')


def check_status_game() -> None:

    '''Функция для проверки состояния игры'''

    global running

    if game_pole.check_win():

        game_pole.count_level += 1
        game_pole.create_level()

    elif game_pole.check_lose():

        end_window = EndWindow(score)

        if end_window.end_window():

            running = False
            terminate()


if __name__ == '__main__':

    start_window = StartWindow()

    if start_window.start_window():

        running = True

        frame = Frame((50, 50), 800, 900)
        player = Player(GamePole.START_POS_PLAYER)
        ball = Ball(GamePole.START_POS_BALL)
        score = Score()
        game_pole = GamePole(frame, score, player, ball)

        x_coord_wall = 100
        y_coord_wall = 100

        game_pole.create_level()
        game_pole.update_all()

        while running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    running = False

                elif event.type == pygame.KEYDOWN:

                    while pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_LEFT]:

                        if pygame.key.get_pressed()[pygame.K_RIGHT] and pygame.key.get_pressed()[pygame.K_LEFT]:

                            pygame.event.pump()
                            break

                        x, y = 0, 0
                        speed = game_pole.player.get_speed()

                        if event.key == pygame.K_RIGHT:

                            x += speed

                        else:

                            x -= speed

                        player.set_coords((x, y))
                        game_pole.update_all()
                        pygame.event.pump()

                        check_status_game()

            check_status_game()
            game_pole.update_all()

        terminate()
