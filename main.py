from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame
from random import randrange
from random import choice
from time import time

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

# Dimensions of the rectangle in which the enemies will be drawn
# Enemies height will be calculated from the top of the window
# Enemies will consist of planes and tanks but tanks can't be destroyed
ENEMIES_WIDTH = WINDOW_WIDTH
ENEMIES_HEIGHT = WINDOW_HEIGHT / 2

time_interval = 10  # ms

lives = 2
game_time = 90 * 1000  # 90sec but will converted to ms because of timer function

# Game states
game_states = ['intro', 'playing', 'wining', 'losing']
intro_states = ['menu', 'controls']
current_state = 'intro'
intro_state = 'menu'
pause = False

# List to save the textures
global texture
textures_names = ['0.png', '1.png', '2.png', '3.jpg', '4.jpg', '5.jpg', '6.jpg']

sounds = []
sound_playing = True

time_win_lose = -1  # Variable to make win or lose background appears for a certain time

active_colors = [True, True, True, True]  # Colors for play and controls and quit and back buttons

keyboard_step = 0  # Intially zero but its real value will be took from Enemies class

enemies_pos = [
    [0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0],
    [0, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 2, 0],
    [0, 2, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 2, 0],
    [0, 2, 0, 0, 2, 0, 0, 2, 0, 2, 0, 0, 2, 0, 0, 2, 0],
    [0, 0, 0, 0, 2, 2, 2, 0, 2, 0, 2, 2, 2, 0, 0, 0, 0]
]


# 0 means this position is empty. 1 means this position contains a tank and 2 means this position contains a plane.

class Player:
    def __init__(self, pos_x):
        self.pos_x = pos_x
        self.texture_number = 0
        self.half_width = 0  # Intially zero but its real value will be took from Enemies class
        self.height = 60
        self.initial_pos_x = pos_x

    def set_half_width(self, half_width):
        self.half_width = half_width

    def clear(self):
        self.pos_x = self.initial_pos_x

    def draw(self):
        glBindTexture(GL_TEXTURE_2D, texture[self.texture_number])
        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glColor(1, 1, 1)
        glTexCoord(0, 1)
        glVertex2d(self.pos_x - self.half_width, self.height)
        glTexCoord(1, 1)
        glVertex2d(self.pos_x + self.half_width, self.height)
        glTexCoord(1, 0)
        glVertex2d(self.pos_x + self.half_width, 0)
        glTexCoord(0, 0)
        glVertex2d(self.pos_x - self.half_width, 0)
        glEnd()
        glDisable(GL_TEXTURE_2D)


class Enemy:
    def __init__(self, pos_x, pos_y, size_x, size_y, tank, texture_number):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size_x = size_x
        self.size_y = size_y
        self.tank = tank
        self.texture_number = texture_number

    def draw(self):
        glBindTexture(GL_TEXTURE_2D, texture[self.texture_number])
        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glColor(1, 1, 1)
        glTexCoord(0, 1)
        glVertex2d(self.pos_x, self.pos_y)
        glTexCoord(1, 1)
        glVertex2d(self.pos_x + self.size_x, self.pos_y)
        glTexCoord(1, 0)
        glVertex2d(self.pos_x + self.size_x, self.pos_y - self.size_y)
        glTexCoord(0, 0)
        glVertex2d(self.pos_x, self.pos_y - self.size_y)
        glEnd()
        glDisable(GL_TEXTURE_2D)


class Enemies:
    def __init__(self):
        self.enemies = []

    def init(self, pos_list, enemy_width, enemy_height, window_height):
        self.enemies.clear()
        unit_width = enemy_width / len(pos_list[0])
        unit_height = enemy_height / len(pos_list)
        for i in range(len(pos_list)):
            for j in range(len(pos_list[0])):
                if pos_list[i][j] > 0:
                    self.enemies.append(Enemy(unit_width * j, window_height - unit_height * i, unit_width, unit_height,
                                              True if pos_list[i][j] == 1 else False,
                                              pos_list[i][j]))
        return unit_width

    def draw(self):
        for enemy in self.enemies:
            enemy.draw()

    def IsCompleted(self):
        for enemy in self.enemies:
            if not enemy.tank:
                return False
        return True


class Bullet:
    def __init__(self, pos_x, pos_y, player_bullet):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.player_bullet = player_bullet
        self.height = 10
        self.delta_y = 4
        self.move = True

    def draw(self):
        glLineWidth(3)
        glBegin(GL_LINES)
        glColor(1, 0, 0)
        glVertex(self.pos_x, self.pos_y, -0.1)
        if self.player_bullet:
            glVertex(self.pos_x, self.pos_y + self.height, -0.1)
            if self.move:
                self.pos_y += self.delta_y
        else:
            glVertex(self.pos_x, self.pos_y - self.height, -0.1)
            if self.move:
                self.pos_y -= self.delta_y
        glEnd()


