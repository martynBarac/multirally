import pygame as pg

class Editor:
    def __init__(self):
        pg.init()
        self.level = []
        self.box_start = (0, 0)
        self.drawing = False


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

        box = self.get_box(x1, y1, x2, y2)
        self.level.append(box)

    def get_box(self, x1, y1, x2, y2):
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

        return [x, y, w, h]

    def event_handle(self):
        for event in  pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.box_start = pg.mouse.get_pos()
                    self.drawing = True
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.drawing = False
                    box_end = pg.mouse.get_pos()
                    self.add_box(self.box_start[0], self.box_start[1], box_end[0], box_end[1])

    def draw(self, screen):
        screen.fill((0, 0, 0))

        if self.drawing:
            mouse = pg.mouse.get_pos()
            pg.draw.rect(screen, (128, 128, 128), self.get_box(self.box_start[0], self.box_start[1], mouse[0], mouse[1]), 2)

        for box in self.level:
            pg.draw.rect(screen, (255, 255, 255), box)
        pg.display.update()

