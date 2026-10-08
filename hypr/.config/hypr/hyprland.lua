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

	hl.exec_cmd("hyprctl reload")
	hl.exec_cmd("hyprresume")
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

		dim_inactive = false,
		dim_strength = 0.15,
		dim_special = 0.2,

		-- lumina: deep cinematic shadows, clean falloff, tight scale
		shadow = {
			enabled = true,
			color = "0xff555555",
			color_inactive = "0xff222222",
			offset = { 4, 4 },
			range = 0,
			render_power = 0,
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
		gaps_out = 8,
		resize_on_border = true,
		col = {
			active_border = "0xff555555",
			inactive_border = "0xff222222",
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
		kb_options = "caps:super",
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
		font_family = "Zalando Sans",
	},

	xwayland = {
		enabled = true,
		force_zero_scaling = false,
	},
})

hl.config({
	plugin = {
		dynamic_cursors = {

			-- enables the plugin
			enabled = true,

			-- sets the cursor behaviour, supports these values:
			-- tilt    - tilt the cursor based on x-velocity
			-- rotate  - rotate the cursor based on movement direction
			-- stretch - stretch the cursor shape based on direction and velocity
			-- none    - do not change the cursor's behaviour
			mode = "stretch",

			-- minimum angle difference in degrees after which the shape is changed
			-- smaller values are smoother, but more expensive for hw cursors
			threshold = 1,

			-- for mode = "rotate"
			rotate = {

				-- length in px of the simulated stick used to rotate the cursor
				-- most realistic if this is your actual cursor size
				length = 20,

				-- clockwise offset applied to the angle in degrees
				-- this will apply to ALL shapes
				offset = 0.0,
			},

			-- for mode = "tilt"
			tilt = {

				-- controls how powerful the tilt is, the lower, the more power
				-- this value controls at which speed (px/s) the full tilt is reached
				limit = 5000,

				-- relationship between speed and tilt, supports these values:
				-- linear             - a linear function is used
				-- quadratic          - a quadratic function is used (most realistic to actual air drag)
				-- negative_quadratic - negative version of the quadratic one, feels more aggressive
				-- see `activation` in `src/mode/utils.cpp` for how exactly the calculation is done
				activation = "negative_quadratic",

				-- time window (ms) over which the speed is calculated
				-- higher values will make slow motions smoother but more delayed
				window = 100,

				-- full tilt for each side (°)
				full = 60,
			},

			-- for mode = "stretch"
			stretch = {

				-- controls how much the cursor is stretched
				-- this value controls at which speed (px/s) the full stretch is reached
				-- the full stretch being twice the original length
				limit = 3000,

				-- relationship between speed and stretch amount, supports these values:
				-- linear             - a linear function is used
				-- quadratic          - a quadratic function is used
				-- negative_quadratic - negative version of the quadratic one, feels more aggressive
				-- see `activation` in `src/mode/utils.cpp` for how exactly the calculation is done
				activation = "quadratic",

				-- time window (ms) over which the speed is calculated
				-- higher values will make slow motions smoother but more delayed
				window = 100,
			},

			-- configure shake to find
			-- magnifies the cursor if its is being shaken
			shake = {

				-- enables shake to find
				enabled = true,

				-- controls how soon a shake is detected
				-- lower values mean sooner
				threshold = 6.0,

				-- magnification level immediately after shake start
				base = 4.0,
				-- magnification increase per second when continuing to shake
				speed = 4.0,
				-- how much the speed is influenced by the current shake intensity
				influence = 0.0,

				-- maximal magnification the cursor can reach
				-- values below 1 disable the limit (e.g. 0)
				limit = 0.0,

				-- time in milliseconds the cursor will stay magnified after a shake has ended
				timeout = 2000,

				-- show cursor behaviour `tilt`, `rotate`, etc. while shaking
				effects = false,

				-- enable ipc events for shake
				-- see the `ipc` section below
				ipc = false,
			},

			-- use hyprcursor to get a higher resolution texture when the cursor is magnified
			-- see the `hyprcursor` section below
			hyprcursor = {

				-- use nearest-neighbour (pixelated) scaling when magnifying beyond texture size
				-- this will also have effect without hyprcursor support being enabled
				-- 0 - never use pixelated scaling
				-- 1 - use pixelated when no highres image
				-- 2 - always use pixelated scaling
				nearest = 1,

				-- enable dedicated hyprcursor support
				enabled = true,

				-- resolution in pixels to load the magnified shapes at
				-- be warned that loading a very high-resolution image will take a long time and might impact memory consumption
				-- -1 means we use [normal cursor size] * [shake:base option]
				resolution = -1,

				-- shape to use when clientside cursors are being magnified
				-- see the shape-name property of shape rules for possible names
				-- specifying clientside will use the actual shape, but will be pixelated
				fallback = "clientside",
			},
		},
	},
})
