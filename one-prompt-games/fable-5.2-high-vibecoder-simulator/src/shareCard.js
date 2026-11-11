// End-of-run share card: a receipt drawn on a 2D canvas, savable as PNG.
export function drawCard(s) {
  const cv = document.createElement('canvas');
  cv.width = 720; cv.height = 1040;
  const c = cv.getContext('2d');
  const g = c.createLinearGradient(0, 0, 720, 1040);
  g.addColorStop(0, '#1b1036'); g.addColorStop(1, '#3a0f3f');
  c.fillStyle = g; c.fillRect(0, 0, 720, 1040);

  // receipt paper
  c.save();
  c.translate(360, 520); c.rotate(-0.025); c.translate(-360, -520);
  c.fillStyle = '#f6f1e4';
  c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 40;
  c.fillRect(70, 50, 580, 940);
  c.shadowBlur = 0;
  c.fillStyle = '#1b1036';
  for (let x = 70; x < 650; x += 20) { c.beginPath(); c.arc(x + 10, 990, 9, 0, Math.PI * 2); c.fill(); }

  c.fillStyle = '#16121f'; c.textAlign = 'center';
  c.font = 'bold 40px Menlo, monospace';
  c.fillText('VIBE CODER SIMULATOR', 360, 115);
  c.font = '18px Menlo, monospace';
  c.fillText('2:00 AM  *  PARABLE HALL MONITOR  *  RECEIPT', 360, 148);

  c.font = 'bold 56px Menlo, monospace';
  c.fillStyle = s.won ? '#0a8a4a' : '#d1122b';
  c.fillText(s.won ? 'SHIPPED!' : 'YOU ARE BANNED', 360, 222);

  c.fillStyle = '#16121f'; c.font = '24px Menlo, monospace';
  const mm = Math.floor(s.time / 60), ss = String(Math.floor(s.time % 60)).padStart(2, '0');
  const rows = [
    ['TIME SURVIVED', `${mm}:${ss}`],
    ['SHIP %', `${Math.floor(s.ship)}%`],
    ['APPEALS WON', s.appeals],
    ['BEST COMBO', `x${s.bestCombo}`],
    ['AGENTS BANNED', s.bans],
    ['BEERS', s.beers],
    ['VAPE CLOUDS', s.vapes],
    ['MONITORS DESTROYED', s.smashed],
    ['PENGUIN SQUEEZES', s.squeezes],
  ];
  let y = 290;
  for (const [k, v] of rows) {
    c.textAlign = 'left'; c.fillText(k, 110, y);
    c.textAlign = 'right'; c.fillText(String(v), 610, y);
    c.fillStyle = 'rgba(0,0,0,.25)'; c.fillRect(110, y + 10, 500, 1); c.fillStyle = '#16121f';
    y += 44;
  }
  y += 12;
  c.font = 'bold 30px Menlo, monospace';
  c.textAlign = 'left'; c.fillText('DAMAGE INVOICE', 110, y);
  c.textAlign = 'right'; c.fillText('$' + s.invoice.toLocaleString('en-US') + ' USD', 610, y);

  y += 56; c.textAlign = 'center'; c.font = '18px Menlo, monospace';
  c.fillText('FUNNIEST BAN REASON', 360, y);
  c.font = 'italic 22px Georgia, serif';
  y = wrap(c, '"' + (s.reason || 'none. suspiciously well-behaved.') + '"', 360, y + 32, 480, 28);

  y += 26; c.font = '18px Menlo, monospace';
  c.fillText("THE PENGUIN'S VERDICT", 360, y);
  c.font = 'bold 24px Menlo, monospace';
  y = wrap(c, s.verdict, 360, y + 34, 480, 30);

  // tiny penguin
  const px = 360, py = Math.min(y + 60, 930);
  c.fillStyle = '#20222e'; c.beginPath(); c.ellipse(px, py, 34, 40, 0, 0, Math.PI * 2); c.fill();
  c.fillStyle = '#fff'; c.beginPath(); c.ellipse(px, py + 8, 22, 28, 0, 0, Math.PI * 2); c.fill();
  c.fillStyle = '#111'; c.beginPath(); c.arc(px - 11, py - 14, 4, 0, 7); c.arc(px + 11, py - 14, 4, 0, 7); c.fill();
  c.fillStyle = '#ff9a2e'; c.beginPath(); c.moveTo(px - 6, py - 7); c.lineTo(px + 6, py - 7); c.lineTo(px, py + 2); c.fill();
  c.fillStyle = '#e0283c'; c.fillRect(px - 26, py + 2, 52, 8);
  c.restore();
  return cv;
}

function wrap(c, text, x, y, maxW, lh) {
  const words = String(text).split(' ');
  let line = '';
  for (const w of words) {
    if (c.measureText(line + w).width > maxW && line) { c.fillText(line.trim(), x, y); y += lh; line = ''; }
    line += w + ' ';
  }
  c.fillText(line.trim(), x, y);
  return y + lh;
}

export function savePNG(cv) {
  cv.toBlob((b) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(b);
    a.download = 'vibe-coder-receipt.png';
    document.body.appendChild(a); a.click(); a.remove();
  }, 'image/png');
}
