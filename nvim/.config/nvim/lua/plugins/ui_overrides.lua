return {
  -- ── RESTRUCTURE SNACKS WORKSPACE (KEEPING CLEAN CAPSULES) ────────────────
  {
    "folke/snacks.nvim",
    priority = 1000,
    opts = {
      win = {
        border = { "╭", "─", "╮", "│", "╯", "─", "╰", "│" },
        wo = {
          winhighlight = "Normal:NormalFloat,FloatBorder:FloatBorder",
        },
      },
      picker = {
        layout = {
          preset = "modern", -- Kept your modern layout, but stripped the clutter below
        },
        win = {
          input = { border = { "╭", "─", "╮", "│", "╯", "─", "╰", "│" } },
          list = { border = { "╭", "─", "╮", "│", "╯", "─", "╰", "│" } },
          preview = { border = { "╭", "─", "╮", "│", "╯", "─", "╰", "│" } },
        },
      },
      explorer = {
        win = {
          border = { "╭", "─", "╮", "│", "╯", "─", "╰", "│" },
        },
      },
      input = {
        win = {
          border = { "╭", "─", "╮", "│", "╯", "─", "╰", "│" },
        },
      },
      -- Redirect snacks native alerts to use a tiny, compact corner layout instead
      notifier = {
        style = "minimal",
        margin = { top = 1, right = 1, bottom = 0 },
      },
    },
  },

  -- ── FORCE NOICE TO BANISH NOTIFICATIONS FROM THE PANES ──────────────────
  {
    "folke/noice.nvim",
    event = "VeryLazy",
    opts = {
      messages = {
        enabled = true,
        view = "mini", -- Redirects generic system writes (:w logs) to a tiny corner popup
        view_error = "mini", -- Keeps errors safely away from your search rows
        view_warn = "mini", -- Keeps warnings safely away from your search rows
      },
      routes = {
        -- CRITICAL RULE: Intercepts and completely suppresses search count logs
        -- (e.g., "Wrote file", "Search hit BOTTOM") so they NEVER split your screen panels
        {
          filter = {
            event = "msg_show",
            any = {
              { kind = "search_count" },
              { find = "written" },
              { find = "change" },
            },
          },
          opts = { skip = true }, -- Instantly dismisses them silently
        },
      },
    },
  },

  -- ── TELESCOPE PARITY ────────────────────────────────────────────────────
  {
    "nvim-telescope/telescope.nvim",
    opts = {
      defaults = {
        sorting_strategy = "ascending",
        layout_config = {
          horizontal = { prompt_position = "top" },
        },
        borderchars = { "─", "│", "─", "│", "╭", "╮", "╯", "╰" },
      },
    },
  },
}
