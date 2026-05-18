#version 330

in vec2 fragTexCoord;
in vec4 fragColor;
out vec4 finalColor;

uniform sampler2D texture0;
uniform float time;
uniform float scanline_strength;
uniform float vignette_strength;

void main() {
    vec2 uv = fragTexCoord;
    vec4 color = texture(texture0, uv);

    float luma = dot(color.rgb, vec3(0.2126, 0.7152, 0.0722));
    float dark_mask = 1.0 - smoothstep(0.0, 0.05, luma);
    vec2 grid_local = fract(uv * vec2(186.0, 141.0));
    float dot_dist = length(grid_local - 0.5);
    float grid_dot = smoothstep(0.10, 0.06, dot_dist);
    color.rgb += vec3(0.06, 0.04, 0.01) * grid_dot * dark_mask * 0.8;

    float scanline = sin(uv.y * 860.0) * 0.5 + 0.5;
    color.rgb *= 1.0 - scanline_strength * (1.0 - pow(scanline, 1.2));

    finalColor = color;
}