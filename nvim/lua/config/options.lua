vim.opt.termguicolors = false -- Rely strictly on your terminal ANSI profile
vim.opt.list = false

-- ── LINE NUMBER DESIGN CONFIGURATION ──
vim.opt.number = true
vim.opt.relativenumber = false

-- Keymaps & Utility Configs
vim.keymap.set({ "i", "c" }, "`", "<Esc>", { noremap = true, silent = true })
vim.keymap.set({ "i", "c" }, "<C-Left>", "<C-o>b", { noremap = true, silent = true })
vim.keymap.set("i", "<C-Right>", "<C-o>w", { noremap = true, silent = true })
vim.keymap.set("c", "<C-Right>", "<C-f>w", { noremap = true, silent = true })
vim.keymap.set({ "i", "c" }, "<C-H>", "<C-w>", { noremap = true, silent = true })
vim.keymap.set({ "i", "c" }, "<C-bs>", "<C-w>", { noremap = true, silent = true })
vim.opt.guicursor = "v-i-c:ver25-blinkwait1000-blinkon1000-blinkoff1000"

-- ── RESET AND FORCE WASD MAPPINGS ──

-- 1. Forcefully unmap 's' to clear any plugin bindings
pcall(vim.keymap.del, { "n", "v" }, "s")

-- 2. Bind WASD for movement
vim.keymap.set({ "n", "v" }, "w", "k", { noremap = true, silent = true, desc = "Move Up" })
vim.keymap.set({ "n", "v" }, "a", "h", { noremap = true, silent = true, desc = "Move Left" })
vim.keymap.set({ "n", "v" }, "s", "j", { noremap = true, silent = true, desc = "Move Down" })
vim.keymap.set({ "n", "v" }, "d", "l", { noremap = true, silent = true, desc = "Move Right" })

-- 3. Remap original actions to HJKL
vim.keymap.set({ "n", "v" }, "h", "w", { noremap = true, silent = true, desc = "Next Word" })
vim.keymap.set("n", "j", "a", { noremap = true, silent = true, desc = "Append Text" })
vim.keymap.set("n", "J", "A", { noremap = true, silent = true, desc = "Append to Line End" })
vim.keymap.set("n", "k", "s", { noremap = true, silent = true, desc = "Substitute Character" })
vim.keymap.set({ "n", "v" }, "l", "d", { noremap = true, silent = true, desc = "Delete Operator" })
vim.keymap.set("n", "ll", "dd", { noremap = true, silent = true, desc = "Delete Current Line" })

-- ── UNBIND ARROW KEYS ──
local arrows = { "<Up>", "<Down>", "<Left>", "<Right>" }
for _, key in ipairs(arrows) do
  vim.keymap.set({ "n", "v", "o" }, key, "<Nop>", { noremap = true, silent = true })
end
