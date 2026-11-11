// Sunset Meadow — a small Japanese-style sunset grass field you can run around in.
// Run: python3 -m http.server 8137 in this folder and open http://127.0.0.1:8137/
import * as THREE from 'three';

const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(55, 1, 0.1, 6000);

const TORII = { x: -10, z: -78 };
function terrainH(x, z) {
  let h = Math.sin(x * 0.021 + 1.3) * Math.cos(z * 0.017 - 0.6) * 5.0;
  h += Math.sin(x * 0.047 + z * 0.031 + 2.1) * 2.2;
  h += Math.sin(z * 0.083 - x * 0.059 + 0.4) * 0.9;
  const dx = x - TORII.x, dz = z - TORII.z;
  return h + 9.0 * Math.exp(-(dx * dx + dz * dz) / 968.0);
}
const az = new THREE.Vector2(TORII.x, TORII.z).normalize();
const EL = 7 * Math.PI / 180;
const sunDir = new THREE.Vector3(az.x * Math.cos(EL), Math.sin(EL), az.y * Math.cos(EL));

const G = {
  uTime: { value: 0 }, uSunDir: { value: sunDir }, uPlayer: { value: new THREE.Vector3() },
  uCamRight: { value: new THREE.Vector2(1, 0) },
};
const COMMON = /* glsl */`
uniform float uTime; uniform vec3 uSunDir; uniform vec3 uPlayer; uniform vec2 uCamRight;
const vec2 WIND = vec2(0.93, 0.36);
const vec3 SUNCOL = vec3(2.2, 1.15, 0.5);
float hash12(vec2 p){ vec3 q = fract(vec3(p.xyx) * .1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float vnoise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.-2.*f);
  return mix(mix(hash12(i), hash12(i+vec2(1,0)), f.x), mix(hash12(i+vec2(0,1)), hash12(i+vec2(1,1)), f.x), f.y); }
float fbm(vec2 p){ float a = .5, s = 0.; for(int i=0;i<5;i++){ s += a*vnoise(p); p = p*2.03 + vec2(17.1,3.7); a *= .5; } return s; }
float terrainH(vec2 p){
  float h = sin(p.x*0.021+1.3)*cos(p.y*0.017-0.6)*5.0;
  h += sin(p.x*0.047+p.y*0.031+2.1)*2.2;
  h += sin(p.y*0.083-p.x*0.059+0.4)*0.9;
  vec2 d = p - vec2(-10.0,-78.0);
  return h + 9.0*exp(-dot(d,d)/968.0);
}
vec3 skyGradient(vec3 d){
  float y = clamp(d.y, 0.0, 1.0);
  float sa = dot(normalize(d.xz + 1e-5), normalize(uSunDir.xz)) * 0.5 + 0.5;
  vec3 zen = vec3(0.045, 0.06, 0.22);
  vec3 mid = mix(vec3(0.22,0.16,0.42), vec3(0.55,0.20,0.38), sa);
  vec3 low = mix(vec3(0.55,0.33,0.50), vec3(1.25,0.50,0.22), sa*sa);
  vec3 hor = mix(vec3(0.62,0.45,0.55), vec3(1.7,0.95,0.38), sa*sa*sa);
  vec3 c = mix(hor, low, smoothstep(0.0, 0.10, y));
  c = mix(c, mid, smoothstep(0.06, 0.32, y));
  return mix(c, zen, smoothstep(0.25, 0.85, y));
}
vec3 applyFog(vec3 col, vec3 wpos){
  vec3 v = wpos - cameraPosition; float dist = length(v); vec3 d = v / max(dist, 1e-4);
  float f = 1.0 - exp(-pow(dist * 0.0034, 1.25));
  float sd = max(dot(d, uSunDir), 0.0);
  vec3 fc = skyGradient(normalize(vec3(d.x, 0.015, d.z))) + vec3(1.3,0.55,0.18) * pow(sd, 8.0) * 0.6;
  f = min(1.0, f + pow(sd, 16.0) * 0.2 * smoothstep(5.0, 60.0, dist));
  return mix(col, fc, f);
}
float gustAt(vec2 w){
  vec2 q = w*0.045 - WIND*uTime*0.55;
  float g = vnoise(q)*0.6 + vnoise(q*2.7+5.0)*0.25 + (sin(dot(w,WIND)*0.16 - uTime*1.7)*0.5+0.5)*0.25;
  return smoothstep(0.25, 0.85, g);
}
float playerShadow(vec2 p){
  vec2 L = -normalize(uSunDir.xz); vec2 a = uPlayer.xz; vec2 ab = L * 13.0;
  float t = clamp(dot(p-a, ab)/dot(ab,ab), 0.0, 1.0);
  float r = 0.3 * (1.0 + 1.2*t);
  return (1.0 - smoothstep(r*0.5, r*1.3, length(p - (a + ab*t)))) * (1.0 - 0.5*t);
}
vec3 shadeGrass(vec3 alb, float t, float gust, float shade, vec3 wpos){
  vec3 V = normalize(wpos - cameraPosition);
  float toward = max(dot(normalize(V.xz), normalize(uSunDir.xz)), 0.0);
  float s = 1.0 - shade;
  vec3 c = alb * (mix(vec3(0.16,0.13,0.14), vec3(0.30,0.24,0.46), 0.35+0.65*t) + SUNCOL*(0.07+0.45*(1.0-toward))*(0.5+0.5*t)*s);
  c += alb * SUNCOL * pow(toward, 3.0) * t*t * 2.6 * s;
  c += SUNCOL * pow(toward, 8.0) * pow(t, 4.0) * 0.9 * s;
  c += vec3(0.55,0.50,0.16) * gust * t*t * 0.22 * (0.35+0.65*s);
  return c;
}
vec3 tonemap(vec3 x){ x *= 0.5; x = clamp((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14), 0.0, 1.0); return pow(x, vec3(1.0/2.2)); }
`;

