import pygame as pg
import editor


SCREEN_SIZE = (640, 480)

pg.init()
screen = pg.display.set_mode(SCREEN_SIZE)

e = editor.Editor()
while True:
    e.event_handle()
    e.update()
    e.draw(screen)