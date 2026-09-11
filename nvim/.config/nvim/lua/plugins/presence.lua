return {
  {
    "andweeb/presence.nvim",
    event = "VeryLazy",
    config = function()
      require("presence"):setup({
        auto_update = true,
        neovim_image_text = "neovim",
        main_image = "file",
        editing_text = "sending %s to tel avi- i mean saving it",
        viewing_text = "watching %s closely",
        git_commit_text = "sending changes to tel avi- i mean github",
        workspace_text = "doing stuff with %s",
        lower_text = "playing inside %s",
      })
    end,
  },
}
