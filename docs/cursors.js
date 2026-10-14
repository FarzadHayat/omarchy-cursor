// Renders Omarchy Cursor pixel art in the browser from theme colors.
// Mirrors Palette in build.py so previews match the installed cursors.

const FALLBACK_COLORS = {
  mode: "dark",
  accent: "#7aa2f7",
  background: "#1a1b26",
  foreground: "#c0caf5",
  red: "#f7768e",
};

// Python's round() rounds halves to even; match it so colors are identical.
function roundHalfEven(x) {
  const r = Math.round(x);
  return Math.abs(x % 1) === 0.5 && r % 2 !== 0 ? r - 1 : r;
}

function rgb(hex) {
  const h = hex.trim().replace(/^#+/, "").slice(0, 6);
  return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16) / 255);
}

function toHex(c) {
  return "#" + c.map(v => roundHalfEven(Math.max(0, Math.min(1, v)) * 255).toString(16).padStart(2, "0")).join("");
}

function mix(a, b, t) {
  const ca = rgb(a), cb = rgb(b);
  return toHex(ca.map((x, i) => x + (cb[i] - x) * t));
}

function luminance(hex) {
  const lin = v => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
  const [r, g, b] = rgb(hex).map(lin);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrast(a, b) {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

// Python's colorsys, so saturate() gives the same result as build.py.
function rgbToHls(r, g, b) {
  const maxc = Math.max(r, g, b), minc = Math.min(r, g, b);
  const sumc = maxc + minc, rangec = maxc - minc, l = sumc / 2;
  if (minc === maxc) return [0, l, 0];
  const s = l <= 0.5 ? rangec / sumc : rangec / (2 - maxc - minc);
  const rc = (maxc - r) / rangec, gc = (maxc - g) / rangec, bc = (maxc - b) / rangec;
  let h = r === maxc ? bc - gc : g === maxc ? 2 + rc - bc : 4 + gc - rc;
  h = (((h / 6) % 1) + 1) % 1;
  return [h, l, s];
}

function hlsToRgb(h, l, s) {
  if (s === 0) return [l, l, l];
  const m2 = l <= 0.5 ? l * (1 + s) : l + s - l * s;
  const m1 = 2 * l - m2;
  const v = hue => {
    hue = ((hue % 1) + 1) % 1;
    if (hue < 1 / 6) return m1 + (m2 - m1) * hue * 6;
    if (hue < 0.5) return m2;
    if (hue < 2 / 3) return m1 + (m2 - m1) * (2 / 3 - hue) * 6;
    return m1;
  };
  return [v(h + 1 / 3), v(h), v(h - 1 / 3)];
}

function saturate(hex, amount) {
  const [h, l, s] = rgbToHls(...rgb(hex));
  return toHex(hlsToRgb(h, l, Math.min(1, s * amount)));
}

// Theme colors to the art's color keys, as [r, g, b, a].
function palette(theme, style = "accent") {
  const c = { ...FALLBACK_COLORS, ...theme };
  let dark = c.darker_background || c.dark_background || c.background;
  let light = c.bright_foreground || c.light_foreground || c.foreground;
  if (c.mode === "light") [dark, light] = [c.foreground || dark, c.background || light];
  if (luminance(dark) > 0.02) dark = mix(dark, "#000000", 0.25);

  // accent: accent body with whichever theme neutral gives the strongest edge.
  // light and dark: neutral body, with the accent kept for the animations.
  let body, rim;
  if (style === "light") [body, rim] = [mix(light, "#ffffff", 0.5), dark];
  else if (style === "dark") [body, rim] = [mix(dark, "#ffffff", 0.15), mix(light, "#ffffff", 0.5)];
  else {
    body = c.accent;
    rim = contrast(dark, body) >= contrast(light, body) ? dark : light;
  }
  const sand = style === "accent" ? body : c.accent;
  let danger = c.red || "#e05561";
  if (contrast(danger, rim) < 2.4) {
    danger = saturate(mix(danger, luminance(rim) < 0.3 ? "#ffffff" : "#000000", 0.35), 1.2);
  }
  const roles = {
    "#": body, s: sand, X: rim,
    w: mix(body, "#ffffff", 0.35), d: mix(body, "#000000", 0.22),
    t: mix(body, rim, 0.6), h: mix(sand, "#ffffff", luminance(sand) < 0.5 ? 0.45 : 0.7),
    r: danger, R: mix(danger, "#ffffff", 0.22), D: mix(danger, "#000000", 0.12),
  };
  const out = {};
  for (const [key, hex] of Object.entries(roles)) out[key] = [...rgb(hex).map(v => roundHalfEven(v * 255)), 255];
  out["%"] = [0, 0, 0, roundHalfEven(255 * (luminance(rim) < 0.2 ? 0.5 : 0.35) * 0.8)];
  return out;
}

// Reads the string values out of an Omarchy colors.toml.
function parseColors(text) {
  const colors = {};
  for (const line of text.split("\n")) {
    const m = line.match(/^\s*([A-Za-z0-9_]+)\s*=\s*"([^"]*)"/);
    if (m) colors[m[1]] = m[2];
  }
  if (!colors.accent || !/^#?[0-9a-f]{6}/i.test(colors.accent)) throw new Error("No accent color found");
  return colors;
}

// One frame (rows of color keys) as a PNG data URL, each art pixel scale x scale.
function renderFrame(rows, colors, scale) {
  const size = rows.length * scale;
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext("2d");
  const image = ctx.createImageData(size, size);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const color = colors[rows[Math.floor(y / scale)][Math.floor(x / scale)]];
      if (color) image.data.set(color, (y * size + x) * 4);
    }
  }
  ctx.putImageData(image, 0, 0);
  return canvas.toDataURL();
}

