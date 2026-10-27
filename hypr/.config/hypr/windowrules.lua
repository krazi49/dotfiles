hl.workspace_rule({ workspace = "special:magic", gaps_in = "30", gaps_out = "60" })
hl.window_rule({ match = { title = "^(Picture-in-Picture)$" }, size = "800 450" })
hl.window_rule({ match = { title = "^(Picture-in-Picture)$" }, pin = "1" })
hl.window_rule({ float = "1", match = { title = "^(Picture-in-Picture)$" } })
hl.window_rule({ float = "1", match = { class = "^(blueberry.py)$" } })
hl.window_rule({ match = { class = "^(blueberry.py)$" }, size = "800 600" })
hl.window_rule({ float = "1", match = { class = "^(waypaper)$" } })
hl.window_rule({ match = { class = "^(waypaper)$" }, size = "800 600" })
hl.window_rule({ float = "1", match = { class = "^(zen)$" } })
hl.window_rule({ match = { class = "^(zen)$" }, size = "1220 760" })
hl.window_rule({ float = "1", match = { class = "^(com.github.hyprmod)$" } })
hl.window_rule({ match = { class = "^(com.github.hyprmod)$" }, size = "800 600" })
hl.window_rule({ float = "1", match = { class = "^(com.network.manager)$" } })
hl.window_rule({ match = { class = "^(io.github.tdesktop_x64.TDesktop)$" }, size = "500 900" })
hl.window_rule({ match = { class = "^(io.github.tdesktop_x64.TDesktop)$" }, float = "1" })
hl.window_rule({ match = { class = "^(com.network.manager)$" }, size = "940 897" })
hl.window_rule({ float = "1", match = { class = "^(chrome-gemini\\.google\\.com.*)$" } })
hl.window_rule({ center = "1", float = "1", match = { class = "^(com.gabm.satty)$" } })
hl.window_rule({ center = "1", float = "1", match = { class = "^(floating_snib)$" } })
hl.window_rule({ match = { class = "^(floating_snib)$" }, size = "60%% 50%%" })
hl.window_rule({
	float = "1",
	match = { initial_class = "^(org.gnome.NautilusPreviewer)$" },
})
hl.window_rule({
	match = { initial_class = "^(org.gnome.NautilusPreviewer)$" },
	size = "40% 55%",
})
hl.window_rule({
	center = "1",
	match = { initial_class = "^(org.gnome.NautilusPreviewer)$" },
})

hl.layer_rule({ animation = "slide bottom", match = { namespace = "swaync-control-center" } })
hl.layer_rule({ animation = "popin 80%", match = { namespace = "rofi" } })
hl.layer_rule({ animation = "slide bottom", match = { namespace = "swaync-notification-window" } })
