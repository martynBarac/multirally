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
        self.tex = loadTexture("sprites/car.png")


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
    pg.init()
    display = (640, 480)
    pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    shader = Shader("shaders/vertex.shader", "shaders/fragment.shader")

    s = Sprite()


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

        #r += 0.1


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
        model = glm.rotate(model, glm.radians(-55.0), glm.vec3(1.0, 0.0, 0.0))
        model = glm.translate(model, glm.vec3(x, y, z))

        view = glm.mat4(1.0)
        # note that we're translating the scene in the reverse direction of where we want to move
        view = glm.translate(view, glm.vec3(0.0, 0.0, -3.0))

        glUseProgram(shader.ID)

        #print( [[ c for c in r] for r in trans])
        modelLoc = glGetUniformLocation(shader.ID, "model")
        glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm.value_ptr(model) )
        viewLoc = glGetUniformLocation(shader.ID, "view")
        glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm.value_ptr(view) )
        projLoc = glGetUniformLocation(shader.ID, "proj")
        glUniformMatrix4fv(projLoc, 1, GL_FALSE, glm.value_ptr(proj) )


        s.draw(shader.ID)
        #glPopMatrix()
        #glUseProgram(0)

        #wireCube()
        pg.display.flip()
        pg.time.wait(10)

if __name__ == "__main__":
    main()