// ---------- sky ----------
const sky = new THREE.Mesh(new THREE.SphereGeometry(3000, 48, 24), new THREE.ShaderMaterial({
  uniforms: G, side: THREE.BackSide, depthWrite: false, depthTest: false,
  vertexShader: `varying vec3 vDir; void main(){ vDir = position; gl_Position = projectionMatrix * viewMatrix * vec4(position + cameraPosition, 1.0); }`,
  fragmentShader: COMMON + /* glsl */`
  varying vec3 vDir;
  void main(){
    vec3 d = normalize(vDir); vec3 c = skyGradient(d);
    float sd = dot(d, uSunDir);
    c += vec3(1.5,0.62,0.22) * (pow(max(sd,0.0), 48.0)*0.9 + pow(max(sd,0.0), 7.0)*0.22);
    float R = 0.075; float ang = acos(clamp(sd,-1.0,1.0));
    float disc = 1.0 - smoothstep(R-0.003, R+0.003, ang);
    c = mix(c, mix(vec3(5.5,1.25,0.28), vec3(7.5,4.6,1.6), smoothstep(-R, R, d.y-uSunDir.y)), disc);
    vec2 f = normalize(uSunDir.xz); vec2 r = vec2(-f.y, f.x);
    vec2 p = vec2(dot(d.xz, r), dot(d.xz, f)) / (max(d.y,0.0) + 0.09);
    float n = fbm(vec2(p.x*0.22 + uTime*0.004, p.y*1.05 + 4.0));
    n += 0.25*fbm(vec2(p.x*0.9 - uTime*0.006, p.y*3.3)) - 0.125;
    float a = smoothstep(0.50, 0.62, n) * smoothstep(0.015, 0.10, d.y);
    float sa = max(dot(normalize(d.xz), f), 0.0);
    vec3 cc = mix(mix(vec3(1.05,0.50,0.48), vec3(2.3,1.15,0.42), pow(sa,3.0)), mix(vec3(0.26,0.17,0.36), vec3(0.62,0.24,0.30), sa), smoothstep(0.50,0.85,n));
    c = mix(c, cc, a*0.92);
    gl_FragColor = vec4(tonemap(c), 1.0);
  }`,
}));
sky.renderOrder = -1; sky.frustumCulled = false; scene.add(sky);

// ---------- ground ----------
const ROOT = new THREE.Vector3(0.012, 0.05, 0.03), TIP = new THREE.Vector3(0.22, 0.34, 0.06);
const ground = new THREE.Mesh(new THREE.PlaneGeometry(1400, 1400, 280, 280).rotateX(-Math.PI / 2), new THREE.ShaderMaterial({
  uniforms: { ...G, uRoot: { value: ROOT }, uTip: { value: TIP } },
  vertexShader: COMMON + `varying vec3 vW; void main(){ vec3 p = position; p.y = terrainH(p.xz); vW = p; gl_Position = projectionMatrix * viewMatrix * vec4(p,1.0); }`,
  fragmentShader: COMMON + /* glsl */`
  uniform vec3 uRoot, uTip; varying vec3 vW;
  void main(){
    float cover = smoothstep(30.0, 56.0, length(vW.xz - uPlayer.xz));
    float tex = vnoise(vW.xz*vec2(2.3,0.9))*0.5 + vnoise(vW.xz*0.35)*0.5;
    float t = mix(0.05, 0.42 + 0.25*tex, cover);
    vec3 alb = mix(uRoot, uTip, t) * mix(vec3(1.0), vec3(1.45,1.05,0.5), smoothstep(0.5,0.85,vnoise(vW.xz*0.031+11.0)));
    vec3 c = shadeGrass(alb, t, gustAt(vW.xz)*cover, playerShadow(vW.xz), vW);
    gl_FragColor = vec4(tonemap(applyFog(c, vW)), 1.0);
  }`,
}));
ground.frustumCulled = false; scene.add(ground);

