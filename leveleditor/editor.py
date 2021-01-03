import pygame as pg

from tkinter import filedialog, Tk

root = Tk()
root.withdraw()


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
        self.drag_mouse_start = () # Mouse pos when start dragging
        self.drag_box_start = () # Box pos when start dragging

        self.cam_drag_start = ()
        self.dragging_cam = False

        self.gridsize = 32
        self.cam = [0, 0]
        self.zoom = 1


    def load_level(self):
        pass

    def save_level(self):


        to_save = self.level
        # Remove all None elements of list
        i = 0
        while i < len(to_save):
            if to_save[i] == None:
                to_save.pop(i)
                i -= 1
            i += 1
        # Save to file
        file = filedialog.asksaveasfile(initialdir=".")
        if file:
            file.write("level = " + str(to_save))
            file.close()
            print("level saved!")


    def run(self):
        while self.running:
            self.event_handle()
            self.update()
            self.draw()

    def update(self):
        if self.dragging:
            mouse = self.get_mouse()
            self.level[self.selection][0] = self.drag_box_start[0] - (self.drag_mouse_start[0] - mouse[0])
            self.level[self.selection][1] = self.drag_box_start[1] - (self.drag_mouse_start[1] - mouse[1])
            self.level[self.selection][0], self.level[self.selection][1] = self.pos_to_grid(self.level[self.selection])

        if self.dragging_cam:
            mouse = list(pg.mouse.get_pos())

            #mouse[0] -= self.cam_drag_start[0]
            #mouse[1] -= self.cam_drag_start[1]

            self.cam[0] -= (mouse[0] - self.cam_drag_start[0])/self.zoom
            self.cam[1] -= (mouse[1] - self.cam_drag_start[1])/self.zoom
            self.cam_drag_start = mouse


    def select(self, x, y):
        new_selection = -1
        selected = False
        for i in range(len(self.level)):
            if self.level[i] != None:
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
            # Check for empty spots first
            for i in range(len(self.level)):
                if self.level[i] == None:
                    self.level[i] = box
                    return
            # If there are no empty spots, append a new item
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

    def get_mouse(self):
        mouse = pg.mouse.get_pos()
        #return ( (mouse[0]-self.cam[0])*self.zoom , (mouse[1]-self.cam[1])*self.zoom )
        return self.cam_to_screen_pos(mouse)

    def event_handle(self):
        for event in  pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.box_start = self.pos_to_grid(self.get_mouse())
                    self.drawing = True

                elif event.button == 2:
                    self.cam_drag_start = pg.mouse.get_pos()
                    self.dragging_cam = True

                elif event.button == 3:
                    mouse = self.get_mouse()
                    if self.select(mouse[0], mouse[1]):
                        self.dragging = True
                        self.drag_mouse_start = self.pos_to_grid(mouse)
                        self.drag_box_start = self.level[self.selection][:2]

                elif event.button == 4: # Scroll up
                    self.zoom *= 2

                elif event.button == 5: # Scroll down
                    self.zoom /= 2

            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.drawing = False
                    box_end = self.pos_to_grid(self.get_mouse())
                    self.add_box(self.box_start, box_end)

                elif event.button == 2:
                    self.dragging_cam = False

                elif event.button == 3:
                    self.dragging = False

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_DELETE:
                    self.level[self.selection] = None
                    self.selection = -1
                elif event.key == pg.K_RIGHTBRACKET:
                    self.gridsize /= 2
                elif event.key == pg.K_LEFTBRACKET:
                    self.gridsize *= 2
                elif event.key == pg.K_s and event.mod&pg.KMOD_CTRL:
                    self.save_level()

    def screen_pos_to_cam(self, pos):
        return ((pos[0]-self.cam[0]) * self.zoom, (pos[1]-self.cam[1]) * self.zoom)

    def cam_to_screen_pos(self, pos):
        return (pos[0]/self.zoom+self.cam[0], pos[1]/self.zoom+self.cam[1])

    def screen_box_to_cam(self, box):
        return [ (box[0]-self.cam[0])*self.zoom, (box[1]-self.cam[1])*self.zoom, box[2]*self.zoom, box[3]*self.zoom ]

    def draw(self):
        screen.fill((0, 0, 0))
        # Draw box outline when drawing a box
        if self.drawing:
            mouse = self.pos_to_grid(self.get_mouse())
            pg.draw.rect(screen, (128, 128, 128), self.screen_box_to_cam( self.get_box(self.box_start[0], self.box_start[1], mouse[0], mouse[1])) , 2)
        # Draw level
        for box in self.level:
            if box != None:
                pg.draw.rect(screen, (255, 255, 255), self.screen_box_to_cam(box))
        # Draw grid
        for x in range(0, SCREEN_SIZE[0], int(self.gridsize*self.zoom)):
            x -= self.cam[0] % self.gridsize*self.zoom
            pg.draw.line(screen, (20, 20, 20), [x, 0], [x, SCREEN_SIZE[1]], 1)
            for y in range(0, SCREEN_SIZE[1], int(self.gridsize*self.zoom)):
                y -= self.cam[1] % self.gridsize*self.zoom
                pg.draw.line(screen, (20, 20, 20), [0, y], [SCREEN_SIZE[0], y], 1)

        # Draw selection box
        if self.selection != -1:
            pg.draw.rect(screen, (0, 255, 0), self.screen_box_to_cam(self.level[self.selection]), 2)

        pg.display.update()

if __name__ == "__main__":
    e = Editor()
    e.run()
    pg.quit()