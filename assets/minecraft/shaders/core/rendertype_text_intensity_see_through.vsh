#version 330

#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:globals.glsl>
#moj_import <minecraft:projection.glsl>
#moj_import <minecraft:interfaces.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;

uniform sampler2D Sampler0;

out vec4 vertexColor;
out vec2 texCoord0;

void main() {
    Data data = interfaces_text(ProjMat, GameTime, Sampler0, Position, UV0, Color);

    gl_Position = ProjMat * ModelViewMat * vec4(data.position, 1.0);
    vertexColor = data.color;
    texCoord0 = data.uv0;
}
