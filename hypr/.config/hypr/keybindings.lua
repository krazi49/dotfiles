-- --- Variables ---
-- caps lock is remapped to super via input.kb_options = "caps:super" (set in your input config)
local main_mod = "SUPER"
local alt_mod = "ALT"

local TERMINAL = "kitty"
local EDITOR = "nvim"
local EXPLORER = "nautilus"
local BROWSER = "helium-browser"
local OMNIAPPS = "bash ~/.config/rofi/scripts/omniapps"
local SCREENSHOT = "bash ~/.config/rofi/scripts/omniscreenshot"
local OMNIKEYS = "bash ~/.config/rofi/scripts/omnikeys"
local power_menu = "bash ~/.config/hypr/scripts/power-menu.sh"

local HELIUM_FLAGS = "--password-store=basic"
local HELIUM_CLAUDE_FLAGS = HELIUM_FLAGS .. " --ozone-platform-hint=auto --disable-gpu-shader-disk-cache"
local REGION_SHOT = 'grim -g "$(slurp)" - | satty -f -'
local REGION_SHOT_CLIP = 'grim -g "$(slurp)" - | wl-copy'

-- --- Window Management ---
hl.bind(main_mod .. " + Q", hl.dsp.window.close({ window = "activewindow" })) -- close
hl.bind(main_mod .. " + F11", hl.dsp.window.fullscreen({ mode = 0 })) -- fullscreen
hl.bind(main_mod .. " + F", hl.dsp.window.fullscreen({ mode = 1 })) -- maximize (keeps bar and gaps)
-- NOTE: check that action = "enable" / "disable" are accepted in your version.
-- if not, swap both for action = "toggle" and use one of the keys for something else.
hl.bind(main_mod .. " + F", hl.dsp.window.float({ window = "activewindow" })) -- float
hl.bind(main_mod .. " + C", hl.dsp.window.center()) -- center (floating)
hl.bind(main_mod .. " + Tab", hl.dsp.window.cycle_next({})) -- cycle windows
hl.bind(main_mod .. " + P", hl.dsp.window.pin({ window = "activewindow" })) -- pin (floating, all workspaces)
hl.bind(main_mod .. " + J", hl.dsp.layout("togglesplit")) -- flip split (dwindle)

-- --- Groups ---
hl.bind(main_mod .. " + G", hl.dsp.group.toggle()) -- group toggle
-- NOTE: verify these two names against your version's hl.dsp.group table
hl.bind(main_mod .. " + SHIFT + bracketright", hl.dsp.group.next()) -- next tab in group
hl.bind(main_mod .. " + SHIFT + bracketleft", hl.dsp.group.prev()) -- prev tab in group

-- --- Focus (WASD) ---
hl.bind(main_mod .. " + SHIFT + W", hl.dsp.focus({ direction = "u" }))
hl.bind(main_mod .. " + SHIFT + A", hl.dsp.focus({ direction = "l" }))
hl.bind(main_mod .. " + SHIFT + S", hl.dsp.focus({ direction = "d" }))
hl.bind(main_mod .. " + SHIFT + D", hl.dsp.focus({ direction = "r" }))

-- --- Workspaces (direct + move window) ---
for i = 1, 10 do
	local key = tostring(i % 10)
	hl.bind(main_mod .. " + " .. key, hl.dsp.focus({ workspace = tostring(i) }))
	hl.bind(main_mod .. " + CONTROL + " .. key, hl.dsp.window.move({ workspace = tostring(i) }))
end
hl.bind(main_mod .. " + minus", hl.dsp.focus({ workspace = "11" }))
hl.bind(main_mod .. " + equal", hl.dsp.focus({ workspace = "12" }))
hl.bind(main_mod .. " + CONTROL + minus", hl.dsp.window.move({ workspace = "11" }))
hl.bind(main_mod .. " + CONTROL + equal", hl.dsp.window.move({ workspace = "12" }))
hl.bind(main_mod .. " + S", hl.dsp.workspace.toggle_special("magic"))
hl.bind(main_mod .. " + CONTROL + S", hl.dsp.window.move({ workspace = "special:magic" }))

