-- ╔══════════════════════════════════════════╗
-- ║  volticOS · hyprland config              ║
-- ║  lumina edition                          ║
-- ╚══════════════════════════════════════════╝

require("keybindings")
require("windowrules")
require("animations")
require("monitors")

-- ── environment ────────────────────────────────────────────────────────────────

hl.env("GTK_MODULES", "appmenu-gtk-module")
hl.env("UBUNTU_MENUPROXY", "1")
hl.env("QT_QPA_PLATFORMTHEME", "qt5ct")
hl.env("XCURSOR_THEME", "Hackneyed-Dark-24px")
hl.env("XCURSOR_SIZE", "24")

-- ── startup ────────────────────────────────────────────────────────────────────

hl.on("hyprland.start", function()
	-- wayland environment (once)
	hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
	hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")

	-- system services
	hl.exec_cmd("udiskie --no-notify -t &")
	hl.exec_cmd("paplay ~/.sounds/login.wav")
	hl.exec_cmd("python ~/dotfiles/hypr/.config/hypr/scripts/sound_daemon.py")
	hl.exec_cmd("/usr/bin/gnome-keyring-daemon --start --components=secrets")
	hl.exec_cmd("/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1")

	-- clipboard
	hl.exec_cmd("wl-clip-persist --clipboard regular")
	hl.exec_cmd("wl-paste --type text  --watch cliphist store")
	hl.exec_cmd("wl-paste --type image --watch cliphist store")

	-- theming
	hl.exec_cmd("gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'")
	hl.exec_cmd("hyprctl setcursor Hackneyed-Dark-24px 18")

	-- ui layer
	hl.exec_cmd("swaync")
	hl.exec_cmd("hyprpm reload")
	hl.exec_cmd("hyprpaper")
	hl.exec_cmd("waybar")
	hl.exec_cmd("awww-daemon")
	hl.exec_cmd("gsr-ui")
	hl.exec_cmd("~/.config/waybar/scripts/adaptive_island_cpu.py")

	-- OpenClaw gateway
	hl.exec_cmd("openclaw gateway start")
	hl.exec_cmd("omniroute &")
	hl.exec_cmd("hyprctl reload")
end)

hl.on("config.reloaded", function()
	hl.exec_cmd("pkill swayosd-server; swayosd-server --top-margin 0.96")
end)

-- ── config ─────────────────────────────────────────────────────────────────────

hl.config({
	cursor = {
		inactive_timeout = 0,
	},

	decoration = {
		active_opacity = 1,
		inactive_opacity = 1,
		rounding = 0,
		rounding_power = 0,

		blur = {
			enabled = false,
			passes = 1,
			size = 3,
			new_optimizations = true,
			xray = false,
			popups = true,
		},

		dim_inactive = true,
		dim_strength = 0.15,
		dim_special = 0.2,

		-- lumina: deep cinematic shadows, clean falloff, tight scale
		shadow = {
			enabled = true,
			color = "0xffffffff",
			color_inactive = "0xff444444",
			offset = { 10, 10 },
			range = 1,
			render_power = 1,
			scale = 1,
		},
	},

	dwindle = {
		force_split = true,
		smart_split = true,
	},

	ecosystem = {
		no_donation_nag = true,
	},

	general = {
		border_size = 3,
		gaps_in = 10,
		gaps_out = 15,
		resize_on_border = true,
		col = {
			active_border = "0xffffffff",
			inactive_border = "0xff444444",
		},
		snap = {
			enabled = false,
		},
	},

	gestures = {
		workspace_swipe_forever = true,
	},

	input = {
		kb_layout = "gb",
		kb_variant = "",
		kb_options = "",
		natural_scroll = false,
	},

	master = {
		allow_small_split = false,
		mfact = 0.9,
		new_status = "slave",
		orientation = "right",
	},

	misc = {
		animate_manual_resizes = true,
		animate_mouse_windowdragging = true,
		disable_hyprland_logo = true,
		font_family = "TikTok Sans",
	},

	xwayland = {
		enabled = true,
		force_zero_scaling = false,
	},

	plugin = {
		hyprbars = {
			bar_height = 10,
			bar_color = "0xffffffff",
			inactive_button_color = "0xff444444",
			bar_part_of_window = true,
			bar_title_enabled = false,
			bar_precedence_over_border = false,
			on_double_click = "hyprctl dispatch fullscreen 1",
			col = {
				text = "0xff1c110c",
			},
		},
	},
})
