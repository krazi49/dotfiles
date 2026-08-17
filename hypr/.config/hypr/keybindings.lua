-- --- Variables ---
local main_mod = "ALT"
local TERMINAL = "kitty"
local EDITOR = "nvim"
local EXPLORER = "kitty --class floating_kitty yazi"
local BROWSER = "helium-browser"
local OMNIFILE = "~/.config/rofi/scripts/omnifile"
local OMNIRUN = "~/.config/rofi/scripts/omnirun"
local OMNIPALETTE = "~/.config/rofi/scripts/omnipalette"
local OMNIWEB = "~/.config/rofi/scripts/omniweb"
local OMNIKEYS = "~/.config/rofi/scripts/omnikeys"
local OMNISEARCH = "~/.config/rofi/scripts/omnisearch"
local SCREENSHOT = "~/.config/rofi/scripts/omniscreenshot"
local power_menu = "~/.config/hypr/scripts/power-menu.sh"

-- --- Window Management ---
hl.bind(main_mod .. " + Q", hl.dsp.window.close({ window = "activewindow" })) -- close (intentional, hard to misfire)
hl.bind(main_mod .. " + F11", hl.dsp.window.fullscreen({ mode = 0 })) -- fullscreen (Win F11)
hl.bind(main_mod .. " + Down", hl.dsp.window.float({ window = "activewindow", action = "toggle" })) -- float
hl.bind(main_mod .. " + Up", hl.dsp.window.float({ window = "activewindow", action = "toggle" })) -- unfloat (same toggle dispatcher)
hl.bind(main_mod .. " + G", hl.dsp.group.toggle()) -- group toggle
hl.bind(main_mod .. " + SHIFT + H", hl.dsp.window.center()) -- center window
hl.bind(main_mod .. " + Tab", hl.dsp.window.cycle_next({})) -- cycle windows
hl.bind(main_mod .. " + P", hl.dsp.window.pin({ window = "activewindow" })) -- pin window (always on top)

-- --- Focus (WASD) ---
hl.bind(main_mod .. " + SHIFT + W", hl.dsp.focus({ direction = "u" }))
hl.bind(main_mod .. " + SHIFT + A", hl.dsp.focus({ direction = "l" }))
hl.bind(main_mod .. " + SHIFT + S", hl.dsp.focus({ direction = "d" }))
hl.bind(main_mod .. " + SHIFT + D", hl.dsp.focus({ direction = "r" }))

-- --- Workspaces (direct) ---
hl.bind(main_mod .. " + 1", hl.dsp.focus({ workspace = "1" }))
hl.bind(main_mod .. " + 2", hl.dsp.focus({ workspace = "2" }))
hl.bind(main_mod .. " + 3", hl.dsp.focus({ workspace = "3" }))
hl.bind(main_mod .. " + 4", hl.dsp.focus({ workspace = "4" }))
hl.bind(main_mod .. " + 5", hl.dsp.focus({ workspace = "5" }))
hl.bind(main_mod .. " + 6", hl.dsp.focus({ workspace = "6" }))
hl.bind(main_mod .. " + 7", hl.dsp.focus({ workspace = "7" }))
hl.bind(main_mod .. " + 8", hl.dsp.focus({ workspace = "8" }))
hl.bind(main_mod .. " + 9", hl.dsp.focus({ workspace = "9" }))
hl.bind(main_mod .. " + 0", hl.dsp.focus({ workspace = "10" }))
hl.bind(main_mod .. " + minus", hl.dsp.focus({ workspace = "11" }))
hl.bind(main_mod .. " + equal", hl.dsp.focus({ workspace = "12" }))
hl.bind(main_mod .. " + S", hl.dsp.workspace.toggle_special("magic"))

-- --- Workspaces (WASD cycle) ---
-- NOTE: Tab as a chord key may need testing — if it doesn't work, a submap is the fallback
hl.bind(main_mod .. " + Tab + W", hl.dsp.focus({ workspace = "e+1" })) -- next workspace
hl.bind(main_mod .. " + Tab + D", hl.dsp.focus({ workspace = "e+1" })) -- next workspace (alt)
hl.bind(main_mod .. " + Tab + S", hl.dsp.focus({ workspace = "e-1" })) -- prev workspace
hl.bind(main_mod .. " + Tab + A", hl.dsp.focus({ workspace = "e-1" })) -- prev workspace (alt)

