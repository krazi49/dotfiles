-- bootstrap lazy.nvim, LazyVim and your plugins
require("config.lazy")
require("config.options")

-- ── UNBIND ARROW KEYS ──
vim.api.nvim_create_autocmd("User", {
  pattern = "VeryLazy",
  callback = function()
    local arrows = { "<Up>", "<Down>", "<Left>", "<Right>" }
    for _, key in ipairs(arrows) do
      vim.keymap.set({ "n", "v", "o" }, key, "<Nop>", { noremap = true, silent = true })
    end
  end,
})
