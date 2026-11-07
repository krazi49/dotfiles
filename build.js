#!/usr/bin/env node
/**
 * oganesson — dotfiles design token builder
 *
 * Reads:
 *   - appearance.json           (fonts, radius, borders, spacing…)
 *   - waybar/theme.css          (matugen-generated colors)
 *
 * Writes every config in the dotfiles repo that needs appearance settings.
 * Run AFTER matugen.
 *
 * Usage: node build.js
 */

const fs = require('fs');
const path = require('path');

const DOTFILES = __dirname;
const DIST = path.join(DOTFILES, '.brand', 'dist');
fs.mkdirSync(DIST, { recursive: true });

// ── Load inputs ─────────────────────────────────────────────
const A = JSON.parse(fs.readFileSync(path.join(DOTFILES, 'appearance.json'), 'utf8'));

function parseDefineColorCSS(filepath) {
  if (!fs.existsSync(filepath)) return null;
  const src = fs.readFileSync(filepath, 'utf8');
  const colors = {};
  const re = /@define-color\s+(\S+)\s+(#[0-9a-fA-F]+);/g;
  let m;
  while ((m = re.exec(src)) !== null) colors[m[1]] = m[2].toLowerCase();
  return colors;
}

const dark = parseDefineColorCSS(path.join(DOTFILES, 'waybar', 'theme.css'));
if (!dark) { console.error('run matugen first — waybar/theme.css not found'); process.exit(1); }

const light = parseDefineColorCSS(path.join(DOTFILES, 'waybar', 'theme-light.css'));

// ── helpers ─────────────────────────────────────────────────
const stripHex = h => h.replace('#', '');
const say = msg => console.log(`  \u2713 ${msg}`);

// ── 1. Waybar: nothing needed on theme.css (matugen handles colors),
// but clean up any stale * { } block from old build.js versions
(function waybarClean() {
  const p = path.join(DOTFILES, 'waybar', 'theme.css');
  let css = fs.readFileSync(p, 'utf8');
  if (css.includes('/* ── appearance managed by build.js ── */')) {
    css = css.replace(/\n\/\* ── appearance managed by build\.js ── \*\/.*?(?=\n\/\*|\n$)/s, '');
    fs.writeFileSync(p, css);
    say('waybar/theme.css (cleaned stale block)');
  }
})();

// ── 2. Waybar style.css: managed appearance block ────────────
(function waybarStyle() {
  const p = path.join(DOTFILES, 'waybar', 'style.css');
  let css = fs.readFileSync(p, 'utf8');

  // Build the managed appearance block — only valid GTK CSS properties,
  // no custom --og-* vars since GTK's CSS parser rejects them.
  const block = `/* OGANESSON_APPEARANCE_START */
    font-family: "${A.typography.sans.family}";
/* OGANESSON_APPEARANCE_END */`;

  if (css.includes('OGANESSON_APPEARANCE_START')) {
    css = css.replace(/\/\* OGANESSON_APPEARANCE_START \*\/[\s\S]*?\/\* OGANESSON_APPEARANCE_END \*\//, block);
  } else {
    // Insert into the first * { } block, right after the opening brace
    const idx = css.indexOf('{');
    css = css.slice(0, idx + 1) + '\n' + block + css.slice(idx + 1);
  }

  // Remove duplicate font-family line that was in the original * block
  // (now redundant since the managed block provides it)
  if (css.includes('OGANESSON_APPEARANCE')) {
    css = css.replace(/\n    font-family: "[^"]+";\n\}/, '\n}');
  }

  // Replace hardcoded values in the rest of the file
  const hardcodedReplacements = [
    [/("|')Zalando Sans("|')/g, `"${A.typography.sans.family}"`],
    [/("|')Monaspace Argon Var("|')/g, `"${A.typography.display.family}"`],
    [/("|')Monaspace Krypton("|')/g, `"${A.typography.alt.family}"`],
    [/("|')JetBrains Mono NerdFont Propo("|')/g, `"${A.typography.nerd.family}"`],
    [/border-radius:\s*\d+/g, `border-radius: ${A.shape.corner_radius}`],
  ];
  for (const [re, replacement] of hardcodedReplacements) {
    css = css.replace(re, replacement);
  }

  fs.writeFileSync(p, css);
  say('waybar/style.css');
})();

// ── 3. Rofi: replace hardcoded values ──────────────────────
(function rofi() {
  const targets = ['config.rasi', 'config-horiz.rasi'];
  const sansVal = `"${A.typography.sans.family} ${A.typography.sans.size_ui}"`;
  const boldVal = `"${A.typography.sans.family} Bold ${A.typography.sans.size_ui}"`;
  const searchVal = A.typography.search ? `"${A.typography.search.family} ${A.typography.search.size}"` : sansVal;

  for (const name of targets) {
    const p = path.join(DOTFILES, 'rofi', name);
    if (!fs.existsSync(p)) continue;
    let rasi = fs.readFileSync(p, 'utf8');

    // entry (search bar) gets the search font, everything else uses sans
    rasi = rasi.replace(/font:\s*"[^"]+"/g, (match, offset, full) => {
      // Check if this font line is inside an `entry` block
      const before = full.slice(0, offset);
      const lastBrace = before.lastIndexOf('{');
      const lastBraceBefore = before.lastIndexOf('}');
      // If the last unclosed block is 'entry', use the search font
      if (lastBrace > lastBraceBefore) {
        const blockName = before.slice(before.lastIndexOf('\n', lastBrace - 1), lastBrace).trim();
        if (blockName === 'entry' || blockName.endsWith('entry')) {
          return `font:                   ${searchVal}`;
        }
      }
      if (match.includes('Bold')) return `font:                   ${boldVal}`;
      return `font:                   ${sansVal}`;
    });
    rasi = rasi.replace(/border:\s*\d+px/g, `border:                 ${A.border.width_thin}px`);
    rasi = rasi.replace(/border-radius:\s*-?\d+/g, `border-radius:          ${A.shape.corner_radius}`);

    fs.writeFileSync(p, rasi);
    say(`rofi/${name}`);
  }
})();

// ── 4. Kitty: font and window padding ──────────────────────
(function kitty() {
  const p = path.join(DOTFILES, 'kitty', 'kitty.conf');
  let conf = fs.readFileSync(p, 'utf8');

  conf = conf.replace(/font_size\s+\d+/, `font_size                   ${A.typography.mono.size_base}`);
  // kitty uses Monaspace Krypton for code, JetBrains Nerd Font for icons
  conf = conf.replace(/# BEGIN_KITTY_FONTS[\s\S]*?# END_KITTY_FONTS/m,
    `# BEGIN_KITTY_FONTS
font_family      family="${A.typography.mono.family}"
bold_font        auto
italic_font      auto
bold_italic_font auto
# END_KITTY_FONTS`);
  conf = conf.replace(/window_padding_width\s+[\d.]+\s+[\d.]+/, `window_padding_width        ${A.window.padding} ${A.window.padding}`);

  fs.writeFileSync(p, conf);
  say('kitty/kitty.conf');
})();

// ── 5. Hyprland: border, rounding, font ────────────────────
(function hyprland() {
  const p = path.join(DOTFILES, 'hypr', 'hyprland.lua');
  let lua = fs.readFileSync(p, 'utf8');

  lua = lua.replace(/rounding\s*=\s*\d+,*/, `rounding = ${A.shape.corner_radius},`);
  lua = lua.replace(/border_size\s*=\s*\d+,*/, `border_size = ${A.border.width_thin},`);
  lua = lua.replace(/font_family\s*=\s*"[^"]+"/, `font_family = "${A.typography.sans.family}"`);

  fs.writeFileSync(p, lua);
  say('hypr/hyprland.lua');
})();

// ── 6. GTK: colors.css (overwrite appearance vars) ───────────
(function gtkColors() {
  const gtkFiles = [path.join(DOTFILES, 'gtk-3.0', 'colors.css'), path.join(DOTFILES, 'gtk-4.0', 'gtk.css')];
  for (const p of gtkFiles) {
    if (!fs.existsSync(p)) continue;
    let css = fs.readFileSync(p, 'utf8');
    const replacements = [
      [/@define-color font_sans\s+"[^"]+";/, `@define-color font_sans                "${A.typography.sans.family}";`],
      [/@define-color font_mono\s+"[^"]+";/, `@define-color font_mono                "${A.typography.mono.family}";`],
      [/@define-color font_size_ui\s+[^;]+;/, `@define-color font_size_ui             ${A.typography.sans.size_ui};`],
      [/@define-color font_size_body\s+[^;]+;/, `@define-color font_size_body           ${A.typography.sans.size_body};`],
      [/@define-color corner_radius\s+[^;]+;/, `@define-color corner_radius            ${A.shape.corner_radius};`],
      [/@define-color border_width_thin\s+[^;]+;/, `@define-color border_width_thin        ${A.border.width_thin};`],
    ];
    for (const [re, replacement] of replacements) {
      css = css.replace(re, replacement);
    }
    fs.writeFileSync(p, css);
  }
  say('gtk-3.0/colors.css + gtk-4.0/gtk.css');

  // Also write settings.ini
  const content = `[Settings]
gtk-theme-name=adw-gtk3-dark
gtk-font-name=${A.typography.sans.family} ${A.typography.sans.size_ui}
`;
  fs.writeFileSync(path.join(DOTFILES, 'gtk-3.0', 'settings.ini'), content);
  fs.writeFileSync(path.join(DOTFILES, 'gtk-4.0', 'settings.ini'), content);
  say('gtk-3.0/settings.ini');
  say('gtk-4.0/settings.ini');
})();

// ── 7. Swaync: config.json + style.css ──────────────────────
(function swaync() {
  // config.json
  const cfgPath = path.join(DOTFILES, 'swaync', 'config.json');
  const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
  cfg.timeout = A.notification.timeout;
  cfg['timeout-low'] = A.notification.timeout_low;
  cfg['timeout-critical'] = A.notification.timeout_critical;
  cfg['notification-window-width'] = A.notification.width;
  cfg['notification-icon-size'] = A.notification.icon_size;
  fs.writeFileSync(cfgPath, JSON.stringify(cfg, null, 4) + '\n');
  say('swaync/config.json');

  // style.css
  const stylePath = path.join(DOTFILES, 'swaync', 'style.css');
  let css = fs.readFileSync(stylePath, 'utf8');
  // Replace the entire font-family line to avoid doubling
  css = css.replace(/font-family:\s*"[^"]+"(?:,\s*"[^"]+")*/g, `font-family: "${A.typography.sans.family}", "${A.typography.mono.family}"`);
  css = css.replace(/font-size:\s*\d+px/g, `font-size: ${A.typography.sans.size_body}px`);
  css = css.replace(/border-radius:\s*-?\d+\.?\d*px?/g, `border-radius: ${A.shape.corner_radius}px`);
  css = css.replace(/-gtk-outline-radius:\s*\d+(\.\d+)?/g, `-gtk-outline-radius: ${A.shape.corner_radius}`);
  fs.writeFileSync(stylePath, css);
  say('swaync/style.css');
})();

// ── 8. Swayosd: style.css ───────────────────────────────────
(function swayosd() {
  const p = path.join(DOTFILES, 'swayosd', 'style.css');
  let css = fs.readFileSync(p, 'utf8');
  css = css.replace(/border:\s*\d+px/g, `border: ${A.border.width_thin}px`);
  css = css.replace(/border-radius:\s*-?\d+/g, `border-radius: ${A.shape.corner_radius}`);
  css = css.replace(/font-size:\s*\d+px/g, `font-size: ${A.typography.sans.size_sm}px`);
  fs.writeFileSync(p, css);
  say('swayosd/style.css');
})();

// ── 9. Snapshot: tokens.json + preview.html ─────────────────

// ── 8. Website: web-vars.css already handled by matugen ────
// But we also need to make the site's style.css use appearance vars
// — that's done via the oganesson.css token aliases, which map to color-* vars
// The font vars on the site are set in web-vars.css by matugen already.

// ── 9. Snapshot: tokens.json + preview.html ─────────────────
(function snapshot() {
  const tokens = {
    name: 'oganesson',
    version: A.version,
    source_color: dark.source_color || 'unknown',
    generated: new Date().toISOString(),
    color: dark,
    light: light ? { color: light } : undefined,
    typography: A.typography,
    shape: A.shape,
    border: A.border,
    spacing: A.spacing,
    motion: A.motion,
    window: A.window,
    notification: A.notification,
  };
  fs.writeFileSync(path.join(DIST, 'tokens.json'), JSON.stringify(tokens, null, 2));
  say('.brand/dist/tokens.json');

  // preview.html
  const swatches = Object.entries(dark)
    .filter(([k]) => !['source_color', 'scrim', 'shadow'].includes(k) && !k.startsWith('inverse_') && !k.startsWith('on_'))
    .slice(0, 30);

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>oganesson — preview</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:${dark.surface};color:${dark.on_surface};font-family:${A.typography.sans.family},system-ui,sans-serif;padding:2rem}
h1{font-size:1.5rem;margin-bottom:.25rem;font-weight:700}
.seed{font-size:.875rem;color:${dark.on_surface_variant};margin-bottom:1rem}
.meta{font-size:.75rem;color:${dark.outline};margin-bottom:2rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem}
.swatch{border-radius:${A.shape.corner_radius}px;overflow:hidden;border:${A.border.width_thin}px solid ${dark.outline}}
.swatch-bar{height:80px;display:flex;align-items:flex-end;padding:8px}
.swatch-bar span{font-size:.75rem;font-weight:600;background:rgba(0,0,0,.5);padding:2px 6px;border-radius:2px;color:white}
.swatch-label{padding:6px 8px;font-size:.75rem;background:${dark.surface_container}}
.swatch-label .name{font-weight:600}
.swatch-label .hex{color:${dark.on_surface_variant}}
.group{border:${A.border.width_hairline}px solid ${dark.outline_variant};padding:1.5rem;margin-top:1.5rem}
.group h2{font-size:1rem;margin-bottom:.75rem;font-weight:600;color:${dark.primary}}
.font-demo{display:flex;flex-direction:column;gap:.25rem}
.font-demo .sans{font-family:"${A.typography.sans.family}";font-size:16px}
.font-demo .mono{font-family:"${A.typography.mono.family}";font-size:14px}
.font-demo .display{font-family:"${A.typography.display.family}";font-size:24px;font-weight:700}
.font-demo .alt{font-family:"${A.typography.alt.family}";font-size:14px}
.info-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:.5rem;font-size:.8125rem}
.info-grid .label{color:${dark.on_surface_variant}}
</style>
</head>
<body>
<h1>oganesson</h1>
<p class="seed">seed: ${dark.source_color} \u00b7 ${Object.keys(dark).length} color tokens</p>
<p class="meta">${A.typography.sans.family} \u00b7 ${A.typography.mono.family} \u00b7 r${A.shape.corner_radius} \u00b7 border ${A.border.width_thick}px</p>
<div class="group"><h2>colors</h2>
<div class="grid">
${swatches.map(s => {
  const tc = dark[`on_${s[0]}`] || dark.on_surface;
  return `<div class="swatch"><div class="swatch-bar" style="background:${s[1]};color:${tc}"><span>${s[1]}</span></div><div class="swatch-label"><div class="name">${s[0]}</div><div class="hex">on: ${tc}</div></div></div>`;
}).join('\n')}
</div></div>
<div class="group"><h2>fonts</h2>
<div class="font-demo">
<div class="display">display — ${A.typography.display.family}</div>
<div class="sans">sans — ${A.typography.sans.family} (${A.typography.sans.size_ui}px ui / ${A.typography.sans.size_body}px body)</div>
<div class="alt">alt — ${A.typography.alt.family}</div>
<div class="mono">mono — ${A.typography.mono.family} (${A.typography.mono.size_base}px base)</div>
</div></div>
<div class="group"><h2>appearance</h2>
<div class="info-grid">
<div><span class="label">corner radius</span><br>${A.shape.corner_radius}px</div>
<div><span class="label">border thick</span><br>${A.border.width_thick}px</div>
<div><span class="label">border thin</span><br>${A.border.width_thin}px</div>
<div><span class="label">window padding</span><br>${A.window.padding}px</div>
<div><span class="label">notif timeout</span><br>${A.notification.timeout}s</div>
<div><span class="label">notif width</span><br>${A.notification.width}px</div>
<div><span class="label">duration fast</span><br>${A.motion.duration_fast}ms</div>
</div></div>
</body></html>`;

  fs.writeFileSync(path.join(DIST, 'preview.html'), html);
  say('.brand/dist/preview.html');
})();

console.log(`\n✨ build complete — ${A.typography.sans.family} / ${A.typography.mono.family} / r${A.shape.corner_radius}`);
