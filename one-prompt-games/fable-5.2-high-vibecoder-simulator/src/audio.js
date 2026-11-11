// Web Audio sound effects and ambience. No samples: everything is synthesized.
let ctx = null, master = null;

export function initAudio() {
  if (ctx) return;
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return;
  ctx = new AC();
  master = ctx.createGain();
  master.gain.value = 0.5;
  master.connect(ctx.destination);
  ambience();
}

function tone(f, d, type = 'sine', vol = 0.2, slideTo = null, delay = 0) {
  if (!ctx) return;
  const t = ctx.currentTime + delay;
  const o = ctx.createOscillator(), g = ctx.createGain();
  o.type = type;
  o.frequency.setValueAtTime(f, t);
  if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, t + d);
  g.gain.setValueAtTime(vol, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + d);
  o.connect(g); g.connect(master);
  o.start(t); o.stop(t + d + 0.02);
}

function noiseBuf(sec) {
  const b = ctx.createBuffer(1, Math.floor(ctx.sampleRate * sec), ctx.sampleRate);
  const d = b.getChannelData(0);
  for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
  return b;
}

function noise(d, vol = 0.3, freq = 2000, type = 'bandpass', delay = 0) {
  if (!ctx) return;
  const t = ctx.currentTime + delay;
  const s = ctx.createBufferSource(); s.buffer = noiseBuf(d);
  const f = ctx.createBiquadFilter(); f.type = type; f.frequency.value = freq;
  const g = ctx.createGain();
  g.gain.setValueAtTime(vol, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + d);
  s.connect(f); f.connect(g); g.connect(master);
  s.start(t);
}

function ambience() {
  // rain
  const s = ctx.createBufferSource(); s.buffer = noiseBuf(3); s.loop = true;
  const f = ctx.createBiquadFilter(); f.type = 'bandpass'; f.frequency.value = 1400; f.Q.value = 0.4;
  const g = ctx.createGain(); g.gain.value = 0.06;
  s.connect(f); f.connect(g); g.connect(master); s.start();
  // fridge hum
  const o = ctx.createOscillator(); o.type = 'sawtooth'; o.frequency.value = 55;
  const lf = ctx.createBiquadFilter(); lf.type = 'lowpass'; lf.frequency.value = 120;
  const og = ctx.createGain(); og.gain.value = 0.035;
  o.connect(lf); lf.connect(og); og.connect(master); o.start();
}

export const sfx = {
  appeal(combo = 1) {
    const base = 520 * Math.pow(1.06, Math.min(combo, 14));
    tone(base, 0.09, 'square', 0.12);
    tone(base * 1.5, 0.14, 'square', 0.1, null, 0.06);
  },
  flag() { tone(880, 0.12, 'sawtooth', 0.1); tone(660, 0.16, 'sawtooth', 0.1, null, 0.12); },
  ban() { tone(220, 0.5, 'sawtooth', 0.22, 60); noise(0.3, 0.2, 400, 'lowpass'); },
  decoy() { tone(300, 0.25, 'square', 0.14, 150); },
  squeak() { tone(900, 0.12, 'sine', 0.3, 1900); tone(1900, 0.2, 'sine', 0.25, 700, 0.12); },
  punch() { noise(0.09, 0.5, 300, 'lowpass'); tone(110, 0.1, 'sine', 0.3, 50); },
  shatter() {
    noise(0.5, 0.45, 5200, 'highpass');
    for (let i = 0; i < 6; i++) tone(2000 + Math.random() * 4000, 0.08, 'triangle', 0.07, null, Math.random() * 0.3);
  },
  can() { noise(0.12, 0.3, 6000, 'highpass'); tone(180, 0.1, 'triangle', 0.15, 90, 0.08); },
  puff() { noise(0.9, 0.12, 700, 'lowpass'); },
  clack() { noise(0.02, 0.05, 3000 + Math.random() * 1500, 'bandpass'); },
  focus() { tone(200, 0.8, 'sine', 0.2, 800); },
  win() { [523, 659, 784, 1047, 1319].forEach((f, i) => tone(f, 0.3, 'square', 0.12, null, i * 0.11)); },
  lose() { [400, 300, 220, 140].forEach((f, i) => tone(f, 0.4, 'sawtooth', 0.15, null, i * 0.2)); },
};
