#version 330


#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:globals.glsl>
#moj_import <minecraft:projection.glsl>
#moj_import <minecraft:interfaces.glsl>

in vec3 Position;
in vec2 UV0;
in vec4 Color;

uniform sampler2D Sampler0;


out vec2 texCoord0;
out vec4 vertexColor;// 1.21


void main() {

    //====== Normal shader

    Data data = interfaces(ProjMat, GameTime, Sampler0, Position, UV0);
    texCoord0 = data.uv0;
    vertexColor = Color; // 1.21
    gl_Position = ProjMat * ModelViewMat * vec4(data.position, 1.0);
}