// ---------- grass ----------
function makeGrass(count, S, fade0, fade1, segs, width, height, wGrow) {
  const pos = [], idx = [];
  for (let i = 0; i < segs; i++) { const t = i / segs, w = 0.5 * (1 - t * t * 0.85); pos.push(-w, t, 0, w, t, 0); }
  pos.push(0, 1, 0);
  for (let i = 0; i < segs - 1; i++) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
  idx.push((segs - 1) * 2, (segs - 1) * 2 + 1, segs * 2);
  const n = Math.floor(Math.sqrt(count)), N = n * n, off = new Float32Array(N * 2), rnd = new Float32Array(N * 4);
  for (let i = 0; i < N; i++) {
    off[i * 2] = ((i % n) + Math.random()) * S / n; off[i * 2 + 1] = (Math.floor(i / n) + Math.random()) * S / n;
    for (let k = 0; k < 4; k++) rnd[i * 4 + k] = Math.random();
  }
  const g = new THREE.InstancedBufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx);
  g.setAttribute('aOffset', new THREE.InstancedBufferAttribute(off, 2));
  g.setAttribute('aRand', new THREE.InstancedBufferAttribute(rnd, 4));
  g.instanceCount = N;
  const m = new THREE.Mesh(g, new THREE.ShaderMaterial({
    side: THREE.DoubleSide,
    uniforms: { ...G, uRoot: { value: ROOT }, uTip: { value: TIP }, uS: { value: S }, uFade: { value: new THREE.Vector2(fade0, fade1) },
      uBlade: { value: new THREE.Vector3(width, height, wGrow) } },
    vertexShader: COMMON + /* glsl */`
    attribute vec2 aOffset; attribute vec4 aRand;
    uniform float uS; uniform vec2 uFade; uniform vec3 uBlade;
    varying float vT; varying float vGust; varying float vShade; varying vec3 vW; varying vec3 vTint;
    void main(){
      vec2 c = uPlayer.xz;
      vec2 w = mod(aOffset - c + 0.5*uS, uS) - 0.5*uS + c;
      float dist = length(w - c);
      float fade = 1.0 - smoothstep(uFade.x, uFade.y, dist);
      float gy = terrainH(w);
      float bh = uBlade.y * mix(0.55,1.15,aRand.y) * mix(0.75,1.25,vnoise(w*0.11+3.0)) * fade;
      float bw = uBlade.x * (1.0 + dist*uBlade.z) * mix(0.8,1.2,aRand.w);
      float ang = aRand.x*6.2831853; vec2 dir = vec2(cos(ang), sin(ang));
      vec2 axis = normalize(dir + uCamRight * (dot(dir,uCamRight) >= 0.0 ? 1.0 : -1.0) * 0.9);
      float g = gustAt(w);
      vec2 bend = WIND * (0.18 + 0.75*g + sin(uTime*(2.5+aRand.z*2.0) + aRand.x*40.0)*0.06) + vec2(-dir.y,dir.x)*(aRand.z-0.5)*0.55;
      vec2 dp = w - uPlayer.xz; float pd = length(dp);
      float push = (1.0 - smoothstep(0.25,1.3,pd)) * (1.0 - smoothstep(0.3,1.6,uPlayer.y-gy));
      bend += dp / max(pd,1e-3) * push * 1.3;
      float t = position.y;
      vec3 p; p.xz = w + axis*position.x*bw + bend*bh*t*t;
      p.y = gy + bh*t*(1.0 - 0.3*min(length(bend),1.5)*t)*(1.0 - 0.45*push);
      vT = t; vGust = g; vShade = playerShadow(w); vW = p;
      vTint = mix(vec3(1.0), vec3(1.45,1.05,0.5), smoothstep(0.5,0.85,vnoise(w*0.031+11.0))) * mix(0.82,1.18,aRand.w);
      gl_Position = projectionMatrix * viewMatrix * vec4(p,1.0);
    }`,
    fragmentShader: COMMON + /* glsl */`
    uniform vec3 uRoot, uTip;
    varying float vT; varying float vGust; varying float vShade; varying vec3 vW; varying vec3 vTint;
    void main(){
      vec3 alb = mix(uRoot, uTip, vT*vT*0.6 + vT*0.4) * vTint;
      gl_FragColor = vec4(tonemap(applyFog(shadeGrass(alb, vT, vGust, vShade, vW), vW)), 1.0);
    }`,
  }));
  m.frustumCulled = false; scene.add(m);
}
makeGrass(110000, 44, 14, 21, 4, 0.085, 0.62, 0.0);
makeGrass(230000, 124, 48, 61, 2, 0.16, 0.72, 0.03);

