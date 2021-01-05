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
        self.screenw = 0
        self.screenh = 0
        self.lastxoff = 0
        self.lastyoff = 0
        self.gap = 0

    def update_pos(self):
        camx = self.root.canvas.canvasx(0)
        camy = self.root.canvas.canvasy(0)



        xoff = camx - camx%self.gap
        yoff = camy - camy%self.gap
        #xmove = xoff - self.lastxoff
        #ymove = yoff - self.lastyoff
        for x in range(0, len(self.vlines)):
            self.root.canvas.coords(self.vlines[x], (x*self.gap)+xoff, camy, (x*self.gap)+xoff, self.screenh+camy)
            #print("x", self.root.canvas.coords(self.vlines[x]))
        for y in range(0, len(self.hlines)):

            self.root.canvas.coords(self.hlines[y], camx, (y*self.gap)+yoff, self.screenw+camx, (y*self.gap)+yoff)
            #print("y", self.root.canvas.coords(self.hlines[y]))
        #self.lastxoff = xoff
        #self.lastyoff = yoff

    def create_grid(self, size, width=None, height=None):

        self.default_size = size




        if not width: width = self.root.winfo_screenwidth()
        if not height: height = self.root.winfo_screenheight()
        self.screenw = width
        self.screenh = height

        self.gap = int(size*self.root.scale)

        if self.gap <= 2: # Doesnt draw if the gap is to small because it gets laggy
            return

        camx = self.root.canvas.canvasx(0)
        camy = self.root.canvas.canvasy(0)

        xoff = camx - camx%self.gap
        yoff = camy - camy%self.gap


        for x in range(0, width, self.gap):
            line = self.root.canvas.create_line(x+xoff, camy, x+xoff, height+camy, width=1, fill="#222222", tags="gridline")
            self.root.canvas.tag_lower(line)
            self.vlines.append( line )
        for y in range(0, height, self.gap):
            line = self.root.canvas.create_line(camx, y+yoff, width+camx, y+yoff, width=1, fill="#222222", tags="gridline")
            self.root.canvas.tag_lower(line)
            self.hlines.append( line )


    def clear(self):
        self.root.canvas.delete("gridline")
        self.vlines = []
        self.hlines = []

    def window_resize(self, e):
        self.clear()
        self.create_grid(self.default_size, e.width, e.height)

    def redraw(self, size, width=None, height=None):
        if not size: size = self.default_size
        self.clear()
        self.create_grid(size, width, height)


class ToolFrame(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root, width=100)
        self.label = tk.Label()

        buttons_text = ["Walls", "Spawn"]
        self.buttons = []

        # Create buttons
        for i in range(2):
            button = tk.Button(self, text= buttons_text[i], command= lambda id=i: self.select_button(id))
            self.buttons.append(button)
            button.pack()


        self.tool = -1
        self.select_button(0)

    def select_button(self, button_id):
        if self.tool != -1:
            self.buttons[self.tool].config(relief=tk.RAISED)
        self.buttons[button_id].config(relief=tk.SUNKEN)
        self.tool = button_id


