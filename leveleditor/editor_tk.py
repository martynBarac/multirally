import tkinter as tk
from tkinter import filedialog
import json


class Grid:
    def __init__(self, root):
        self.hlines = []
        self.vlines = []
        self.root = root
        self.root.bind("<Configure>", self.window_resize)
        self.default_size = 8

    def create_grid(self, size, width=None, height=None):

        self.default_size = size




        if not width: width = self.root.winfo_screenwidth()
        if not height: height = self.root.winfo_screenheight()

        gap = int(size*self.root.scale)

        if gap <= 4: # Doesnt draw if the gap is to small because it gets laggy
            return

        camx = self.root.canvas.canvasx(0)
        camy = self.root.canvas.canvasy(0)

        xoff = camx - camx%gap
        yoff = camy - camy%gap



        for x in range(0, width, gap):
            line = self.root.canvas.create_line(x+xoff, camy, x+xoff, height+camy, width=1, fill="#222222", tags="gridline")
            self.root.canvas.tag_lower(line)
            self.vlines.append( line )
        for y in range(0, height, gap):
             line = self.root.canvas.create_line(camx, y+yoff, width+camx, y+yoff, width=1, fill="#222222", tags="gridline")
             self.root.canvas.tag_lower(line)
             self.hlines.append( line )

    def clear(self):
        self.root.canvas.delete("gridline")
        self.vlines = []
        self.hlines = []

    def window_resize(self, e):
        pass
        self.clear()
        self.create_grid(self.default_size, e.width, e.height)

    def redraw(self, size, width=None, height=None):
        if not size: size = self.default_size
        self.clear()
        self.create_grid(size, width, height)

class Editor(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.canvas = tk.Canvas(self, width=640, height=480, bg="black")


        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)
        self.canvas.bind("<Motion>", self.mouse_move)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.bind("<KeyPress-s>", self.save_level)
        self.bind("<KeyPress-l>", self.load_level)

        self.bind("<KeyPress-Delete>", self.delete_selection)

        self.bind("<KeyPress-bracketleft>", self.grid_smaller)
        self.bind("<KeyPress-bracketright>", self.grid_larger)


        self.outline_rect = None
        self.rect_start = (0, 0)

        self.drawing = False
        self.x = 0
        self.level = []


        self.canvas.bind("<ButtonPress-2>", self.scroll_start)
        self.canvas.bind("<B2-Motion>", self.scroll_move)

        self.scale = 1

        self.gridsize = 16
        self.grid = Grid(self)
        self.grid.create_grid(self.gridsize)

        self.selected = -1
        self.drag_mouse_start = (0, 0)
        self.drag_rect_start = (0, 0)

    def grid_smaller(self, e):
        self.gridsize/=2
        self.grid.redraw(self.gridsize)

    def grid_larger(self, e):
        self.gridsize*=2
        self.grid.redraw(self.gridsize)


    def delete_selection(self, e):
        self.canvas.delete(self.selected)
        print(self.selected)
        self.level.remove(self.selected[0])
        print(self.level)

    def rect_selected(self, e):
        mx, my = self.canvasx(e.x, self.gridsize), self.canvasy(e.y, self.gridsize)
        rect = self.canvas.find_closest(mx, my)
        self.canvas.itemconfig(rect, outline="green")
        if self.selected != rect:
            self.canvas.itemconfig(self.selected, outline="gray")
            self.selected = rect

        self.drag_mouse_start = (e.x, e.y)
        c = self.canvas.coords(rect)
        self.drag_rect_start = (c[0], c[1])

    def rect_dragged(self, e):
        x0, y0, x1, y1 = self.canvas.coords(self.selected)
        newx = self.drag_rect_start[0] - (self.drag_mouse_start[0] - e.x)
        newy = self.drag_rect_start[1] - (self.drag_mouse_start[1] - e.y)
        newx, newy = self.pos_to_grid([newx, newy])
        self.canvas.move(self.selected, newx-x0, newy-y0)

    def pos_to_grid(self, pos):

        size = self.gridsize*self.scale

        if pos[0] % size < size/2:
            pos[0] -= pos[0] % size
        else:
            pos[0] += size - (pos[0]%size)

        if pos[1] % size < size/2:
            pos[1] -= pos[1] % size
        else:
            pos[1] += size - (pos[1]%size)

        return pos

    def coords_to_rect(self, coords):
        return [coords[0], coords[1], coords[2]-coords[0], coords[3]-coords[1]]

    def rect_to_coords(self, rect):
        return [rect[0], rect[1], rect[2]+rect[0], rect[3]+rect[1]]

    def save_level(self, e):
        ctrl = (e.state & 0x4) != 0
        if ctrl:
            to_save = []
            # Remove all None elements of list
            i = 0
            while i < len(self.level):
                if self.level[i] == None:
                    to_save.pop(i)
                    i -= 1
                else:
                    to_save.append( self.coords_to_rect(self.canvas.coords(self.level[i])) )
                i += 1
            # Save to file
            file = filedialog.asksaveasfile(initialdir=".")
            if file:
                file.write(json.dumps(to_save))
                file.close()
                print("level saved!")

    def load_level(self, e):
        ctrl = (e.state & 0x4) != 0
        if not ctrl:
            return

        path = filedialog.askopenfilename(initialdir=".")
        if path:
            file = open(path, "r")
            data = file.read()
            rects = json.loads(data)
            file.close()
            print("loaded", path)

            # Delete everything in level already
            self.canvas.delete("all")
            self.level = []

            # convert and append all rects (game uses [x, y, w, h], tkinter uses [x0, y0, x1, y1])
            for r in rects:
                coords = self.rect_to_coords(r)
                self.create_rect(coords)

        print(rects, self.level)

    def create_rect(self, coords):
        new_rect = self.canvas.create_rectangle(coords[0], coords[1], coords[2], coords[3], fill="white", outline="gray", width=2 )
        self.canvas.tag_bind(new_rect, "<Button-3>", self.rect_selected)
        self.canvas.tag_bind(new_rect, "<B3-Motion>", self.rect_dragged)
        self.level.append(new_rect)
        return new_rect

    def canvasx(self, x, grid=None):
        return self.canvas.canvasx(x, grid*self.scale)
    def canvasy(self, y, grid=None):
        return self.canvas.canvasy(y, grid*self.scale)

    def zoom(self, event):
        if event.delta == 120:
            factor = 2
        elif event.delta == -120:
            factor = 0.5

        self.canvas.scale(tk.ALL, 0, 0, factor, factor)
        self.scale *= factor

        self.grid.redraw(self.gridsize)

    def scroll_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.grid.redraw(self.gridsize)


    def start_drawing(self, m):
        x, y = self.canvasx(m.x, self.gridsize), self.canvasy(m.y, self.gridsize)


        self.drawing = True
        self.outline_rect = self.canvas.create_rectangle(x, y, x, y, outline="green", width=2)
        self.rect_start = (x, y)

    def stop_drawing(self, m):
        x, y = self.canvasx(m.x, self.gridsize), self.canvasy(m.y, self.gridsize)

        self.drawing = False
        self.canvas.delete(self.outline_rect)
        self.create_rect((x, y, self.rect_start[0], self.rect_start[1]))

    def mouse_move(self, m):
        x, y = self.canvasx(m.x, self.gridsize), self.canvasy(m.y, self.gridsize)

        if self.drawing:
            self.canvas.coords(self.outline_rect, self.rect_start[0], self.rect_start[1], x, y)


if __name__ == "__main__":
    e = Editor()
    e.mainloop()