// ---------- toon props ----------
function toon(hex, emissive = 0) {
  return new THREE.ShaderMaterial({
    uniforms: { ...G, uColor: { value: new THREE.Color(hex) }, uEm: { value: emissive } }, side: THREE.DoubleSide,
    vertexShader: `varying vec3 vN; varying vec3 vW; void main(){ vec4 w = modelMatrix*vec4(position,1.0); vW = w.xyz; vN = normalize(mat3(modelMatrix)*normal); gl_Position = projectionMatrix*viewMatrix*w; }`,
    fragmentShader: COMMON + /* glsl */`
    uniform vec3 uColor; uniform float uEm; varying vec3 vN; varying vec3 vW;
    void main(){
      vec3 N = normalize(vN); if(!gl_FrontFacing) N = -N;
      vec3 V = normalize(cameraPosition - vW);
      float lit = smoothstep(-0.02, 0.10, dot(N, uSunDir));
      vec3 c = uColor * (mix(vec3(0.16,0.13,0.14), vec3(0.30,0.24,0.46), N.y*0.5+0.5) + SUNCOL*lit);
      float fres = pow(1.0 - max(dot(N,V),0.0), 3.0);
      c += SUNCOL * fres * (0.15 + 0.85*smoothstep(0.3,-0.5,dot(V,uSunDir))) * 0.5 * (0.4+0.6*uColor);
      c += uColor * uEm;
      gl_FragColor = vec4(tonemap(applyFog(c, vW)), 1.0);
    }`,
  });
}
const add = (parent, geo, mat, x, y, z) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); parent.add(m); return m; };
const colliders = [];

