#!/usr/bin/env bash
set -euo pipefail

DOTDIR="$(cd "$(dirname "$0")" && pwd)"

echo ":: dotfiles installer"
echo "   target: $DOTDIR"
echo ""

# --- helper: install packages ---
install_pkgs() {
    local file="$1"
    local label="$2"
    if [ ! -f "$DOTDIR/homes/$file" ]; then
        echo "  ! $label list not found, skipping"
        return
    fi
    if ! command -v pacman &>/dev/null; then
        echo "  ! pacman not found, skipping $label install"
        return
    fi
    echo "  installing $label..."
    sudo pacman -S --needed --noconfirm - < "$DOTDIR/homes/$file" 2>/dev/null || true
}

install_aur() {
    local file="$1"
    if [ ! -f "$DOTDIR/homes/$file" ]; then
        echo "  ! AUR list not found, skipping"
        return
    fi
    if ! command -v yay &>/dev/null && ! command -v paru &>/dev/null; then
        echo "  ! no AUR helper found, skipping AUR install"
        return
    fi
    local helper
    helper="$(command -v yay || command -v paru)"
    echo "  installing AUR packages with $helper..."
    $helper -S --needed --noconfirm - < "$DOTDIR/homes/$file" 2>/dev/null || true
}

# --- symlink helpers ---
link_dir() {
    local src="$1"
    local dst="$2"
    if [ -L "$dst" ]; then
        if [ "$(readlink "$dst")" = "$src" ]; then
            return  # already linked correctly
        fi
        rm "$dst"
    elif [ -e "$dst" ]; then
        echo "  backing up $dst -> ${dst}.bak"
        mv "$dst" "${dst}.bak"
    fi
    ln -sf "$src" "$dst"
    echo "  linked $src -> $dst"
}

link_file() {
    local src="$1"
    local dst="$2"
    if [ -L "$dst" ]; then
        if [ "$(readlink "$dst")" = "$src" ]; then
            return
        fi
        rm "$dst"
    elif [ -e "$dst" ]; then
        echo "  backing up $dst -> ${dst}.bak"
        mv "$dst" "${dst}.bak"
    fi
    ln -sf "$src" "$dst"
    echo "  linked $src -> $dst"
}

# --- main ---

# 1. packages
install_pkgs "packages-pacman.txt" "pacman"
install_aur "packages-aur.txt"

# 2. ensure ~/.config exists
mkdir -p "$HOME/.config"

# 3. symlink config dirs (most apps get their whole folder linked)
for pkg in btop cava hypr input-remapper-2 kitty MangoHud matugen nvim qt5ct qt6ct rofi systemd uwsm vkBasalt vkSumi waybar xsettingsd; do
    if [ -d "$DOTDIR/$pkg" ]; then
        link_dir "$DOTDIR/$pkg" "$HOME/.config/$pkg"
    fi
done

# 4. shared-files dirs (gtk-3.0, gtk-4.0, swaync, swayosd) — symlink individual files
for pkg in gtk-3.0 gtk-4.0 swaync swayosd; do
    if [ -d "$DOTDIR/$pkg" ]; then
        mkdir -p "$HOME/.config/$pkg"
        for f in "$DOTDIR/$pkg/"*; do
            fname="$(basename "$f")"
            link_file "$f" "$HOME/.config/$pkg/$fname"
        done
    fi
done

# 5. root-level files
if [ -f "$DOTDIR/homes/.zshrc" ]; then
    link_file "$DOTDIR/homes/.zshrc" "$HOME/.zshrc"
fi

# 6. wallpapers
if [ -d "$DOTDIR/wallpapers" ]; then
    link_dir "$DOTDIR/wallpapers" "$HOME/wallpapers"
fi

echo ""
echo "done. run 'matugen image ~/wallpapers/<your-wallpaper>' to regenerate colors."
