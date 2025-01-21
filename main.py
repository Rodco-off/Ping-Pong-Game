import pygame

from sys import exit
from os.path import join, isfile


SIZE = HEIGHT, WIDTH = (900, 1024)
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
                  '                     Нажмите на любую кнопку, чтобы начать игру']

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


class GamePole:

    '''Класс для описание игрового поля'''

    IMAGE_FON = load_image('fon.png')

    def __init__(self, coords: tuple[int, int], height: int, width: int) -> None:

        self.coords = coords
        self.height_frame = height
        self.width_frame = width
        self.image_fon = self.IMAGE_FON
        self.color_frame = pygame.color.Color('white')

    def update_frame(self) -> None:

        screen.blit(self.image_fon, (0, 0))
        pygame.draw.rect(screen, self.color_frame,
                         pygame.Rect(*self.coords, self.height_frame, self.width_frame), 1)

    def update_player(self) -> None:

        pygame.draw.rect()


class Player:

    '''Класс для описание модельки игрока'''

    def __init__(self, start_coords: tuple[int, int], speed: int) -> None:

        self.coords = start_coords
        self.speed = speed

    def set_coords(self, coords: tuple[int, int]) -> None:

        self.coords = coords

    def get_coords(self) -> tuple[int, int]:

        return self.coords


class Wall:

    '''Общий класс для описание объектов находящихся на игровом поле'''

    def __init__(self, coords: tuple[int, int]) -> None:

        self.coords = coords
        self.is_life = True


class InvulWall(Wall):

    '''Класс для описание неразрушаймых стен'''

    def __init__(self, coords: tuple[int, int]) -> None:

        super().__init__(coords)


class ScoreWall(Wall):

    '''Класс для описание стен, которые будут давать очки'''

    def __init__(self, coords: tuple[int, int], score: int) -> None:

        super().__init__(coords)
        self.score = score


class Ball:

    '''Класс для описание мяча'''

    def __init__(self, start_coords: tuple[int, int], speed: int) -> None:

        self.start_coords = start_coords
        self.speed = speed


class Score:

    '''Класс для опсания игрового счёта'''

    def __init__(self):

        self.score = 0


if __name__ == '__main__':

    start_window = StartWindow()

    if start_window.start_window():

        running = True

        while running:

            screen.fill((0, 0, 0))
            game_pole = GamePole((50, 50), 800, 924)
            game_pole.update_frame()
            pygame.display.flip()