-- --- Move Window to Workspace ---
hl.bind(main_mod .. " + CONTROL + 1", hl.dsp.window.move({ workspace = "1" }))
hl.bind(main_mod .. " + CONTROL + 2", hl.dsp.window.move({ workspace = "2" }))
hl.bind(main_mod .. " + CONTROL + 3", hl.dsp.window.move({ workspace = "3" }))
hl.bind(main_mod .. " + CONTROL + 4", hl.dsp.window.move({ workspace = "4" }))
hl.bind(main_mod .. " + CONTROL + 5", hl.dsp.window.move({ workspace = "5" }))
hl.bind(main_mod .. " + CONTROL + 6", hl.dsp.window.move({ workspace = "6" }))
hl.bind(main_mod .. " + CONTROL + 7", hl.dsp.window.move({ workspace = "7" }))
hl.bind(main_mod .. " + CONTROL + 8", hl.dsp.window.move({ workspace = "8" }))
hl.bind(main_mod .. " + CONTROL + 9", hl.dsp.window.move({ workspace = "9" }))
hl.bind(main_mod .. " + CONTROL + 0", hl.dsp.window.move({ workspace = "10" }))
hl.bind(main_mod .. " + CONTROL + minus", hl.dsp.window.move({ workspace = "11" }))
hl.bind(main_mod .. " + CONTROL + equal", hl.dsp.window.move({ workspace = "12" }))
hl.bind(main_mod .. " + CONTROL + S", hl.dsp.window.move({ workspace = "special:magic" }))

-- --- Resize (arrows) ---
hl.bind(
	main_mod .. " + CONTROL + Right",
	hl.dsp.window.resize({ x = 30, y = 0, relative = true, window = "activewindow" }),
	{ repeating = true }
)
hl.bind(
	main_mod .. " + CONTROL + Left",
	hl.dsp.window.resize({ x = -30, y = 0, relative = true, window = "activewindow" }),
	{ repeating = true }
)
hl.bind(
	main_mod .. " + CONTROL + Up",
	hl.dsp.window.resize({ x = 0, y = -30, relative = true, window = "activewindow" }),
	{ repeating = true }
)
hl.bind(
	main_mod .. " + CONTROL + Down",
	hl.dsp.window.resize({ x = 0, y = 30, relative = true, window = "activewindow" }),
	{ repeating = true }
)

-- --- Move Window (directional) ---
hl.bind(main_mod .. " + SHIFT + CONTROL + Left", hl.dsp.window.move({ direction = "l" }))
hl.bind(main_mod .. " + SHIFT + CONTROL + Right", hl.dsp.window.move({ direction = "r" }))
hl.bind(main_mod .. " + SHIFT + CONTROL + Up", hl.dsp.window.move({ direction = "u" }))
hl.bind(main_mod .. " + SHIFT + CONTROL + Down", hl.dsp.window.move({ direction = "d" }))

-- --- Launchers ---
hl.bind(main_mod .. " + Space", hl.dsp.exec_cmd("pkill rofi || " .. OMNIPALETTE)) -- main launcher (macOS Spotlight feel)
hl.bind(main_mod .. " + SHIFT + Space", hl.dsp.exec_cmd("pkill rofi || " .. OMNISEARCH)) -- search (Win Search feel)
hl.bind(main_mod .. " + R", hl.dsp.exec_cmd("pkill rofi || " .. OMNIRUN)) -- run command (Win Run feel)
hl.bind(main_mod .. " + SHIFT + E", hl.dsp.exec_cmd("pkill rofi || " .. OMNIFILE)) -- file picker
hl.bind(main_mod .. " + SHIFT + B", hl.dsp.exec_cmd("pkill rofi || " .. OMNIWEB)) -- web search
hl.bind(main_mod .. " + K", hl.dsp.exec_cmd("pkill rofi || " .. OMNIKEYS)) -- keybinds reference
hl.bind(
	main_mod .. " + period",
	hl.dsp.exec_cmd("pkill rofi || rofi -show emoji -p Omniemoji -theme ~/.config/rofi/config-horiz.rasi")
)

