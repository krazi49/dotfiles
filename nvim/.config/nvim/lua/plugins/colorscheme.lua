return {
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = function()
        vim.opt.termguicolors = false
        local hl = vim.api.nvim_set_hl

        -- 1. THE SOLID SHIELD (Context Menu & Popups)
        hl(0, "NormalFloat", { ctermbg = 0, ctermfg = 7, force = true })
        hl(0, "FloatBorder", { ctermbg = 0, ctermfg = 12, force = true })
        hl(0, "Pmenu", { ctermbg = 0, ctermfg = 7, force = true })
        hl(0, "MatchParen", { ctermbg = "NONE", ctermfg = 12, bold = true, underline = true })
        hl(0, "Visual", { ctermbg = 8, ctermfg = 12, bold = true })
        hl(0, "PmenuSel", { ctermbg = 8, ctermfg = 12, bold = true, force = true })

        -- 2. TRANSPARENCY & CORE UI DESIGN
        hl(0, "Normal", { bg = "NONE", ctermbg = "NONE" })
        hl(0, "NormalNC", { bg = "NONE", ctermbg = "NONE" })
        hl(0, "SignColumn", { bg = "NONE", ctermbg = "NONE" })

        -- Custom Sidebar Line Number Highlights
        hl(0, "LineNr", { ctermfg = 8, bg = "NONE" })
        hl(0, "CursorLineNr", { ctermfg = 12, bg = "NONE", bold = true })

        hl(0, "IblIndent", { ctermfg = 8 })
        hl(0, "IblWhitespace", { ctermfg = 8 })
        hl(0, "IblScope", { ctermfg = 12 })

        -- 3. SYNTAX
        hl(0, "Comment", { ctermfg = 8 })
        hl(0, "String", { ctermfg = 10 })
        hl(0, "Keyword", { ctermfg = 12 })
        hl(0, "Function", { ctermfg = 12 })
        -- Append these lines inside your colorscheme.lua function block:
        local hl = vim.api.nvim_set_hl

        -- 1. Obliterate the vertical split separator lines entirely
        hl(0, "WinSeparator", { bg = "NONE", ctermbg = "NONE", fg = 0, ctermfg = 0 })
        hl(0, "RenderMarkdownH1Bg", { bg = "NONE", ctermbg = "NONE" })

        -- 2. Make the file tree background seamlessly match the editor background
        hl(0, "NeoTreeNormal", { bg = "NONE", ctermbg = "NONE" })
        hl(0, "NeoTreeNormalNC", { bg = "NONE", ctermbg = "NONE" })
        hl(0, "SnacksExplorerNormal", { bg = "NONE", ctermbg = "NONE" })
      end,
    },
  },
  {
    "nvim-lualine/lualine.nvim",
    event = "VeryLazy",
    opts = function(_, opts)
      vim.opt.cmdheight = 1 -- Set to 1 to keep the screen bottom tight and modular
      vim.api.nvim_set_hl(0, "StatusLine", { bg = "NONE", ctermbg = "NONE" })
      vim.api.nvim_set_hl(0, "StatusLineNC", { bg = "NONE", ctermbg = "NONE" })

      local m3_theme = {
        normal = {
          a = { fg = 0, bg = 13, gui = "bold" },
          b = { fg = 7, bg = 8 },
          c = { fg = 7, bg = "NONE" },
        },
        insert = { a = { fg = 0, bg = 14, gui = "bold" } },
        visual = { a = { fg = 0, bg = 15, gui = "bold" } },
        command = { a = { fg = 0, bg = 13, gui = "bold" } },
        replace = { a = { fg = 0, bg = 9, gui = "bold" } },
        inactive = { c = { fg = 8, bg = "NONE" } },
      }

      opts.options = {
        theme = m3_theme,
        globalstatus = true,
        component_separators = "",
        section_separators = "",
      }

      opts.sections = {
        lualine_a = {
          {
            "mode",
            separator = { left = "", right = "" },
            padding = 0,
            fmt = function(str)
              return str:lower()
            end,
          },
        },
        lualine_b = {
          {
            function()
              return " "
            end,
            padding = 0,
            color = { bg = "NONE" },
          },
          { "branch", icon = "", separator = { left = "", right = "" }, padding = 0 },
        },
        lualine_c = {
          {
            function()
              return "  "
            end,
            padding = 0,
            color = { bg = "NONE" },
          },
          { "filename", path = 1, separator = "", padding = 0 },
        },
        lualine_x = { { "filetype", separator = { left = "", right = "" }, padding = 0 } },
        lualine_y = {
          {
            function()
              return " "
            end,
            padding = 0,
            color = { bg = "NONE" },
          },
          { "progress", separator = { left = "", right = "" }, padding = 0 },
        },
        lualine_z = {
          {
            function()
              return " "
            end,
            padding = 0,
            color = { bg = "NONE" },
          },
          { "location", separator = { left = "", right = "" }, padding = 0 },
        },
      }
      opts.winbar = {}
    end,
  },
  { "lukas-reineke/indent-blankline.nvim", enabled = false },
}
