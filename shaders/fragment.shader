#version 330 core
//https://learnopengl.com/Getting-started/
in vec3 ourColor;
in vec2 TexCoord;

out vec4 FragColor;

uniform sampler2D ourTexture;

void main()
{
    //FragColor = texture(ourTexture, TexCoord) * vec4(ourColor, 1.0);
    FragColor = texture(ourTexture, TexCoord) * vec4(1.0, 1.0, 1.0, 1.0);
    //FragColor = vec4(1.0, 1.0, 1.0, 1.0);
}