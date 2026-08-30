hl.workspace_rule({ workspace = "special:magic", gaps_in = "30", gaps_out = "60" })
hl.window_rule({ match = { title = "^(Picture-in-Picture)$" }, size = "800 450" })
hl.window_rule({ match = { title = "^(Picture-in-Picture)$" }, pin = "1" })
hl.window_rule({ float = "1", match = { title = "^(Picture-in-Picture)$" } })
hl.window_rule({ float = "1", match = { class = "^(blueberry.py)$" } })
hl.window_rule({ match = { class = "^(blueberry.py)$" }, size = "800 600" })
hl.window_rule({ float = "1", match = { class = "^(floating_kitty)$" } })
hl.window_rule({ match = { class = "^(floating_kitty)$" }, size = "490 370" })
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
hl.window_rule({
	match = { class = "^(chrome-gemini\\.google\\.com.*)$" },
	size = "900 600",
})
hl.window_rule({
	match = { class = "^(chrome-claude\\.ai__new-Default)$" },
	size = "670 800",
	float = "1",
})
hl.window_rule({ match = { class = "^(chrome-gemini\\.google\\.com.*)$" }, pin = "1" })
hl.window_rule({
	fullscreen = "1",
	match = { class = "(chrome-pitwall\\.me__dashboard-Default)$" },
})
hl.window_rule({ animation = "slide bottom", match = { class = "^(valent)$" } })
hl.window_rule({ match = { class = "^(valent)$" }, size = "360 441" })
hl.window_rule({ match = { class = "^(valent)$" }, move = "1544 585" })
hl.window_rule({ float = "1", match = { class = "^(valent)$" } })
hl.window_rule({ center = "1", float = "1", match = { class = "^(com.gabm.satty)$" } })
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
hl.window_rule({ center = "1", match = { class = "^(floating_kitty)$" } })
hl.window_rule({ animation = "popin 90%", match = { class = "^(wofi)$" } })
hl.window_rule({ border_size = 0, match = { class = "^(wofi)$" } })
hl.window_rule({ float = "1", match = { class = "^(wofi)$" } })
hl.window_rule({ match = { class = "^(wofi)$" }, rounding = 0 })
hl.window_rule({ match = { class = "^(wofi)$" }, no_shadow = "1" })

hl.layer_rule({ animation = "slide left", match = { namespace = "swaync-control-center" } })
hl.layer_rule({ animation = "slide left", match = { namespace = "swaync-notification-window" } })

-- ── no_blur: save perf on fullscreen + known media/games ──────────────────────

hl.window_rule({ no_blur = "1", match = { fullscreen = true } }) -- all fullscreen windows
hl.window_rule({ no_blur = "1", match = { class = "^(mpv|vlc)$" } }) -- video players
hl.window_rule({ no_blur = "1", match = { class = "^(steam|steam_app|heroic|lutris)$" } }) -- games
hl.layer_rule({ blur = "1", match = { namespace = "swayosd" } })

hl.layer_rule({ blur = "1", match = { namespace = "^(waybar)$" } })
hl.layer_rule({ blur = "1", match = { namespace = "^(rofi)$" } })
hl.layer_rule({ blur = "1", match = { namespace = "^(notifications)$" } }) -- swaync panel
hl.layer_rule({ blur = "1", match = { namespace = "^(gtk-layer-shell)$" } }) -- misc overlays
hl.layer_rule({ blur = "1", match = { namespace = "^(selection)$" } }) --screenshot overlays

hl.layer_rule({ ignore_alpha = "0.5", match = { namespace = "^(rofi)$" } })
hl.layer_rule({ ignore_alpha = "0.5", match = { namespace = "^(notifications)$" } })

hl.layer_rule({ blur = "1", match = { namespace = "^(swaync-control-center)$" } })
hl.layer_rule({ blur = "1", match = { namespace = "^(swaync-notification-window)$" } })
hl.layer_rule({ ignore_alpha = "0.05", match = { namespace = "^(swayosd)$" } })
hl.layer_rule({ ignore_alpha = "0.05", match = { namespace = "^(swaync-control-center)$" } })
hl.layer_rule({ ignore_alpha = "0.05", match = { namespace = "^(swaync-notification-window)$" } })
hl.layer_rule({ ignore_alpha = "0.05", match = { namespace = "^(waybar)$" } })
hl.layer_rule({ ignore_alpha = "0.05", match = { namespace = "^(rofi)$" } })
