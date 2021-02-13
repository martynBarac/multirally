"""
code from
https://stackoverflow.com/questions/56514791/how-to-correctly-add-a-light-to-make-object-get-a-better-view-with-pygame-and-py
https://stackabuse.com/brief-introduction-to-opengl-in-python-with-pyopengl/
https://learnopengl.com/Getting-started/

Useful link
https://github.com/yarolig/OBJFileLoader

"""


import pygame as pg
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from array import array
from ctypes import *

import glm #pip install pyglm
#import pywavefront #pip install pywavefront



# front top right, back top right, back bottom right, front bottom right, front top left, back bottom left, front bottom left, back top left
cubeVertices = ((1,1,1),(1,1,0),(1,0,0),(1,0,1),(0,1,1),(0,0,0),(0,0,1),(0,1,0))
# front, bottom, back, top, left, right
cubeQuads = ((0,3,6,4),(2,5,6,3),(1,2,5,7),(1,0,4,7),(7,4,6,5),(2,3,0,1))

# normals are the out direction for each surface
# used for calculting lighting
normals = [
    ( 0,  0,  1),  # surface 0
    ( 0, -1,  0),  # surface 1
    ( 0,  0, -1),  # surface 2
    ( 0,  1,  0),  # surface 3
    (-1,  0,  0),  # surface 4
    ( 1,  0,  0)   # surface 5
]

cubes = [[1, 1], [-3, 1]]

def loadTexture(filename):
    image = pg.image.load(filename).convert_alpha()
    width, height = image.get_size()
    imgstr = pg.image.tostring(image, "RGBA", True)
    ID = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, ID)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, imgstr
        )

    return ID


pg.init()
display = (640, 480)
pg.display.set_mode(display, DOUBLEBUF|OPENGL)
car_tex = loadTexture("sprites/car.png")
happy_tex = loadTexture("sprites/happy.png")


class Shader:
    def __init__(self, vertex_path, fragment_path):
        with open(vertex_path, "r") as vfile:
            VERTEX_SHADER_SOURCE = vfile.read()
        with open(fragment_path, "r") as ffile:
            FRAGMENT_SHADER_SOURCE = ffile.read()

        # Compile vertex shader
        vertexShader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertexShader, VERTEX_SHADER_SOURCE)
        glCompileShader(vertexShader)

        # Check for errors in vertex shader compilation
        success = glGetShaderiv(vertexShader, GL_COMPILE_STATUS)
        if not success:
            infolog = glGetShaderInfoLog(vertexShader)
            print("vertex shader compilation failed:", infolog)

        # compile fragment shader
        fragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragmentShader, FRAGMENT_SHADER_SOURCE)
        glCompileShader(fragmentShader)

        # Check for errors in fragment shader compilation
        success = glGetShaderiv(fragmentShader, GL_COMPILE_STATUS)
        if not success:
            infolog = glGetShaderInfoLog(fragmentShader)
            print("vertex shader compilation failed:", infolog)

        # Create shader program by linking the vertex and fragment shader
        shaderProgram = glCreateProgram()

        glAttachShader(shaderProgram, vertexShader)
        glAttachShader(shaderProgram, fragmentShader)
        glLinkProgram(shaderProgram)

        # Check for errors in shader linking
        success = glGetProgramiv(shaderProgram, GL_LINK_STATUS)
        if not success:
            infolog = glGetProgramInfoLog(shaderProgram)
            print("shader link failed:", infolog)

        # Delete shadersbecause we dont need them anymore
        glDeleteShader(vertexShader)
        glDeleteShader(fragmentShader)

        self.ID = shaderProgram

