return {
  {
    "folke/noice.nvim",
    event = "VeryLazy",
    opts = {
      cmdline = {
        view = "cmdline_popup",
        format = {
          -- Pre-padded spaces to sit beautifully over your statusline components
          cmdline = { pattern = "^:", icon = " cmd ", lang = "vim", title = "" },
          search_down = { kind = "search", pattern = "^/", icon = " scd ", lang = "regex", title = "" },
          search_up = { kind = "search", pattern = "^%?", icon = " scu ", lang = "regex", title = "" },
          filter = { pattern = "^:%s*!", icon = " flt ", lang = "bash", title = "" },
          lua = { pattern = { "^:%s*lua%s+", "^:%s*=%s*" }, icon = " lua ", lang = "lua", title = "" },
          help = { pattern = "^:%s*he?l?p?%s+", icon = " 󰋖 ", title = "" },
          input = { icon = " inp ", title = "" },
        },
      },
      messages = {
        enabled = true,
        view = "cmdline_output", -- Routes logs flatly over the bottom space
        view_error = "cmdline_output",
        view_warn = "cmdline_output",
      },
      popupmenu = {
        backend = "cmp",
      },
      views = {
        cmdline_popup = {
          position = {
            row = "100%", -- Completely forces the input layout down to overlap the status line
            col = "0%",
          },
          size = {
            width = "100%", -- Spans edge to edge to seamlessly cover your powerline bar
            height = "auto",
          },
          border = {
            style = "none", -- No borders so it seamlessly hides the status bar under it
          },
          win_options = {
            foldenable = false,
            cursorline = false,
            winhighlight = {
              Normal = "NoiceCoverBarNormal",
            },
          },
        },
      },
    },
    init = function()
      vim.api.nvim_create_autocmd("ColorScheme", {
        callback = function()
          -- Matches your solid Matugen background color (ctermbg = 0)
          vim.api.nvim_set_hl(0, "NoiceCoverBarNormal", { ctermbg = 0, ctermfg = 7, force = true })
        end,
      })
    end,
  },
}
