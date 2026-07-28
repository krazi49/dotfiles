export PATH="/usr/bin:$PATH"
export PATH="$HOME/.npm-global/bin:$PATH"
# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH

# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time Oh My Zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
ZSH_THEME=""

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in $ZSH/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment one of the following lines to change the auto-update behavior
# zstyle ':omz:update' mode disabled  # disable automatic updates
# zstyle ':omz:update' mode auto      # update automatically without asking
# zstyle ':omz:update' mode reminder  # just remind me to update when it's time

# Uncomment the following line to change how often to auto-update (in days).
# zstyle ':omz:update' frequency 13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# You can also set it to another string to have that shown instead of the default red dots.
# e.g. COMPLETION_WAITING_DOTS="%F{yellow}waiting...%f"
# Caution: this setting can cause issues with multiline prompts in zsh < 5.7.1 (see #5765)
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(git zsh-autosuggestions fast-syntax-highlighting zsh-syntax-highlighting history-substring-search)

source $ZSH/oh-my-zsh.sh

# Starship prompt
precmd() { export STARSHIP_LAST_STATUS=$? }
eval "$(starship init zsh)"

# eza aliases — modern ls replacement with icons
unalias ls 2>/dev/null
unalias ll 2>/dev/null
unalias la 2>/dev/null
unalias l  2>/dev/null
unalias tree 2>/dev/null
alias ls='eza --icons=auto'
alias ll='eza -l --icons=auto --git'
alias la='eza -la --icons=auto --git'
alias l='eza -l --icons=auto --git'
alias tree='eza --tree --icons=auto'
alias power='sudo'
alias openclaw tui='clawt'

# User configuration

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='nvim'
# fi

# Compilation flags
# export ARCHFLAGS="-arch $(uname -m)"

# Set personal aliases, overriding those provided by Oh My Zsh libs,
# plugins, and themes. Aliases can be placed here, though Oh My Zsh
# users are encouraged to define aliases within a top-level file in
# the $ZSH_CUSTOM folder, with .zsh extension. Examples:
# - $ZSH_CUSTOM/aliases.zsh
# - $ZSH_CUSTOM/macos.zsh
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"

# 1. Enable completion-based ghost text properly
# 'history' looks at what you did; 'completion' looks at what's in the folder
export ZSH_AUTOSUGGEST_STRATEGY=(history completion)

# 2. Make the ghost text update instantly
export ZSH_AUTOSUGGEST_USE_ASYNC=1

# 3. FIX: Show hidden files (like .config) in the ghost text
# Without this, it ignores anything starting with a dot
_comp_options+=(globdots) 

# 4. Set the ghost text color to be visible but dim
export ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=8"

# This forces Zsh to generate completion matches even before you hit Tab
zstyle ':completion:*' completions 1

# TTY Aesthetic Tweaks
if [[ $TERM == "linux" ]]; then
    # Hide the blinking cursor immediately
    setterm -cursor off
    # Clear any leftover boot messages
    clear
fi

alias startgnome="XDG_SESSION_TYPE=wayland dbus-run-session gnome-session"

if [[ -z "$DISPLAY" && "$(tty)" == /dev/tty1 ]]; then
    exec start-hyprland
fi

# Bind Up arrow to search backward
bindkey '^[[A' history-substring-search-up
# Bind Down arrow to search forward
bindkey '^[[B' history-substring-search-down
# Bind Ctrl + Backspace to delete the previous word
bindkey '^H' backward-kill-word
# Press Ctrl + Space to accept the next word of a suggestion
bindkey '^ ' forward-word

# YouTube Music Playlist Function
playlist() {
    mpv --no-video --loop-playlist=inf 'https://music.youtube.com/playlist?list=PLceR-IJd9-lJPmrT4QLIx2_BuTFCy3NA-&si=IVgzkRTeF3bURw7i'
}

playlist-shuffle() {
    mpv --no-video --loop-playlist=inf --shuffle 'https://music.youtube.com/playlist?list=PLceR-IJd9-lJPmrT4QLIx2_BuTFCy3NA-&si=IVgzkRTeF3bURw7i'
}

eval $(thefuck --alias)

flatline() {
    killall "$@"
}

# Direct commands for poli
get() { poli get "$@"; }
search() { poli search "$@"; }
update() { poli update "$@"; }
remove() { poli remove "$@"; }
orphans() { poli orphans "$@"; }
info() { poli info "$@"; }
check() { poli check "$@"; }
log() { poli log "$@"; }
reinstall() { poli reinstall "$@"; }
stats() { poli stats "$@"; }

# Overriding the default help to show your assembly manual
help() {
  if [ $# -ne 0 ]; then
    builtin help "$@"
    return
  fi
  poli help
}

export CHROMIUM_FLAGS="--password-store=basic"

export GROQ_API_KEY="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"

export MISTRAL_API_KEY="1gS84Uv8T5x8cXXxBTdbEZ84Efj78Mgn"

export DISCORD_BOT_TOKEN="MTUxNjA5NTE5MDA3MzQ3NTE4Mg.GSBLt-.2fsH7biYkpTXxWQuWtFgWw_djNEQEWXiARc2Rc"

export YAY_ANSI=1
export PATH="$HOME/.local/bin:$PATH"


# opencode
export PATH=/home/em/.opencode/bin:$PATH

alias ai="crush"


# Added by Antigravity CLI installer
export PATH="/home/em/.local/bin:$PATH"

eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv zsh)"

# OpenClaw Completion
[ -f "/home/em/.openclaw/completions/openclaw.zsh" ] && source "/home/em/.openclaw/completions/openclaw.zsh"

clear && fastfetch

# Toggle Docker data-root between USB and default
toggle-docker-usb() {
  local usb_path="/run/media/em/powerdrive/docker-data"
  local daemon_file="/etc/docker/daemon.json"
  local current_config

  # Check if jq is installed
  if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install it first (e.g., poli get jq)."
    return 1
  fi

  # Get current data-root setting (empty string if not set or file doesn't exist)
  if [[ -f "$daemon_file" ]]; then
    current_config=$(jq -r '.["data-root"] // empty' "$daemon_file" 2>/dev/null)
  else
    current_config=""
  fi

  if [[ "$current_config" == "$usb_path" ]]; then
    # Switching back to default
    echo "Switching Docker data-root to default (removing USB setting)..."
    if [[ -f "$daemon_file" ]]; then
      # Remove the data-root key
      jq 'del(.["data-root"])' "$daemon_file" | sudo tee "$daemon_file" > /dev/null
    else
      echo "{}" > "$daemon_file"
    fi
  else
    # Switching to USB
    echo "Switching Docker data-root to USB: $usb_path"
    # Ensure the USB directory exists
    if [[ ! -d "$usb_path" ]]; then
      echo "Error: USB directory $usb_path does not exist. Is the USB plugged in?"
      return 1
    fi
    # Create or update the daemon.json
    if [[ -f "$daemon_file" ]]; then
      jq --arg path "$usb_path" '.["data-root"] = $path' "$daemon_file" | sudo tee "$daemon_file" > /dev/null
    else
      echo "{\"data-root\": \"$usb_path\"}" | sudo tee "$daemon_file" > /dev/null
    fi
  fi

  # Restart Docker
  echo "Restarting Docker..."
  sudo systemctl restart docker
}