// torii
{
  const g = new THREE.Group(), red = toon(0xd2351f), dark = toon(0x1c1a22);
  for (const s of [-1, 1]) {
    add(g, new THREE.CylinderGeometry(0.3, 0.37, 6.2, 16), red, s * 2.6, 3.1, 0).rotation.z = -s * 0.035;
    add(g, new THREE.CylinderGeometry(0.5, 0.56, 0.5, 12), dark, s * 2.65, 0.25, 0);
  }
  add(g, new THREE.BoxGeometry(6.6, 0.42, 0.34), red, 0, 4.6, 0);
  add(g, new THREE.BoxGeometry(0.5, 0.9, 0.2), red, 0, 5.25, 0);
  const curve = (geo) => { const p = geo.attributes.position; for (let i = 0; i < p.count; i++) p.setY(i, p.getY(i) + Math.pow(p.getX(i) / 4.3, 2) * 0.5); return geo; };
  add(g, curve(new THREE.BoxGeometry(7.6, 0.42, 0.5, 16, 1, 1)), red, 0, 5.9, 0);
  add(g, curve(new THREE.BoxGeometry(8.6, 0.32, 0.72, 16, 1, 1)), dark, 0, 6.28, 0);
  g.scale.setScalar(1.3);
  g.position.set(TORII.x, terrainH(TORII.x, TORII.z) - 0.2, TORII.z);
  g.rotation.y = Math.atan2(az.x, az.y);
  scene.add(g);
  const c = Math.cos(g.rotation.y), s = Math.sin(g.rotation.y);
  for (const k of [-1, 1]) colliders.push({ x: TORII.x + k * 3.4 * c, z: TORII.z - k * 3.4 * s, r: 0.7 });
}
// stone lanterns along the way
for (let i = 0; i < 6; i++) {
  const t = 0.16 + i * 0.13, side = i % 2 ? 1 : -1;
  const x = TORII.x * t - az.y * side * 2.6, z = TORII.z * t + az.x * side * 2.6;
  const g = new THREE.Group(), stone = toon(0x6f6a78);
  add(g, new THREE.CylinderGeometry(0.34, 0.4, 0.18, 6), stone, 0, 0.09, 0);
  add(g, new THREE.CylinderGeometry(0.11, 0.14, 0.95, 6), stone, 0, 0.65, 0);
  add(g, new THREE.CylinderGeometry(0.36, 0.2, 0.14, 6), stone, 0, 1.19, 0);
  add(g, new THREE.BoxGeometry(0.34, 0.34, 0.34), toon(0xffb347, 6), 0, 1.43, 0);
  add(g, new THREE.ConeGeometry(0.52, 0.3, 6), stone, 0, 1.75, 0);
  g.position.set(x, terrainH(x, z) - 0.05, z); scene.add(g);
  colliders.push({ x, z, r: 0.45 });
}
// sakura tree
{
  const g = new THREE.Group(), bark = toon(0x2a1a1c), pink = toon(0xf7a8c4, 0.25);
  add(g, new THREE.CylinderGeometry(0.32, 0.5, 3.6, 8), bark, 0, 1.8, 0).rotation.z = 0.12;
  add(g, new THREE.CylinderGeometry(0.16, 0.28, 3.2, 6), bark, 0.9, 4.1, 0.2).rotation.z = -0.7;
  add(g, new THREE.CylinderGeometry(0.16, 0.28, 3.2, 6), bark, -0.9, 4.3, -0.3).rotation.z = 0.75;
  for (const [x, y, z, r] of [[0, 6.2, 0, 2.6], [1.9, 5.6, 0.4, 2.0], [-2.0, 5.8, -0.4, 2.1], [0.3, 5.5, 1.9, 1.9], [-0.4, 5.4, -1.8, 1.9],
    [1.2, 7.2, -0.6, 1.7], [-1.1, 7.3, 0.5, 1.7], [2.9, 4.9, -0.8, 1.4], [-3.0, 5.0, 0.7, 1.5], [0.2, 8.0, 0.1, 1.4]])
    add(g, new THREE.SphereGeometry(r, 14, 10), pink, x, y, z).scale.y = 0.8;
  const x = -22, z = -30; g.scale.setScalar(1.25); g.position.set(x, terrainH(x, z) - 0.1, z); scene.add(g);
  colliders.push({ x, z, r: 0.9 });
}
// far mountain rings + fuji
function ridge(a, seed) { let s = 0, amp = 0.5, tot = 0; [3, 5, 8, 13, 21, 34, 55].forEach((k, i) => { const v = 1 - Math.abs(Math.sin(k * a * 0.5 + seed * 12.9898 + i * 4.13)); s += v * v * amp; tot += amp; amp *= 0.62; }); return s / tot; }
const hazeMat = (tint, k) => new THREE.ShaderMaterial({
  uniforms: { ...G, uTint: { value: new THREE.Vector3(...tint) }, uK: { value: k } }, side: THREE.DoubleSide,
  vertexShader: `attribute float aH; varying float vH; varying vec3 vW; void main(){ vH = aH; vec4 w = modelMatrix*vec4(position,1.0); vW = w.xyz; gl_Position = projectionMatrix*viewMatrix*w; }`,
  fragmentShader: COMMON + `uniform vec3 uTint; uniform float uK; varying float vH; varying vec3 vW;
    void main(){ vec3 d = normalize(vW - cameraPosition); vec3 haze = skyGradient(normalize(vec3(d.x,0.02,d.z)));
      float snow = smoothstep(0.80, 0.84, vH + 0.03*sin(atan(vW.z, vW.x)*90.0)) * step(1.5, uK);
      vec3 c = mix(haze, haze*uTint, min(uK,1.0)*smoothstep(0.0,0.6,vH));
      c = mix(c, vec3(1.25,0.82,0.78), snow*0.85);
      gl_FragColor = vec4(tonemap(c),1.0); }`,
});
const sunA = Math.atan2(az.y, az.x);
function ring(R, hMin, hMax, seed, tint, k) {
  const N = 360, pos = [], hh = [], idx = [];
  for (let i = 0; i <= N; i++) {
    const a = i / N * Math.PI * 2; let da = Math.abs(a - ((sunA + Math.PI * 2) % (Math.PI * 2))); da = Math.min(da, Math.PI * 2 - da);
    const top = (hMin + (hMax - hMin) * ridge(a, seed)) * (1 - 0.45 * Math.exp(-da * da / 0.12));
    pos.push(Math.cos(a) * R, -40, Math.sin(a) * R, Math.cos(a) * R, top, Math.sin(a) * R); hh.push(0, 1);
    if (i < N) { const b = i * 2; idx.push(b, b + 1, b + 2, b + 1, b + 3, b + 2); }
  }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('aH', new THREE.Float32BufferAttribute(hh, 1)); g.setIndex(idx);
  const m = new THREE.Mesh(g, hazeMat(tint, k)); m.frustumCulled = false; scene.add(m);
}
ring(1500, 90, 210, 3.1, [0.72, 0.62, 0.86], 0.45);
ring(1050, 60, 150, 1.7, [0.52, 0.44, 0.74], 0.7);
ring(680, 30, 80, 0.4, [0.36, 0.30, 0.58], 0.9);
{
  const H = 520, R = 900, pts = [], hs = [];
  for (let i = 0; i <= 40; i++) { const r = 0.035 * R + (i / 40) * R * 0.965; pts.push(new THREE.Vector2(r, H * (Math.exp(-3.2 * r / R) - Math.exp(-3.2)) / (1 - Math.exp(-3.2)))); }
  const g = new THREE.LatheGeometry(pts, 72); const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) hs.push(p.getY(i) / (H * 0.9));
  g.setAttribute('aH', new THREE.Float32BufferAttribute(hs, 1));
  const m = new THREE.Mesh(g, hazeMat([0.40, 0.33, 0.62], 2.0));
  const a = sunA + 0.40; m.position.set(Math.cos(a) * 1900, -30, Math.sin(a) * 1900); m.frustumCulled = false; scene.add(m);
}

