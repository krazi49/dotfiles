-- Curves
hl.curve("md3_standard", { type = "bezier", points = { { 0.2, 0 }, { 0, 1 } } })
hl.curve("md3_decel", { type = "bezier", points = { { 0.05, 0.7 }, { 0.1, 1 } } })
hl.curve("md3_accel", { type = "bezier", points = { { 0.3, 0 }, { 0.8, 1 } } })
hl.curve("snappy", { type = "bezier", points = { { 0.15, 0.85 }, { 0.1, 1 } } }) -- replaces spring/bouncy, no overshoot
hl.curve("swift_out", { type = "bezier", points = { { 0.0, 0.0 }, { 0.2, 1 } } })
hl.curve("swift_in", { type = "bezier", points = { { 0.4, 0.0 }, { 1.0, 1 } } })
-- Animations
hl.animation({ leaf = "windowsIn", enabled = true, speed = 1.5, bezier = "swift_out", style = "popin 90%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 1.8, bezier = "swift_in", style = "popin 90%" })
hl.animation({ leaf = "windows", enabled = true, speed = 2, bezier = "snappy", style = "popin 85%" })
hl.animation({ leaf = "border", enabled = true, speed = 3, bezier = "md3_standard" })
hl.animation({ leaf = "fade", enabled = true, speed = 3, bezier = "md3_decel" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 4, bezier = "snappy", style = "slide" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 4, bezier = "swift_out", style = "slidevert" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 2.2, bezier = "md3_decel", style = "fade" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 2.2, bezier = "swift_in", style = "fade" })
hl.animation({ leaf = "fadeLayersIn", enabled = true, speed = 2, bezier = "md3_decel" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 2, bezier = "swift_in" })