// Mirrors placement() in pixelart.py: the largest whole number scale that fits
// a size x size image, shifted so the hotspot sits at the same fraction at every
// size. Hotspots are points on the art grid, rounded half up like Hyprland.
function placement(hotspot, size, canvas = 18) {
  const scale = Math.max(1, Math.floor(size / canvas));
  const room = Math.max(0, size - canvas * scale);
  const [ox, oy] = hotspot.map(p => Math.min(room, Math.max(0, Math.floor(p / canvas * size + 0.5) - Math.floor(p * scale + 0.5))));
  return { scale, ox, oy };
}

// One frame drawn into a size x size PNG data URL, placed like the installed cursor.
function renderAt(rows, colors, size, hotspot) {
  const { scale, ox, oy } = placement(hotspot, size, rows.length);
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext("2d");
  const image = ctx.createImageData(size, size);
  rows.forEach((row, y) => [...row].forEach((key, x) => {
    const color = colors[key];
    if (!color) return;
    for (let py = 0; py < scale; py++) {
      for (let px = 0; px < scale; px++) {
        image.data.set(color, ((oy + y * scale + py) * size + ox + x * scale + px) * 4);
      }
    }
  }));
  ctx.putImageData(image, 0, 0);
  return canvas.toDataURL();
}

// Frames shifted so the drawing sits in the middle of its square, for icons.
// One offset for all frames, so animations don't jitter.
function centered(frames) {
  const size = frames[0].length;
  let x0 = size, x1 = 0, y0 = size, y1 = 0;
  for (const rows of frames) {
    rows.forEach((r, y) => [...r].forEach((c, x) => {
      if (c === ".") return;
      x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y);
    }));
  }
  const dx = Math.floor((size - (x1 - x0 + 1)) / 2) - x0;
  const dy = Math.floor((size - (y1 - y0 + 1)) / 2) - y0;
  return frames.map(rows => Array.from({ length: size }, (_, y) =>
    Array.from({ length: size }, (_, x) => (rows[y - dy] || "")[x - dx] || ".").join("")));
}

if (typeof module !== "undefined") module.exports = { palette, parseColors, placement };