class Bullets:
    def __init__(self):
        self.player_bullets = []
        self.enemies_bullets = []

    def clear(self):
        self.player_bullets.clear()
        self.enemies_bullets.clear()

    def add(self, pos_x, pos_y, player_bullet):
        if player_bullet:
            self.player_bullets.append(Bullet(pos_x, pos_y, True))
        else:
            self.enemies_bullets.append(Bullet(pos_x, pos_y, False))

    def draw(self, window_height, player_bullet, move):
        if player_bullet:
            temp = self.player_bullets
            for bullet in temp:
                if bullet.pos_y + bullet.height >= window_height:
                    self.player_bullets.remove(bullet)
                else:
                    if move:
                        bullet.move = True
                    else:
                        bullet.move = False
                    bullet.draw()
        else:
            temp = self.enemies_bullets
            for bullet in temp:
                if bullet.pos_y <= 0:
                    self.enemies_bullets.remove(bullet)
                else:
                    if move:
                        bullet.move = True
                    else:
                        bullet.move = False
                    bullet.draw()


# There are 4 backgrounds 2 of them move which are textures 3,4. Textures 5,6 are fixed
class Background:
    def __init__(self):
        self.delta_x = 0
        self.speed = 0.0003

    def clear(self):
        self.delta_x = 0

    def draw(self, texture_number):
        if texture_number == 5 or texture_number == 6:
            self.clear()
        glBindTexture(GL_TEXTURE_2D, texture[texture_number])
        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glColor(1, 1, 1)
        glTexCoord(self.delta_x, 0)
        glVertex(0, 0, -0.3)

        glTexCoord(1 + self.delta_x, 0)
        glVertex(WINDOW_WIDTH, 0, -0.3)

        glTexCoord(1 + self.delta_x, 1)
        glVertex(WINDOW_WIDTH, WINDOW_HEIGHT, -0.3)

        glTexCoord(self.delta_x, 1)
        glVertex(0, WINDOW_HEIGHT, -0.3)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        if texture_number == 3 or texture_number == 4:
            self.delta_x -= self.speed


enemies_obj = Enemies()
player_obj = Player(WINDOW_WIDTH / 2)
bullets_obj = Bullets()
bg_obj = Background()


def positions_generator(pos_list):
    for i in range(len(pos_list)):
        for j in range(len(pos_list[0])):
            rand_number = randrange(3)  # range is (0,1,2)
            plane_behind_tank = False
            if rand_number == 1:  # as we can't destroy the tank so we shouldn't have a plane behind it.
                for k in range(i - 1, -1, -1):
                    if pos_list[k][j] == 2:
                        plane_behind_tank = True
                        break
            if plane_behind_tank:
                pos_list[i][j] = choice([0, 2])
            else:
                pos_list[i][j] = rand_number


def secondary_bullets_generator(bullets, enemies):
    for enemy in enemies.enemies:
        if randrange(0, 250) == 7:
            bullets.add(enemy.pos_x + enemy.size_x / 2, enemy.pos_y - enemy.size_y, False)


def collision(bullets, enemies, player):
    global lives
    # collision between player bullets and the enemies
    temp_player_bullets = bullets.player_bullets
    temp_enemies_bullets = bullets.enemies_bullets
    temp_enemies = enemies.enemies
    for bullet in temp_player_bullets:
        for enemy in temp_enemies:

            if enemy.pos_x <= bullet.pos_x <= enemy.pos_x + enemy.size_x and \
                    bullet.pos_y + bullet.height >= enemy.pos_y - enemy.size_y:
                if not enemy.tank:
                    enemies.enemies.remove(enemy)
                # removing the bullet either the enemy is solid or not
                bullets.player_bullets.remove(bullet)
                break
    # collision between enemies bullets and the player
    for bullet in temp_enemies_bullets:
        if player.pos_x - player.half_width <= bullet.pos_x <= player.pos_x + player.half_width and \
                bullet.pos_y - bullet.height <= player.height:
            lives -= 1
            bullets.enemies_bullets.remove(bullet)

    # collision between enemies bullets and player bullets
    epsilon = 1
    for e_bullet in temp_enemies_bullets:
        for p_bullet in temp_player_bullets:
            if e_bullet.pos_x - epsilon <= p_bullet.pos_x <= e_bullet.pos_x + epsilon and \
                    p_bullet.pos_y + p_bullet.height >= e_bullet.pos_y - e_bullet.height:
                bullets.enemies_bullets.remove(e_bullet)
                bullets.player_bullets.remove(p_bullet)
                break