// ---------- falling petals ----------
{
  const N = 1400, seed = new Float32Array(N * 4); for (let i = 0; i < N * 4; i++) seed[i] = Math.random();
  const g = new THREE.InstancedBufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute([-1, -1, 0, 1, -1, 0, 1, 1, 0, -1, 1, 0], 3));
  g.setIndex([0, 1, 2, 0, 2, 3]); g.setAttribute('aSeed', new THREE.InstancedBufferAttribute(seed, 4)); g.instanceCount = N;
  const m = new THREE.Mesh(g, new THREE.ShaderMaterial({
    uniforms: G, side: THREE.DoubleSide,
    vertexShader: COMMON + /* glsl */`
    attribute vec4 aSeed; varying vec2 vP; varying vec3 vW;
    void main(){
      vec3 box = vec3(70.0, 26.0, 70.0); vec3 p0 = aSeed.xyz * box;
      p0.y -= uTime * (0.6 + aSeed.w*0.8);
      p0.xz += WIND*uTime*(1.6+aSeed.w) + vec2(sin(uTime*0.7+aSeed.x*30.0), cos(uTime*0.6+aSeed.z*30.0))*0.8;
      vec3 c = cameraPosition; vec3 w = mod(p0 - c + 0.5*box, box) - 0.5*box + c;
      float a = uTime*(1.5+aSeed.w*3.0) + aSeed.x*50.0, b = uTime*(1.1+aSeed.y*2.0) + aSeed.z*40.0;
      vec3 ax1 = vec3(cos(a), sin(a)*cos(b), sin(a)*sin(b)); vec3 ax2 = normalize(cross(ax1, vec3(sin(b), cos(b), 0.3)));
      float vis = step(terrainH(w.xz) + 0.05, w.y) * (1.0 - smoothstep(25.0, 34.0, length(w - c)));
      w += (ax1*position.x + ax2*position.y*1.3) * 0.06 * vis;
      vP = position.xy; vW = w; gl_Position = projectionMatrix*viewMatrix*vec4(w,1.0);
    }`,
    fragmentShader: COMMON + `varying vec2 vP; varying vec3 vW; void main(){ if(length(vP) > 1.0) discard;
      vec3 V = normalize(vW - cameraPosition); vec3 c = vec3(1.0,0.62,0.72) * (0.55 + 1.6*pow(max(dot(V,uSunDir),0.0),2.0));
      gl_FragColor = vec4(tonemap(applyFog(c, vW)),1.0); }`,
  }));
  m.frustumCulled = false; scene.add(m);
}

// ---------- the wanderer ----------
const hero = new THREE.Group(); scene.add(hero);
const body = new THREE.Group(); hero.add(body);
const tunic = toon(0x1f6b5c), skin = toon(0xf0c4a0), cream = toon(0xe8dcc0), brown = toon(0x3a2418);
add(body, new THREE.CapsuleGeometry(0.2, 0.34, 6, 14), tunic, 0, 1.05, 0);
add(body, new THREE.CylinderGeometry(0.19, 0.31, 0.32, 14), tunic, 0, 0.83, 0);
add(body, new THREE.CylinderGeometry(0.215, 0.215, 0.07, 14), brown, 0, 0.97, 0);
add(body, new THREE.SphereGeometry(0.21, 18, 14), skin, 0, 1.52, 0);
add(body, new THREE.SphereGeometry(0.225, 18, 14, 0, Math.PI * 2, 0, Math.PI * 0.55), toon(0x241a1a), 0, 1.54, -0.03);
add(body, new THREE.ConeGeometry(0.47, 0.21, 24), toon(0xd9b060), 0, 1.76, 0);
add(body, new THREE.BoxGeometry(0.05, 0.8, 0.05), brown, 0, 1.1, -0.23).rotation.z = 0.6;
const limb = (x, y, len, r, mat, tipMat) => { const p = new THREE.Group(); p.position.set(x, y, 0); body.add(p);
  add(p, new THREE.CapsuleGeometry(r, len, 4, 10), mat, 0, -len / 2 - r * 0.5, 0);
  if (tipMat) add(p, new THREE.CapsuleGeometry(r * 1.15, 0.1, 4, 10), tipMat, 0, -len - r, 0.03); return p; };