class Obj:
    def __init__(self, file):
        f = open(file, "r")
        data = f.readlines()
        f.close()

        self.vertices = []
        self.faces = []
        defined_verts = {}
        objverts = []
        objtexcoords = []
        objnormals = []
        curr_index = 0

        for line in data:
            list = line.split()
            if list[0] == "v": # Vertex position
                for coord in list[1:]:
                    objverts.append(float(coord))
            if list[0] == "vt": # Texture coord
                for texcoord in list[1:]:
                    objtexcoords.append(float(texcoord))
            if list[0] == "vn": # Normal
                for normal in list[1:]:
                    objnormals.append(float(normal))


            if list[0] == "f": # face

                for vertex in list[1:]:
                    """
                    For Every unique index combination in the obj file (ie. 1/5/2)
                    we create a new index and add the position/tex coord/normal.

                    This needs to be done because the obj format has an index for
                    each unique position, an index for each unique normal and
                    and index for each unique texture coord,
                    but opengl only has an index for each position/texture coord/normal combination
                    """
                    vertdat = vertex.split("/")
                    # vertex looks like pos_index/texture_index/normal_index

                    if vertex not in defined_verts:
                        self.faces.append(curr_index)
                        defined_verts[vertex] = curr_index

                        curr_index += 1


                        # Add Vertex Index
                        # we subtract 1 because obj indices start at 1 not 0
                        pos_index = int(vertdat[0])-1
                        # Append Vertex Data
                        self.vertices.append( objverts[pos_index*3] )
                        self.vertices.append( objverts[pos_index*3+1] )
                        self.vertices.append( objverts[pos_index*3+2] )

                        tex_index = int(vertdat[1])-1
                        self.vertices.append( objtexcoords[tex_index*2] )
                        self.vertices.append( objtexcoords[tex_index*2+1] )

                        norm_index = int(vertdat[2])-1
                        self.vertices.append( objnormals[norm_index*3] )
                        self.vertices.append( objnormals[norm_index*3+1] )
                        self.vertices.append( objnormals[norm_index*3+2] )

                    else:
                        self.faces.append(defined_verts[vertex])




class Cube:
    def __init__(self):

        self.verts = (1.0, 1.0, 1.0,
                      1.0, 1.0, 0.0,
                      1.0, 0.0, 0.0,
                      1.0, 0.0, 1.0,
                      0.0, 1.0, 1.0,
                      0.0, 0.0, 0.0,
                      0.0, 0.0, 1.0,
                      0.0, 1.0, 0.0,
                      )
        self.faces = (0,3,6,4,
                      2,5,6,3,
                      1,2,5,7,
                      1,0,4,7,
                      7,4,6,5,
                      2,3,0,1,

                    )


        self.face_arr = array("i", self.faces).tobytes()
        self.vert_arr = array("f", self.verts).tobytes()

        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)
        self.vao = glGenVertexArrays(1)

        # set the current vao, which holds the vbo and ebo settings (for later use)
        glBindVertexArray(self.vao)
        # Setup the vbo which holds all vertices
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo) # make the vbo the current buffer
        glBufferData(GL_ARRAY_BUFFER, len(self.verts) * 4, self.vert_arr, GL_STATIC_DRAW) # give our vertices to the vbo
        # setup the ebo which holds data for which vertices belong to which faces (so one vertex can be in multiple faces)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo) # make the ebo the current buffer
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(self.faces)*4, self.face_arr, GL_STATIC_DRAW) # give our data to the ebo

        # Enable the position attribute (for drawing)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3*4, c_void_p(0))
        glEnableVertexAttribArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        #glDrawArrays(GL_QUADS, 0, 4)
        glDrawElements(GL_QUADS, len(self.faces), GL_UNSIGNED_INT, None)
        #glBindVertexArray(0)

class Mesh:
    def __init__(self, file):
        self.scene = Obj(file)
        self.verts = self.scene.vertices
        self.faces = self.scene.faces

        self.vert_arr = array("f", self.verts).tobytes()
        self.face_arr = array("i", self.faces).tobytes()

        print(self.verts)
        print()
        print(self.faces)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, len(self.verts) * 4, self.vert_arr, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo) # make the ebo the current buffer
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(self.faces)*4, self.face_arr, GL_STATIC_DRAW)

        # Position attribute
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8*4, c_void_p(0))
        glEnableVertexAttribArray(0)

        # texture attribute
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8*4, c_void_p(3*4))
        glEnableVertexAttribArray(2)

        

    def draw(self):
        glBindTexture(GL_TEXTURE_2D, happy_tex)
        glBindVertexArray(self.vao)
        glDrawElements(GL_QUADS, len(self.faces), GL_UNSIGNED_INT, None)
        #glDrawArrays(GL_QUADS, 0, len(self.verts))
        #glBindVertexArray(0)

