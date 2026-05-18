#version 330

in vec2 fragTexCoord;
in vec4 fragColor;
out vec4 finalColor;

uniform sampler2D texture0;
uniform vec2 resolution;
uniform float intensity;

vec3 blur13(sampler2D tex, vec2 uv, vec2 dir) {
    vec3 c = vec3(0.0);
    vec2 o1 = 1.411765 * dir;
    vec2 o2 = 3.294118 * dir;
    vec2 o3 = 5.176471 * dir;
    c += texture(tex, uv).rgb      * 0.196483;
    c += texture(tex, uv + o1).rgb * 0.296907;
    c += texture(tex, uv - o1).rgb * 0.296907;
    c += texture(tex, uv + o2).rgb * 0.094470;
    c += texture(tex, uv - o2).rgb * 0.094470;
    c += texture(tex, uv + o3).rgb * 0.010381;
    c += texture(tex, uv - o3).rgb * 0.010381;
    return c;
}

vec3 bright_pass(vec3 color) {
    float brightness = dot(color, vec3(0.2126, 0.7152, 0.0722));
    float thresh = smoothstep(0.5, 0.85, brightness);
    return color * thresh;
}

void main() {
    vec2 uv = fragTexCoord;
    vec2 px = 1.0 / resolution;
    vec4 orig = texture(texture0, uv);

    if (intensity <= 0.0) { finalColor = orig; return; }

    vec3 bh = blur13(texture0, uv, vec2(px.x * 2.0, 0.0));
    vec3 bv = blur13(texture0, uv, vec2(0.0, px.y * 2.0));
    vec3 bloom1 = bright_pass((bh + bv) * 0.5);

    vec3 bh2 = blur13(texture0, uv, vec2(px.x * 5.0, 0.0));
    vec3 bv2 = blur13(texture0, uv, vec2(0.0, px.y * 5.0));
    vec3 bloom2 = bright_pass((bh2 + bv2) * 0.5) * 0.3;

    vec3 result = orig.rgb + (bloom1 + bloom2) * intensity;

    result = result / (result + vec3(1.0));
    result = pow(result, vec3(1.0 / 1.1));

    finalColor = vec4(result, orig.a);
}