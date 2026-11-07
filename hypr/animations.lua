-- Curves (performance-first: no overshoot springs, all sub-2x speeds)
hl.curve("md3_standard", { type = "bezier", points = { { 0.2, 0 }, { 0, 1 } } })
hl.curve("md3_decel", { type = "bezier", points = { { 0.05, 0.7 }, { 0.1, 1 } } })
hl.curve("md3_accel", { type = "bezier", points = { { 0.3, 0 }, { 0.8, 1 } } })
hl.curve("snappy", { type = "bezier", points = { { 0.15, 0.85 }, { 0.1, 1 } } }) -- replaces spring/bouncy, no overshoot
hl.curve("swift_out", { type = "bezier", points = { { 0.0, 0.0 }, { 0.2, 1 } } })
hl.curve("swift_in", { type = "bezier", points = { { 0.4, 0.0 }, { 1.0, 1 } } })
hl.curve("overshoot", { type = "bezier", points = { { 0.34, 1.3 }, { 0.65, 1.0 } } }) -- single overshoot for workspaces only

-- Global animation toggle — flip enabled to false for a hard perf mode
hl.animation({ leaf = "global", enabled = true, speed = 1, bezier = "md3_standard" })

-- Windows: fast pop-in, slight scale, no fade (fade costs a compositing pass)
hl.animation({ leaf = "windows", enabled = true, speed = 1.6, bezier = "snappy", style = "popin 92%" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 1.4, bezier = "swift_out", style = "popin 94%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 1.6, bezier = "swift_in", style = "popin 96%" })
hl.animation({ leaf = "windowsMove", enabled = true, speed = 1.8, bezier = "md3_standard", style = "slide" })

-- Borders + fade: cheap, keep them
hl.animation({ leaf = "border", enabled = true, speed = 2.5, bezier = "md3_standard" })
hl.animation({ leaf = "borderangle", enabled = true, speed = 2.5, bezier = "md3_standard" })
hl.animation({ leaf = "fade", enabled = true, speed = 2.5, bezier = "md3_decel" })
hl.animation({ leaf = "fadeDim", enabled = true, speed = 2.5, bezier = "md3_decel" })

-- Workspaces: the money shot — vertical slide with a touch of overshoot
hl.animation({ leaf = "workspaces", enabled = true, speed = 3.2, bezier = "overshoot", style = "slidevert" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 3.2, bezier = "overshoot", style = "slidevert" })

-- Layers (waybar, rofi, swaync): quick fades, no slide
hl.animation({ leaf = "layers", enabled = true, speed = 1.8, bezier = "md3_decel", style = "fade" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 1.6, bezier = "md3_decel", style = "fade" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 1.8, bezier = "swift_in", style = "fade" })
hl.animation({ leaf = "fadeLayersIn", enabled = true, speed = 1.8, bezier = "md3_decel" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 1.8, bezier = "swift_in" })