-- --- Workspaces (cycle) ---
-- the old Tab + WASD chord can't register (binds take one key plus modifiers)
hl.bind(main_mod .. " + bracketright", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(main_mod .. " + bracketleft", hl.dsp.focus({ workspace = "e-1" }))
hl.bind(main_mod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(main_mod .. " + mouse_up", hl.dsp.focus({ workspace = "e-1" }))

-- --- Resize (arrows, works on tiled and floating) ---
local resize_step = 30
for key, delta in pairs({
	Right = { resize_step, 0 },
	Left = { -resize_step, 0 },
	Up = { 0, -resize_step },
	Down = { 0, resize_step },
}) do
	hl.bind(
		main_mod .. " + CONTROL + " .. key,
		hl.dsp.window.resize({ x = delta[1], y = delta[2], relative = true, window = "activewindow" }),
		{ repeating = true }
	)
end

-- --- Window mode submap (super + M) ---
-- wasd        = move window in direction (swaps when tiled)
-- arrows      = nudge window by pixels (floating)
-- shift + wasd = resize (tiled and floating)
-- escape / return = leave
local nudge = 40
local grow = 40
hl.define_submap("window", function()
	hl.bind("W", hl.dsp.window.move({ direction = "u" }))
	hl.bind("A", hl.dsp.window.move({ direction = "l" }))
	hl.bind("S", hl.dsp.window.move({ direction = "d" }))
	hl.bind("D", hl.dsp.window.move({ direction = "r" }))

	hl.bind(
		"Up",
		hl.dsp.window.move({ x = 0, y = -nudge, relative = true, window = "activewindow" }),
		{ repeating = true }
	)
	hl.bind(
		"Down",
		hl.dsp.window.move({ x = 0, y = nudge, relative = true, window = "activewindow" }),
		{ repeating = true }
	)
	hl.bind(
		"Left",
		hl.dsp.window.move({ x = -nudge, y = 0, relative = true, window = "activewindow" }),
		{ repeating = true }
	)
	hl.bind(
		"Right",
		hl.dsp.window.move({ x = nudge, y = 0, relative = true, window = "activewindow" }),
		{ repeating = true }
	)

	hl.bind(
		"SHIFT + Up",
		hl.dsp.window.resize({ x = 0, y = grow, relative = true, window = "activewindow" }),
		{ repeating = true }
	)
	hl.bind(
		"SHIFT + Down",
		hl.dsp.window.resize({ x = 0, y = -grow, relative = true, window = "activewindow" }),
		{ repeating = true }
	)
	hl.bind(
		"SHIFT + Right",
		hl.dsp.window.resize({ x = grow, y = 0, relative = true, window = "activewindow" }),
		{ repeating = true }
	)
	hl.bind(
		"SHIFT + Left",
		hl.dsp.window.resize({ x = -grow, y = 0, relative = true, window = "activewindow" }),
		{ repeating = true }
	)

	hl.bind("C", hl.dsp.window.center())
	hl.bind("SHIFT + W", hl.dsp.window.float({ window = "activewindow", action = "enable" }))
	hl.bind("SHIFT + S", hl.dsp.window.float({ window = "activewindow", action = "disable" }))

	hl.bind("Escape", hl.dsp.submap("reset"))
	hl.bind("Return", hl.dsp.submap("reset"))
end)
hl.bind(main_mod .. " + M", hl.dsp.submap("window"))

-- --- Launchers ---
hl.bind(main_mod .. " + D", hl.dsp.exec_cmd("pkill rofi || " .. OMNIAPPS)) -- app launcher (most used first)
hl.bind(main_mod .. " + K", hl.dsp.exec_cmd("pkill rofi || " .. OMNIKEYS)) -- keybinds reference
hl.bind(
	main_mod .. " + period",
	hl.dsp.exec_cmd("pkill rofi || rofi -show emoji -p Omniemoji -theme ~/.config/rofi/config-horiz.rasi")
)

-- --- Apps ---
hl.bind(main_mod .. " + T", hl.dsp.exec_cmd("kitty --class floating_kitty")) -- floating terminal
hl.bind(main_mod .. " + CONTROL + T", hl.dsp.exec_cmd(TERMINAL)) -- tiled terminal
hl.bind("XF86Calculator", hl.dsp.exec_cmd("bash ~/.local/bin/asterisk"))
hl.bind(main_mod .. " + B", hl.dsp.exec_cmd(BROWSER)) -- browser
hl.bind(main_mod .. " + E", hl.dsp.exec_cmd(EXPLORER)) -- file explorer
hl.bind(main_mod .. " + N", hl.dsp.exec_cmd("swaync-client -t")) -- notifications

-- --- System ---
hl.bind(main_mod .. " + L", hl.dsp.exec_cmd("pidof hyprlock || hyprlock")) -- lock (no stacking)
hl.bind(main_mod .. " + SHIFT + R", hl.dsp.exec_cmd("~/rotate.sh")) -- rotate screen
hl.bind(main_mod .. " + SHIFT + K", hl.dsp.exec_cmd("killall -SIGUSR1 waybar")) -- toggle waybar
hl.bind("CONTROL + ALT + Delete", hl.dsp.exec_cmd("pkill rofi || " .. power_menu)) -- power menu
hl.bind(main_mod .. " + SHIFT + Escape", hl.dsp.exec_cmd("~/.local/bin/panic-kill.sh")) -- panic kill
hl.bind("switch:on:Lid Switch", hl.dsp.exec_cmd("pidof hyprlock || hyprlock &"), { locked = true })

-- --- Hardware Keys ---
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("swayosd-client --output-volume mute-toggle"), { locked = true })
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("swayosd-client --input-volume mute-toggle"), { locked = true })
hl.bind(
	"XF86AudioLowerVolume",
	hl.dsp.exec_cmd("swayosd-client --output-volume lower"),
	{ locked = true, repeating = true }
)
hl.bind(
	"XF86AudioRaiseVolume",
	hl.dsp.exec_cmd("swayosd-client --output-volume raise"),
	{ locked = true, repeating = true }
)
hl.bind(
	"XF86MonBrightnessUp",
	hl.dsp.exec_cmd("swayosd-client --brightness raise"),
	{ locked = true, repeating = true }
)
hl.bind(
	"XF86MonBrightnessDown",
	hl.dsp.exec_cmd("swayosd-client --brightness lower"),
	{ locked = true, repeating = true }
)
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioStop", hl.dsp.exec_cmd("playerctl stop"), { locked = true })
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), { locked = true })
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), { locked = true })

