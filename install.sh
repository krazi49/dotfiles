#!/bin/sh
# dotfiles installer. you already have stow, so let stow do the work.
set -e
cd "$(dirname "$0")"
stow -R */
echo "done. everything linked."
