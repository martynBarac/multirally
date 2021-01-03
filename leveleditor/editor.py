import pygame as pg

SCREEN_SIZE = (640, 480)

pg.init()
screen = pg.display.set_mode(SCREEN_SIZE)

class Editor:
    def __init__(self):
        pg.init()
        self.level = []
        self.box_start = (0, 0)
        self.drawing = False
        self.selection = -1
        self.running = True

        self.dragging = False
        self.drag_mouse_start = (0, 0) # Mouse pos when start dragging
        self.drag_box_start = (0, 0) # Box pos when start dragging

        self.gridsize = 32


    def load_level(self):
        pass

    def save_level(self):
        pass

    def run(self):
        while self.running:
            self.event_handle()
            self.update()
            self.draw()

    def update(self):
        if self.dragging:
            mouse = self.pos_to_grid(pg.mouse.get_pos())
            self.level[self.selection][0] = self.drag_box_start[0] - (self.drag_mouse_start[0] - mouse[0])
            self.level[self.selection][1] = self.drag_box_start[1] - (self.drag_mouse_start[1] - mouse[1])


    def select(self, x, y):
        new_selection = -1
        selected = False
        for i in range(len(self.level)):
            if self.box_col(self.level[i], x, y):
                selected = True
                new_selection = i

        self.selection = new_selection
        return selected

    def box_col(self, rect, x, y):
        if x < rect[0]+rect[2] and x > rect[0] and y > rect[1] and y < rect[1]+rect[3]:
            return True
        return False

    def add_box(self, xy1, xy2):

        box = self.get_box(xy1[0], xy1[1], xy2[0], xy2[1])
        # Only add if it has a width and height
        if box[2] > 0 and box[3] > 0:
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

    def pos_to_grid(self, pos):
        x = pos[0]
        y = pos[1]
        xoff = x % self.gridsize
        yoff = y % self.gridsize

        newx = newy = 0

        if xoff > self.gridsize/2:
            newx = x + (self.gridsize - xoff)
        else:
            newx = x - xoff

        if yoff > self.gridsize/2:
            newy = y + (self.gridsize - yoff)
        else:
            newy = y - yoff

        return [newx, newy]

    def event_handle(self):
        for event in  pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.box_start = self.pos_to_grid(pg.mouse.get_pos())
                    self.drawing = True
                elif event.button == 3:
                    mouse = pg.mouse.get_pos()
                    if self.select(mouse[0], mouse[1]):
                        self.dragging = True
                        self.drag_mouse_start = self.pos_to_grid(mouse)
                        self.drag_box_start = self.level[self.selection][:2]

            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.drawing = False
                    box_end = self.pos_to_grid(pg.mouse.get_pos())
                    self.add_box(self.box_start, box_end)
                elif event.button == 3:
                    self.dragging = False

    def draw(self):
        screen.fill((0, 0, 0))
        # Draw box outline when drawing a box
        if self.drawing:
            mouse = self.pos_to_grid(pg.mouse.get_pos())
            pg.draw.rect(screen, (128, 128, 128), self.get_box(self.box_start[0], self.box_start[1], mouse[0], mouse[1]), 2)
        # Draw level
        for box in self.level:
            pg.draw.rect(screen, (255, 255, 255), box)
        # Draw grid
        for x in range(0, SCREEN_SIZE[0], self.gridsize):
            pg.draw.line(screen, (20, 20, 20), [x, 0], [x, SCREEN_SIZE[1]], 1)
            for y in range(0, SCREEN_SIZE[1], self.gridsize):
                pg.draw.line(screen, (20, 20, 20), [0, y], [SCREEN_SIZE[0], y], 1)

        # Draw selection box
        if self.selection != -1:
            pg.draw.rect(screen, (0, 255, 0), self.level[self.selection], 2)

        pg.display.update()

if __name__ == "__main__":
    e = Editor()
    e.run()
    pg.quit()