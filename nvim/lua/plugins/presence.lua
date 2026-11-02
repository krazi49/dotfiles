return {
  "vyfor/cord.nvim",
  opts = {
    enabled = true,
    log_level = vim.log.levels.OFF,
    editor = {
      client = "neovim",
      tooltip = "hiiiiii",
    },

    display = {
      theme = "atom",
      flavor = "dark",
      view = "full",
      swap_fields = false,
      swap_icons = false,
    },
    timestamp = {
      enabled = false,
    },
    idle = {
      enabled = true,
      timeout = 300000,
      show_status = true,
      ignore_focus = true,
      unidle_on_focus = true,
      smart_idle = true,
      details = "sleeping...",
      state = "wake me up",
      tooltip = "💤",
    },

    text = {
      default = "neoviming",

      workspace = function(opts)
        return opts.workspace and (opts.workspace .. " gp in malaysia™") or "working..."
      end,

      viewing = function(opts)
        return "staring at " .. opts.filename
      end,

      editing = function(opts)
        return "changing " .. opts.filename
      end,

      file_browser = function(opts)
        return "looking at " .. opts.name
      end,

      plugin_manager = function(opts)
        return "swapping plugins"
      end,

      lsp = function(opts)
        return "tf is an lsp"
      end,

      docs = function(opts)
        return "researching " .. opts.name
      end,

      vcs = function(opts)
        return "git push origin main --force"
      end,

      notes = function(opts)
        return "what is note"
      end,

      debug = function(opts)
        return "breaking " .. opts.name
      end,

      test = function(opts)
        return "testing " .. opts.name
      end,

      diagnostics = function(opts)
        local count = #vim.diagnostic.get(0)

        if count == 0 then
          return true
        end

        return string.format("fixing %d foolish mistake%s", count, count == 1 and "" or "s")
      end,
      games = function(opts)
        return "playing " .. opts.name
      end,
      terminal = function(opts)
        return "running commands"
      end,
      dashboard = "ok ok i'm here, hey-hey, hey-hey uh-huh",
    },
    buttons = {
      {
        label = function(opts)
          return opts.repo_url and "see my shoddy work" or "github"
        end,

        url = function(opts)
          return opts.repo_url or "https://github.com"
        end,
      },
    },
    assets = {
      [".rs"] = {
        icon = "rust",
        tooltip = "rust, isn't that a game",
      },

      ["lua"] = {
        tooltip = "script kiddie coding language",
      },

      ["python"] = {
        tooltip = "superior in every single way",
      },

      ["javascript"] = {
        tooltip = "oh god",
      },

      ["typescript"] = {
        tooltip = "oh god (slowed + reverb)",
      },

      ["netrw"] = {
        name = "File Explorer",
        type = "file_browser",
      },
    },
    variables = true,
    hooks = {
      workspace_change = function(opts) end,
    },
    advanced = {
      plugin = {
        autocmds = true,
        cursor_update = "on_hold",
        match_in_mappings = true,
        debounce = {
          delay = 50,
          interval = 750,
        },
      },
      server = {
        update = "fetch",
        auto_update = true,
        timeout = 300000,
      },
      discord = {
        reconnect = {
          enabled = true,
          interval = 5000,
          initial = true,
        },
        sync = {
          enabled = false,
        },
      },
      workspace = {
        root_markers = {
          ".git",
          ".hg",
          ".svn",
        },

        limit_to_cwd = false,
      },
    },
  },
}