-- --- Mouse Controls ---
-- volume on main mod, brightness on alt, drag/resize on main mod with different buttons
hl.bind(main_mod .. " + mouse:276", hl.dsp.exec_cmd("swayosd-client --output-volume raise"), { repeating = true })
hl.bind(main_mod .. " + mouse:275", hl.dsp.exec_cmd("swayosd-client --output-volume lower"), { repeating = true })
hl.bind(alt_mod .. " + mouse:276", hl.dsp.exec_cmd("swayosd-client --brightness raise"), { repeating = true })
hl.bind(alt_mod .. " + mouse:275", hl.dsp.exec_cmd("swayosd-client --brightness lower"), { repeating = true })
hl.bind(main_mod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind(main_mod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- --- Screenshot / Tools ---
for _, key in ipairs({ "Menu", "Print" }) do
	hl.bind(key, hl.dsp.exec_cmd(SCREENSHOT))
	hl.bind("SHIFT + " .. key, hl.dsp.exec_cmd(REGION_SHOT))
	hl.bind("CONTROL + " .. key, hl.dsp.exec_cmd(REGION_SHOT_CLIP))
end
hl.bind(main_mod .. " + SHIFT + P", hl.dsp.exec_cmd("hyprpicker -a")) -- colour picker to clipboard

-- --- Gestures ---
hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })
