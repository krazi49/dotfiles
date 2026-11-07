return {
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = function()
        -- termguicolors is set in config/options.lua; matugen owns all colors via
        -- colors/matugen.vim (guifg/guibg). No cterm overrides here — they clobber
        -- the matugen palette.
        local hl = vim.api.nvim_set_hl

        -- transparency & core UI (bg only, never force cterm colors over matugen)
        hl(0, "Normal", { bg = "NONE" })
        hl(0, "NormalNC", { bg = "NONE" })
        hl(0, "SignColumn", { bg = "NONE" })
        hl(0, "NormalFloat", { bg = "NONE" })
        hl(0, "FloatBorder", { bg = "NONE" })
        hl(0, "Pmenu", { bg = "NONE" })
        hl(0, "WinSeparator", { bg = "NONE" })
        hl(0, "NeoTreeNormal", { bg = "NONE" })
        hl(0, "NeoTreeNormalNC", { bg = "NONE" })
        hl(0, "SnacksExplorerNormal", { bg = "NONE" })
      end,
    },
  },
  {
    "nvim-lualine/lualine.nvim",
    event = "VeryLazy",
    opts = function(_, opts)
      vim.opt.cmdheight = 1

      -- lualine theme built from matugen_res.lua so the status bar stays in
      -- sync when the wallpaper changes
      local ok, res = pcall(require, "matugen_res")
      local m3_theme
      if ok and res then
        m3_theme = {
          normal = {
            a = { fg = res.on_primary, bg = res.primary, gui = "bold" },
            b = { fg = res.on_surface, bg = res.surface_container_high },
            c = { fg = res.on_surface, bg = "NONE" },
          },
          insert = { a = { fg = res.on_secondary, bg = res.secondary, gui = "bold" } },
          visual = { a = { fg = res.on_tertiary, bg = res.tertiary, gui = "bold" } },
          command = { a = { fg = res.on_primary, bg = res.primary, gui = "bold" } },
          replace = { a = { fg = res.on_error_container, bg = res.error_container, gui = "bold" } },
          inactive = { c = { fg = res.outline, bg = "NONE" } },
        }
      else
        m3_theme = "auto"
      end

      opts.options = {
        theme = m3_theme,
        globalstatus = true,
        component_separators = { left = "", right = "" },
        section_separators = { left = "", right = "" },
      }

      opts.sections = {
        lualine_a = {
          { "mode", padding = 1, fmt = function(str) return str:lower() end },
        },
        lualine_b = {
          { "branch", icon = "", padding = 0 },
        },
        lualine_c = {
          { "filename", path = 1, padding = 0 },
        },
        lualine_x = { { "filetype", padding = 0 } },
        lualine_y = { { "progress", padding = 0 } },
        lualine_z = { { "location", padding = 1 } },
      }
      opts.winbar = {}
    end,
  },
  { "lukas-reineke/indent-blankline.nvim", enabled = false },
}