const legL = limb(-0.12, 0.78, 0.55, 0.085, cream, brown), legR = limb(0.12, 0.78, 0.55, 0.085, cream, brown);
const armL = limb(-0.28, 1.27, 0.4, 0.065, tunic, skin), armR = limb(0.28, 1.27, 0.4, 0.065, tunic, skin);
// scarf (verlet ribbon)
const K = 9, nodes = [], prev = [];
for (let i = 0; i < K; i++) { nodes.push(new THREE.Vector3()); prev.push(new THREE.Vector3()); }
const scarfGeo = new THREE.BufferGeometry(); scarfGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(K * 6), 3));
{ const idx = []; for (let i = 0; i < K - 1; i++) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); } scarfGeo.setIndex(idx); }
scarfGeo.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(K * 6).fill(0).map((_, i) => (i % 3 === 1 ? 1 : 0)), 3));
const scarf = new THREE.Mesh(scarfGeo, toon(0xe0352b, 0.35)); scarf.frustumCulled = false; scene.add(scarf);

// ---------- input / update ----------
const keys = {}; let started = false;
const begin = () => { if (!started) { started = true; document.getElementById('title').style.opacity = 0; } };
addEventListener('keydown', (e) => { keys[e.code] = true; begin(); if (e.code === 'Space') e.preventDefault(); });
addEventListener('keyup', (e) => { keys[e.code] = false; });
const P = { pos: new THREE.Vector3(0, terrainH(0, 0), 0), vel: new THREE.Vector3(), yaw: Math.atan2(az.x, az.y), vy: 0, grounded: true, phase: 0 };
const cam = { yaw: Math.atan2(-az.x, -az.y), pitch: 0.1, dist: 6.5, target: P.pos.clone().add(new THREE.Vector3(0, 1.3, 0)) };
let drag = false, lx = 0, ly = 0;
canvas.addEventListener('pointerdown', (e) => { drag = true; lx = e.clientX; ly = e.clientY; canvas.setPointerCapture(e.pointerId); begin(); });
canvas.addEventListener('pointerup', () => { drag = false; });
canvas.addEventListener('pointermove', (e) => { if (!drag) return; cam.yaw -= (e.clientX - lx) * 0.005; cam.pitch = Math.max(-0.12, Math.min(1.2, cam.pitch + (e.clientY - ly) * 0.004)); lx = e.clientX; ly = e.clientY; });
canvas.addEventListener('wheel', (e) => { cam.dist = Math.max(3, Math.min(14, cam.dist + e.deltaY * 0.01)); e.preventDefault(); }, { passive: false });
function resize() { const w = innerWidth, h = innerHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
addEventListener('resize', resize); resize();

const tmp = new THREE.Vector3(), tmp2 = new THREE.Vector3(), glow = document.getElementById('glow'); let last = performance.now(), fps = 60;
function frame(now) {
  const dt = Math.min((now - last) / 1000, 0.05); last = now; fps += (1 / Math.max(dt, 1e-3) - fps) * 0.05;
  const t = G.uTime.value += dt;
  const ix = (keys.KeyD || keys.ArrowRight ? 1 : 0) - (keys.KeyA || keys.ArrowLeft ? 1 : 0), iz = (keys.KeyW || keys.ArrowUp ? 1 : 0) - (keys.KeyS || keys.ArrowDown ? 1 : 0);
  const fx = -Math.sin(cam.yaw), fz = -Math.cos(cam.yaw), rx = Math.cos(cam.yaw), rz = -Math.sin(cam.yaw);
  let wx = fx * iz + rx * ix, wz = fz * iz + rz * ix; const l = Math.hypot(wx, wz); if (l > 0) { wx /= l; wz /= l; }
  const maxS = l > 0 ? (keys.ShiftLeft || keys.ShiftRight ? 9.5 : 5.0) : 0, k = 1 - Math.exp(-dt * 8);
  P.vel.x += (wx * maxS - P.vel.x) * k; P.vel.z += (wz * maxS - P.vel.z) * k;
  P.pos.x += P.vel.x * dt; P.pos.z += P.vel.z * dt;
  for (const c of colliders) { const dx = P.pos.x - c.x, dz = P.pos.z - c.z, d = Math.hypot(dx, dz), m = c.r + 0.3; if (d < m && d > 1e-4) { P.pos.x = c.x + dx / d * m; P.pos.z = c.z + dz / d * m; } }
  const rr = Math.hypot(P.pos.x, P.pos.z); if (rr > 230) { P.pos.x *= 230 / rr; P.pos.z *= 230 / rr; }
  const speed = Math.hypot(P.vel.x, P.vel.z), gy = terrainH(P.pos.x, P.pos.z);
  if (P.grounded) { P.pos.y = gy; if (keys.Space) { P.vy = 6.5; P.grounded = false; } }
  else { P.vy -= 20 * dt; P.pos.y += P.vy * dt; if (P.pos.y <= gy) { P.pos.y = gy; P.grounded = true; P.vy = 0; } }
  if (speed > 0.3) { let d = Math.atan2(P.vel.x, P.vel.z) - P.yaw; d = Math.atan2(Math.sin(d), Math.cos(d)); P.yaw += d * (1 - Math.exp(-dt * 12)); }
  P.phase += speed * dt * 2.4; const sf = Math.min(speed / 9.5, 1), sw = Math.sin(P.phase) * (0.35 + 0.75 * sf) * Math.min(speed, 1);
  legL.rotation.x = sw; legR.rotation.x = -sw; armL.rotation.x = -sw * 0.8; armR.rotation.x = sw * 0.8;
  if (!P.grounded) { legL.rotation.x = 0.5; legR.rotation.x = -0.3; armL.rotation.x = armR.rotation.x = -1.2; }
  body.rotation.x = sf * 0.22; body.position.y = Math.abs(Math.sin(P.phase)) * 0.06 * sf + Math.sin(t * 2) * 0.008;
  hero.position.copy(P.pos); hero.rotation.y = P.yaw; G.uPlayer.value.copy(P.pos);
  // scarf
  nodes[0].set(P.pos.x - Math.sin(P.yaw) * 0.17, P.pos.y + 1.34 + body.position.y, P.pos.z - Math.cos(P.yaw) * 0.17);
  for (let i = 1; i < K; i++) {
    const p = nodes[i], q = prev[i]; tmp.copy(p).sub(q).multiplyScalar(0.9); q.copy(p);
    p.add(tmp); p.x += 0.93 * 16 * dt * dt; p.z += 0.36 * 16 * dt * dt; p.y += (-4 + Math.sin(t * 9 + i * 1.2) * 9) * dt * dt;
    tmp.copy(p).sub(nodes[i - 1]); const d = tmp.length() || 1; p.copy(nodes[i - 1]).addScaledVector(tmp, 0.13 / d);
    p.y = Math.max(p.y, terrainH(p.x, p.z) + 0.05);
  }
  const sp = scarfGeo.attributes.position;
  for (let i = 0; i < K; i++) {
    tmp.copy(nodes[Math.min(i + 1, K - 1)]).sub(nodes[Math.max(i - 1, 0)]); const wxx = -tmp.z, wzz = tmp.x, wl = Math.hypot(wxx, wzz) || 1, ww = 0.075 * (1 - 0.3 * i / K) / wl;
    sp.setXYZ(i * 2, nodes[i].x + wxx * ww, nodes[i].y, nodes[i].z + wzz * ww); sp.setXYZ(i * 2 + 1, nodes[i].x - wxx * ww, nodes[i].y, nodes[i].z - wzz * ww);
  }
  sp.needsUpdate = true;
  // camera
  if (!started) cam.yaw += Math.sin(t * 0.2) * 0.0006;
  tmp.set(P.pos.x, P.pos.y + 1.3, P.pos.z); cam.target.lerp(tmp, 1 - Math.exp(-dt * 10));
  const cp = Math.cos(cam.pitch);
  camera.position.set(cam.target.x + Math.sin(cam.yaw) * cp * cam.dist, cam.target.y + Math.sin(cam.pitch) * cam.dist, cam.target.z + Math.cos(cam.yaw) * cp * cam.dist);
  camera.position.y = Math.max(camera.position.y, terrainH(camera.position.x, camera.position.z) + 0.4);
  camera.lookAt(cam.target.x, cam.target.y + 1.0, cam.target.z);
  G.uCamRight.value.set(Math.cos(cam.yaw), -Math.sin(cam.yaw));
  // sun glow overlay follows the sun on screen
  const facing = camera.getWorldDirection(tmp2).dot(sunDir);
  tmp.copy(sunDir).multiplyScalar(1000).add(camera.position).project(camera);
  glow.style.opacity = Math.max(0, Math.min(1, (facing - 0.35) * 2.2));
  glow.style.transform = `translate(${(tmp.x * 0.5 + 0.5) * innerWidth}px, ${(-tmp.y * 0.5 + 0.5) * innerHeight}px)`;
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
window.__demo = { P, cam, keys, get fps() { return fps; } };