def init():
    global texture, textures_names, keyboard_step, enemies_pos, ENEMIES_WIDTH, ENEMIES_HEIGHT
    glClearColor(1.0, 1.0, 1.0, 0.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, 0, 1)
    glMatrixMode(GL_MODELVIEW)

    texture = glGenTextures(len(textures_names))
    for i in range(len(textures_names)):
        imgload = pygame.image.load(textures_names[i])
        img = pygame.image.tostring(imgload, "RGBA", True)
        width = imgload.get_width()
        height = imgload.get_height()
        glBindTexture(GL_TEXTURE_2D, texture[i])
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        gluBuild2DMipmaps(GL_TEXTURE_2D, 4, width, height, GL_RGBA, GL_UNSIGNED_BYTE, img)

    pygame.mixer.init()
    pygame.mixer.music.load('cinematic-chillhop-main-6676.mp3')
    pygame.mixer.music.play()
    sounds.append(pygame.mixer.Sound('Grenade-SoundBible.com-1777900486.wav'))
    sounds.append(pygame.mixer.Sound('mixkit-arcade-game-complete-or-approved-mission-205.wav'))
    sounds.append(pygame.mixer.Sound('mixkit-arcade-fast-game-over-233.wav'))
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    keyboard_step = enemies_obj.init(enemies_pos, ENEMIES_WIDTH, ENEMIES_HEIGHT, WINDOW_HEIGHT)
    player_obj.set_half_width(keyboard_step / 2)


def drawText(string, x, y, scale):
    glLineWidth(2)
    glColor(1, 1, 1)
    glPushMatrix()
    glRasterPos(x, y, 0)
    glScale(scale, scale, 1)
    for c in string:  # render character by character starting from the origin
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(c))
    glPopMatrix()


