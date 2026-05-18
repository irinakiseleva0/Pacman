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

    float scanline = sin(uv.y * 900.0) * 0.5 + 0.5;
    scanline = pow(scanline, 0.8);
    float scan_factor = 1.0 - scanline_strength * (1.0 - scanline);
    color.rgb *= scan_factor;

    float flicker = 1.0 - 0.012 * sin(time * 47.3 + uv.y * 3.1);
    color.rgb *= flicker;

    vec2 vig_uv = uv * 2.0 - 1.0;
    float vignette = 1.0 - dot(vig_uv * vec2(0.9, 1.1), vig_uv * vec2(0.9, 1.1));
    vignette = smoothstep(0.0, 1.0, vignette);
    vignette = pow(vignette, vignette_strength);
    color.rgb *= vignette;

    float aberr_amount = length(vig_uv) * 0.0018;
    float r = texture(texture0, uv + vec2(aberr_amount, 0.0)).r;
    float b = texture(texture0, uv - vec2(aberr_amount, 0.0)).b;
    color.r = mix(color.r, r, 0.4);
    color.b = mix(color.b, b, 0.4);

    finalColor = color;
}