class Editor(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.canvas = tk.Canvas(self, width=640, height=480, bg="black")
        self.frm_items = ToolFrame(self)

        self.frm_items.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)
        self.canvas.bind("<B1-Motion>", self.drag_draw)
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
        self.level = self.empty_level()


        self.canvas.bind("<ButtonPress-2>", self.scroll_start)
        self.canvas.bind("<B2-Motion>", self.scroll_move)



        self.gridsize = 16
        self.scale = 1
        self.grid = Grid(self)
        self.grid.create_grid(self.gridsize)


        self.selected = -1
        self.drag_mouse_start = (0, 0)
        self.drag_rect_start = (0, 0)

    def empty_level(self):
        return {"wall":[], "spawn":[]}

    def grid_smaller(self, e):
        self.gridsize/=2
        self.grid.redraw(self.gridsize)

    def grid_larger(self, e):
        self.gridsize*=2
        self.grid.redraw(self.gridsize)

    def delete_selection(self, e):
        if self.selected != -1:
            type = self.canvas.gettags(self.selected)[0]
            self.canvas.delete(self.selected)
            self.level[type].remove(self.selected[0])
            self.selected = -1

    def rect_selected(self, e):
        mx, my = self.canvas.canvasx(e.x), self.canvas.canvasy(e.y)
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
            to_save = {}

            i = 0
            new_wall = []
            while i < len(self.level["wall"]):
                new_wall.append( self.coords_to_rect(self.canvas.coords(self.level["wall"][i])) )
                i += 1
            new_spawn = []
            for i in range(len(self.level["spawn"])):
                x0, y0, x1, y1 = self.canvas.coords(self.level["spawn"][i])
                new_spawn.append([x0, y0])

            to_save["wall"] = new_wall
            to_save["spawn"] = new_spawn

            # Save to file
            file = filedialog.asksaveasfile(initialdir="../levels")
            if file:
                file.write(json.dumps(to_save))
                file.close()
                print("level saved!")

    def load_level(self, e):
        ctrl = (e.state & 0x4) != 0
        if not ctrl:
            return

        path = filedialog.askopenfilename(initialdir="../levels")
        if path:
            file = open(path, "r")
            data = file.read()
            loaded_level = json.loads(data)
            file.close()
            print("loaded", path)

            # Delete everything in level already
            self.canvas.delete("all")
            self.level = self.empty_level()

            # convert and append all rects (game uses [x, y, w, h], tkinter uses [x0, y0, x1, y1])
            for r in loaded_level["wall"]:
                coords = self.rect_to_coords(r)
                self.create_rect(coords)

            for s in loaded_level["spawn"]:
                self.create_spawn(s)


    def create_rect(self, coords):
        new_rect = self.canvas.create_rectangle(coords[0], coords[1], coords[2], coords[3], fill="white", outline="gray", width=2, tags="wall" )
        self.canvas.tag_bind(new_rect, "<Button-3>", self.rect_selected)
        self.canvas.tag_bind(new_rect, "<B3-Motion>", self.rect_dragged)
        self.level["wall"].append(new_rect)
        return new_rect

    def create_spawn(self, pos):
        spawn = self.canvas.create_rectangle(pos[0], pos[1], pos[0]+8*self.scale, pos[1]+8*self.scale, fill="blue", tags="spawn")
        self.canvas.tag_bind(spawn, "<Button-3>", self.rect_selected)
        self.canvas.tag_bind(spawn, "<B3-Motion>", self.rect_dragged)
        self.level["spawn"].append(spawn)

    def canvasx(self, x, grid=None):
        return self.canvas.canvasx(x, grid*self.scale)

    def canvasy(self, y, grid=None):
        return self.canvas.canvasy(y,  grid*self.scale)

    def canvas_scale(self, x, y):
        return ( int(self.canvas.canvasx(x)/self.scale), int(self.canvas.canvasy(y)/self.scale) )

    def zoom(self, event):
        if event.delta == 120:
            factor = 2
        elif event.delta == -120:
            factor = 0.5

        mouse_b = self.canvas_scale(event.x, event.y) # Mouse pos before zoom

        # scale canvas
        self.canvas.scale(tk.ALL, 0, 0, factor, factor)
        self.scale *= factor

        mouse_a = self.canvas_scale(event.x, event.y) # Mouse pos after zoom

        # Move canvas so mouse stays in the same position
        movex = mouse_a[0] - mouse_b[0]
        movey = mouse_a[1] - mouse_b[1]
        self.canvas.scan_mark(0, 0)
        self.canvas.scan_dragto(int(movex*self.scale), int(movey*self.scale), gain=1)

        # Redraw grid
        self.grid.redraw(self.gridsize)

    def scroll_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.grid.update_pos()


    def start_drawing(self, e):
        if self.frm_items.tool == 0:
            self.start_drawing_wall(e)
        elif self.frm_items.tool == 1:
            self.draw_spawn(e)
    def stop_drawing(self, e):
        if self.frm_items.tool == 0:
            self.stop_drawing_wall(e)
    def drag_draw(self, e):
        if self.frm_items.tool == 0:
            self.drag_drawing_wall(e)

    def start_drawing_wall(self, m):
        x, y = self.canvasx(m.x, self.gridsize), self.canvasy(m.y, self.gridsize)

        self.drawing = True
        self.outline_rect = self.canvas.create_rectangle(x, y, x, y, outline="green", width=2)
        self.rect_start = (x, y)

    def stop_drawing_wall(self, m):
        x, y = self.canvasx(m.x, self.gridsize), self.canvasy(m.y, self.gridsize)

        self.drawing = False
        self.canvas.delete(self.outline_rect)
        self.create_rect((x, y, self.rect_start[0], self.rect_start[1]))

    def drag_drawing_wall(self, e):
        x, y = self.canvasx(e.x, self.gridsize), self.canvasy(e.y, self.gridsize)

        if self.drawing:
            self.canvas.coords(self.outline_rect, self.rect_start[0], self.rect_start[1], x, y)

    def draw_spawn(self, e):
        pos = self.canvasx(e.x, self.gridsize), self.canvasy(e.y, self.gridsize)
        self.create_spawn(pos)



if __name__ == "__main__":
    e = Editor()
    e.mainloop()