-- --- Apps ---
hl.bind(main_mod .. " + T", hl.dsp.exec_cmd("kitty --class floating_kitty")) -- floating terminal (primary)
hl.bind(main_mod .. " + CTRL + T", hl.dsp.exec_cmd(TERMINAL)) -- terminal (Enter = open)
hl.bind("XF86Calculator", hl.dsp.exec_cmd("bash ~/.local/bin/asterisk"))
hl.bind(main_mod .. " + B", hl.dsp.exec_cmd(BROWSER)) -- browser
hl.bind(main_mod .. " + E", hl.dsp.exec_cmd(EXPLORER)) -- file explorer
hl.bind(main_mod .. " + N", hl.dsp.exec_cmd("swaync-client -t")) -- notifications
hl.bind(main_mod .. " + V", hl.dsp.exec_cmd("bash ~/.config/rofi/scripts/omniclip")) -- clipboard
hl.bind(main_mod .. " + W", hl.dsp.exec_cmd("~/.config/hypr/scripts/workspace-overview.sh")) -- workspace overview (rofi)
hl.bind(
	main_mod .. " + F1",
	hl.dsp.exec_cmd("helium-browser --app=https://pitwall.me/dashboard --password-store=basic")
)
hl.bind(
	main_mod .. " + F2",
	hl.dsp.exec_cmd(
		"helium-browser --app=https://claude.ai/new --password-store=basic --ozone-platform-hint=auto --disable-gpu-shader-disk-cache"
	)
)

-- --- System ---
hl.bind(main_mod .. " + L", hl.dsp.exec_cmd("hyprlock")) -- lock (Win+L)
hl.bind(main_mod .. " + SHIFT + R", hl.dsp.exec_cmd("~/rotate.sh")) -- rotate screen
hl.bind(main_mod .. " + SHIFT + K", hl.dsp.exec_cmd("killall -SIGUSR1 waybar")) -- toggle waybar
hl.bind("CONTROL + ALT + Delete", hl.dsp.exec_cmd("pkill wofi || " .. power_menu)) -- power menu
hl.bind("SUPER + SHIFT + Escape", hl.dsp.exec_cmd("~/.local/bin/panic-kill.sh")) -- panic kill
hl.bind(
	"switch:on:Lid Switch",
	hl.dsp.exec_cmd("hyprlock & ~/.config/waybar/scripts/mood-suspend.sh"),
	{ locked = true }
)

-- --- Hardware Keys ---
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("swayosd-client --output-volume mute-toggle"), { locked = true })
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
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), { locked = true })
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), { locked = true })

-- --- Mouse Controls ---
hl.bind("SUPER + mouse:276", hl.dsp.exec_cmd("swayosd-client --output-volume raise"), { repeating = true })
hl.bind("SUPER + mouse:275", hl.dsp.exec_cmd("swayosd-client --output-volume lower"), { repeating = true })
hl.bind("ALT + mouse:276", hl.dsp.exec_cmd("swayosd-client --brightness raise"), { repeating = true })
hl.bind("ALT + mouse:275", hl.dsp.exec_cmd("swayosd-client --brightness lower"), { repeating = true })
hl.bind(main_mod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind(main_mod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- --- Screenshot ---
hl.bind("Menu", hl.dsp.exec_cmd(SCREENSHOT))
hl.bind("SHIFT + Menu", hl.dsp.exec_cmd('grim -g "$(slurp)" - | satty -f -'))
hl.bind("Print", hl.dsp.exec_cmd(SCREENSHOT))
hl.bind("SHIFT + Print", hl.dsp.exec_cmd('grim -g "$(slurp)" - | satty -f -'))

-- --- Gestures ---
hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })
