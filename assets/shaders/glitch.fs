#version 330

in vec2 fragTexCoord;
in vec4 fragColor;

out vec4 finalColor;

uniform sampler2D texture0;
uniform float time;
uniform float intensity;

float hash(float n) {
    return fract(sin(n) * 43758.5453123);
}

void main() {
    vec2 uv = fragTexCoord;
    float amount = clamp(intensity, 0.0, 1.0);

    float row = floor(uv.y * 220.0);
    float rowNoise = hash(row * 17.13 + floor(time * 42.0));
    float band = step(0.82, rowNoise);
    float drift = (rowNoise - 0.5) * 0.055 * amount * band;

    float wave = sin(uv.y * 95.0 + time * 28.0) * 0.0025 * amount;
    vec2 shiftedUv = uv + vec2(drift + wave, 0.0);

    float chroma = 0.0065 * amount;
    float r = texture(texture0, shiftedUv + vec2(chroma, 0.0)).r;
    float g = texture(texture0, shiftedUv).g;
    float b = texture(texture0, shiftedUv - vec2(chroma, 0.0)).b;
    vec4 col = vec4(r, g, b, texture(texture0, shiftedUv).a);

    float scanline = 0.78 + 0.22 * sin(uv.y * 900.0);
    col.rgb *= mix(1.0, scanline, amount * 0.72);

    float tear = step(0.985, hash(floor(uv.y * 38.0) + floor(time * 18.0)));
    col.rgb += tear * amount * vec3(0.12, 0.02, 0.16);

    float vignette = smoothstep(0.9, 0.18, distance(uv, vec2(0.5)));
    col.rgb *= mix(1.0, vignette, amount * 0.25);

    finalColor = col * fragColor;
}