def buttonandtext(str, multi_string, pos_x, pos_y, width, height, color):
    glBegin(GL_QUADS)
    glColor(color[0], color[1], color[2])
    glVertex(pos_x, pos_y, -0.1)
    glVertex(pos_x + width, pos_y, -0.1)
    glVertex(pos_x + width, pos_y + height, -0.1)
    glVertex(pos_x, pos_y + height, -0.1)
    glEnd()
    str_height = glutBitmapHeight(GLUT_BITMAP_TIMES_ROMAN_24)
    if multi_string:
        unit_height_window = height / len(str)
        pos_y += height
        for st in str:
            pos_y -= unit_height_window
            str_width = 0
            for ch in st:
                str_width += glutBitmapWidth(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
            drawText(st, pos_x + ((width - str_width) / 2), pos_y + (unit_height_window - str_height) / 2, 1)
    else:
        str_width = 0
        for ch in str:
            str_width += glutBitmapWidth(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
        drawText(str, pos_x + ((width - str_width) / 2), pos_y + (height - str_height) / 2 + 5, 1)


def drawTime(timee):
    timee //= 1000
    drawText(str(timee // 60) + ':' + str(timee % 60), 65, WINDOW_HEIGHT - 20, 0.1)


def PassiveMouseMotion(x, y):
    global intro_state, active_colors, WINDOW_HEIGHT
    if intro_state == 'menu':
        if 400 <= x <= 600 and 400 <= WINDOW_HEIGHT - y <= 475:
            active_colors[0] = False
        else:
            active_colors[0] = True
        if 400 <= x <= 600 and 275 <= WINDOW_HEIGHT - y <= 350:
            active_colors[1] = False
        else:
            active_colors[1] = True
        if 400 <= x <= 600 and 150 <= WINDOW_HEIGHT - y <= 225:
            active_colors[2] = False
        else:
            active_colors[2] = True
    elif intro_state == 'controls':
        if 200 <= x <= 300 and 50 <= WINDOW_HEIGHT - y <= 100:
            active_colors[3] = False
        else:
            active_colors[3] = True


def ActiveMouseMotion(button, state, x, y):
    global intro_state, current_state, WINDOW_HEIGHT
    if intro_state == 'menu':
        if 400 <= x <= 600 and 400 <= WINDOW_HEIGHT - y <= 475:
            if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
                current_state = 'playing'
        if 400 <= x <= 600 and 275 <= WINDOW_HEIGHT - y <= 350:
            if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
                intro_state = 'controls'
        if 400 <= x <= 600 and 150 <= WINDOW_HEIGHT - y <= 225:
            if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
                Quit()
    elif intro_state == 'controls':
        if 200 <= x <= 300 and 50 <= WINDOW_HEIGHT - y <= 100:
            if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
                intro_state = 'menu'


def KeyboardMotion(key, x, y):
    global keyboard_step, current_state, pause, WINDOW_WIDTH
    if current_state == 'playing' and not pause:
        if key == GLUT_KEY_LEFT:
            if player_obj.pos_x - player_obj.half_width - keyboard_step >= 0:
                player_obj.pos_x -= keyboard_step
        elif key == GLUT_KEY_RIGHT:
            if player_obj.pos_x + player_obj.half_width + keyboard_step <= WINDOW_WIDTH + .1:
                # just added .1 because of float point comparing
                player_obj.pos_x += keyboard_step


def keyboard(key, x, y):
    global sound_playing, current_state, intro_state, pause
    if key == b'q':
        Quit()
    if key == b' ':
        if current_state == 'playing' and not pause:
            bullets_obj.add(player_obj.pos_x, player_obj.height, True)
            if sound_playing:
                sounds[0].play()
    if key == b's':
        sound_playing = not sound_playing
        if sound_playing:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
            sounds[0].stop()
    if key == b'p':
        if current_state == 'playing':
            pause = not pause
    if ord(key) == 27:  # 27 is the ascii code of escape button
        if current_state == 'playing':
            current_state = 'intro'
            bullets_obj.clear()
            enemies_obj.init(enemies_pos, ENEMIES_WIDTH, ENEMIES_HEIGHT, WINDOW_HEIGHT)
            player_obj.clear()
        elif current_state == 'intro':
            if intro_state == 'controls':
                intro_state = 'menu'
            else:
                Quit()


def Timer(v):
    Display()
    glutTimerFunc(time_interval, Timer, 1)


def Display():
    global WINDOW_HEIGHT, ENEMIES_WIDTH, ENEMIES_HEIGHT, current_state, intro_state, lives, game_time, pause, \
        time_interval, time_win_lose, active_colors, enemies_pos

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    if current_state == 'intro':
        bg_obj.draw(3)
        if intro_state == 'menu':
            buttonandtext('Play', False, 400, 400, 200, 75,
                          [0.403, 0.384, 0.407] if active_colors[0] else [0.266, 0.250, 0.270])
            buttonandtext('Controls', False, 400, 275, 200, 75,
                          [0.403, 0.384, 0.407] if active_colors[1] else [0.266, 0.250, 0.270])
            buttonandtext('Quit', False, 400, 150, 200, 75,
                          [0.403, 0.384, 0.407] if active_colors[2] else [0.266, 0.250, 0.270])
        if intro_state == 'controls':
            buttonandtext(['Move: left and right arrow',
                           'Fire: space bar',
                           'Toggling music: s',
                           'Pause: p',
                           'Back: escape',
                           'Quit: q'], True, 350, 125, 300, 350, [0.403, 0.384, 0.407])
            buttonandtext('Back', False, 200, 50, 100, 50,
                          [0.403, 0.384, 0.407] if active_colors[3] else [0.266, 0.250, 0.270])

    elif current_state == 'playing':
        drawText("Time:", 2, WINDOW_HEIGHT - 20, 0.1)
        drawText("Lives:", 2, WINDOW_HEIGHT - 40, 0.1)
        drawText(str(lives), 65, WINDOW_HEIGHT - 40, 0.1)
        if not pause:
            game_time -= time_interval
        drawTime(game_time)
        bg_obj.draw(4)
        enemies_obj.draw()
        player_obj.draw()
        if not pause:
            secondary_bullets_generator(bullets_obj, enemies_obj)
        bullets_obj.draw(WINDOW_HEIGHT, True, not pause)
        bullets_obj.draw(WINDOW_HEIGHT, False, not pause)
        collision(bullets_obj, enemies_obj, player_obj)
        if lives <= 0 or game_time <= 0 or enemies_obj.IsCompleted():
            current_state = 'wining' if enemies_obj.IsCompleted() else 'losing'
            bullets_obj.clear()
            positions_generator(enemies_pos)
            enemies_obj.init(enemies_pos, ENEMIES_WIDTH, ENEMIES_HEIGHT, WINDOW_HEIGHT)
            player_obj.clear()
            game_time = 90 * 1000
            lives = 2
    else:
        if time_win_lose == -1:
            if sound_playing:
                pygame.mixer.music.pause()
                sounds[1 if current_state == 'wining' else 2].play()
            time_win_lose = time()
        if time() <= time_win_lose + 3:
            bg_obj.draw(5 if current_state == 'wining' else 6)
        else:
            current_state = 'playing'
            time_win_lose = -1
            if sound_playing:
                pygame.mixer.music.play()

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Star Wars")
    init()
    glutDisplayFunc(Display)
    glutTimerFunc(time_interval, Timer, 1)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(KeyboardMotion)
    glutMouseFunc(ActiveMouseMotion)
    glutPassiveMotionFunc(PassiveMouseMotion)
    glutMainLoop()


main()
