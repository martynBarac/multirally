import pygame as pg

class Editor:
    def __init__(self):
        pg.init()
        self.level = []
        self.box_start = (0, 0)
        self.mouse_down = False


    def load_level(self):
        pass

    def save_level(self):
        pass

    def run(self):
        self.event_handle()
        self.update()
        self.draw()

    def update(self):
        pass

    def add_box(self, x1, y1, x2, y2):
        w = h = x = y = 0
        if x1 < x2:
            w = x2 - x1
            x = x1
        else:
            w = x1 - x2
            x = x2

        if y1 < y2:
            h = y2 - y1
            y = y1
        else:
            h = y1 - y2
            y = y2

        self.level.append([x, y, w, h])

    def event_handle(self):
        for event in  pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.box_start = pg.mouse.get_pos()
                    self.mouse_down = True
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_down = False
                    box_end = pg.mouse.get_pos()
                    self.add_box(self.box_start[0], self.box_start[1], box_end[0], box_end[1])

    def draw(self, screen):
        pg.draw.rect(screen, (255, 255, 255), [0, 0, 10, 10])
        for box in self.level:
            pg.draw.rect(screen, (255, 255, 255), box)
        pg.display.update()

