#version 330

in vec2 fragTexCoord;
in vec4 fragColor;

out vec4 finalColor;

uniform sampler2D texture0;
uniform vec2 resolution;
uniform float intensity;  

vec3 blur13(sampler2D tex, vec2 uv, vec2 dir) {
    vec3 col = vec3(0.0);
    vec2 off1 = vec2(1.411764705882353) * dir;
    vec2 off2 = vec2(3.2941176470588234) * dir;
    vec2 off3 = vec2(5.176470588235294) * dir;
    col += texture(tex, uv).rgb * 0.1964825501511404;
    col += texture(tex, uv + off1).rgb * 0.2969069646728344;
    col += texture(tex, uv - off1).rgb * 0.2969069646728344;
    col += texture(tex, uv + off2).rgb * 0.09447039785044732;
    col += texture(tex, uv - off2).rgb * 0.09447039785044732;
    col += texture(tex, uv + off3).rgb * 0.010381362401148057;
    col += texture(tex, uv - off3).rgb * 0.010381362401148057;
    return col;
}

vec3 bright_pass(vec3 color) {
    float brightness = dot(color, vec3(0.2126, 0.7152, 0.0722));
    float threshold = 0.35;
    float soft = smoothstep(threshold, threshold + 0.3, brightness);
    return color * soft;
}

void main() {
    vec2 uv = fragTexCoord;
    vec2 px = 1.0 / resolution;

    vec4 original = texture(texture0, uv);

    if (intensity <= 0.0) {
        finalColor = original;
        return;
    }

    vec3 bright = bright_pass(original.rgb);

    vec2 blur_px = px * 2.5;
    vec3 blur_h = blur13(texture0, uv, vec2(blur_px.x, 0.0));
    vec3 blur_v = blur13(texture0, uv, vec2(0.0, blur_px.y));
    vec3 blurred = (blur_h + blur_v) * 0.5;

    vec3 bloom_bright = bright_pass(blurred);

    vec2 blur_wide = px * 6.0;
    vec3 blur_h2 = blur13(texture0, uv, vec2(blur_wide.x, 0.0));
    vec3 blur_v2 = blur13(texture0, uv, vec2(0.0, blur_wide.y));
    vec3 blurred2 = (blur_h2 + blur_v2) * 0.5;
    vec3 bloom_wide = bright_pass(blurred2) * 0.4;

    float bloom_strength = intensity * 1.2;
    vec3 result = original.rgb + (bloom_bright + bloom_wide) * bloom_strength;

    float luma = dot(result, vec3(0.2126, 0.7152, 0.0722));
    vec3 tint = vec3(0.85, 0.95, 1.0);  
    result = mix(result * tint, result, smoothstep(0.0, 0.5, luma));

    result = result / (result + vec3(1.0));
    result = pow(result, vec3(1.0 / 1.15)); 

    finalColor = vec4(result, original.a);
}