class Sprite:
    def __init__(self):
        self.verts =[
        #   position        #colour             #Tex coords
            1.0, 1.0,       1.0, 0.0, 0.0,      1.0, 1.0,
            1.0, 0.0,       0.0, 1.0, 0.0,      1.0, 0.0,
            0.0, 0.0,       0.0, 0.0, 1.0,      0.0, 0.0,
            0.0, 1.0,       1.0, 1.0, 1.0,      0.0, 1.0,
        ]

        self.vert_arr = array("f", self.verts).tobytes()
        self.vbo = glGenBuffers(1)
        self.vao = glGenVertexArrays(1)
        self.tex = car_tex


        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, len(self.verts) * 4, self.vert_arr, GL_STATIC_DRAW)
        # Position attribute
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 7 * 4, c_void_p(0))
        glEnableVertexAttribArray(0)
        # color attribute
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 7 * 4, c_void_p(2*4))
        glEnableVertexAttribArray(1)
        # texture attribute
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 7 * 4, c_void_p(5*4))
        glEnableVertexAttribArray(2)

    def draw(self, shaderProgram):

        glBindTexture(GL_TEXTURE_2D, self.tex)



        glBindVertexArray(self.vao)

        glDrawArrays(GL_QUADS, 0, 4)
        glBindVertexArray(0)



def wireCube():
    glBegin(GL_LINES)
    for cubeEdge in cubeEdges:
        for cubeVertex in cubeEdge:
            glVertex3fv(cubeVertices[cubeVertex])
    glEnd()

def solidCube():
    glBegin(GL_QUADS)

    for i, cubeQuad in enumerate(cubeQuads):
        glNormal3fv(normals[i]) # set the normal vector the vertices of the surface
        for cubeVertex in cubeQuad:


            glVertex3fv(cubeVertices[cubeVertex])
    glEnd()


def main():
    clock = pg.time.Clock()

    shader = Shader("shaders/vertex.shader", "shaders/fragment.shader")

    s = Sprite()
    m = Mesh("models/arch.obj")
    c = Cube()


    proj = glm.perspective(glm.radians(45.0), display[0]/display[1], 0.1, 100.0)

    #glTranslatef(0.0, 0.0, 0)

    glLight(GL_LIGHT0, GL_POSITION,  (0, 0, -5, 1))

    #glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
    #glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))

    glEnable(GL_DEPTH_TEST)
    glEnable( GL_BLEND );
    glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA );


    x = 0
    y = 0
    z = 0
    r = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()


        keys = pg.key.get_pressed()
        if keys[pg.K_RIGHT]:
            x += 0.1
        if keys[pg.K_LEFT]:
            x -= 0.1
        if keys[pg.K_UP]:
            y += 0.1
        if keys[pg.K_DOWN]:
            y -= 0.1
        if keys[pg.K_a]:
            z += 0.1
        if keys[pg.K_z]:
            z -= 0.1

        r += 0.01


        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        """
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )

        for cube in cubes:
            glPushMatrix()
            glTranslatef(cube[0], cube[1], 0)
            solidCube()
            glPopMatrix()



        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)
        """
        #glUseProgram(shader)
        #glPushMatrix()
        #glLoadIdentity()

        #glTranslatef(-0.5, 0, 0)
        #glTranslatef(x, y, z)


        model = glm.mat4(1.0)
        model = glm.rotate(model, r, glm.vec3(0.1, 1.0, 0.0))
        model = glm.scale(model, glm.vec3(0.5, 0.5, 0.5))


        view = glm.mat4(1.0)
        # note that we're translating the scene in the reverse direction of where we want to move
        view = glm.translate(view, glm.vec3(x, y, z))
        view = glm.translate(view, glm.vec3(0.0, 0.0, -5.0))

        glUseProgram(shader.ID)

        #print( [[ c for c in r] for r in trans])
        modelLoc = glGetUniformLocation(shader.ID, "model")
        glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm.value_ptr(model) )
        viewLoc = glGetUniformLocation(shader.ID, "view")
        glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm.value_ptr(view) )
        projLoc = glGetUniformLocation(shader.ID, "proj")
        glUniformMatrix4fv(projLoc, 1, GL_FALSE, glm.value_ptr(proj) )


        #s.draw(shader.ID)
        m.draw()
        #c.draw()
        #glPopMatrix()
        #glUseProgram(0)

        #wireCube()
        pg.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()