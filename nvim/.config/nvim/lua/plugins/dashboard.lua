return {
  {
    "folke/snacks.nvim",
    opts = {
      dashboard = {
        sections = {
          { section = "header", padding = 2 },
          { section = "keys", gap = 1, padding = 1, align = "center" },
          { section = "startup", padding = 2 },
        },
        preset = {
          header = [[
   _  __                          
  / |/ /__ ___ _  __ (_)__ _      
 /    / -_) _ \ |/ / / /  ' \     
/_/|_/\__/\___/___/_/_/_/_/_/     ]],

          keys = {
            { icon = " 󰱼 ", key = "f", desc = "search files      ", action = ":lua Snacks.dashboard.pick('files')" },
            { icon = " 󰝒 ", key = "n", desc = "draft new file    ", action = ":ene | startinsert" },
            {
              icon = " 󱎸 ",
              key = "g",
              desc = "global grep       ",
              action = ":lua Snacks.dashboard.pick('live_grep')",
            },
            {
              icon = " 󰋚 ",
              key = "r",
              desc = "recent history    ",
              status = "oldfiles",
              action = ":lua Snacks.dashboard.pick('oldfiles')",
            },
            {
              icon = " 󰒓 ",
              key = "c",
              desc = "system config     ",
              action = ":lua Snacks.dashboard.pick('files', {cwd = vim.fn.stdpath('config')})",
            },
            {
              icon = " 󰦛 ",
              key = "s",
              desc = "resume session    ",
              action = ":lua Snacks.dashboard.pick('resume')",
            },
            { icon = " 󰒲 ", key = "l", desc = "plugin manager    ", action = ":Lazy" },
            { icon = " 󰈆 ", key = "q", desc = "exit editor       ", action = ":qa" },
          },
        },
        formats = {
          startup = {
            format = "  󱐋 v${version}  •  ${count} plugins  •  ${time}  ",
            hl = "SnacksDashboardFooter",
          },
        },
      },
    },
  },
}
