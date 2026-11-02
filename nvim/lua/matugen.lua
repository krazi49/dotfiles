require("base16-colorscheme").setup({
	base00 = "#141314",
	base01 = "#0e0e0f",
	base02 = "#1c1b1c",
	base03 = "#46464b",
	base04 = "#c7c5cc",
	base05 = "#e5e2e2",
	base06 = "#313031",
	base07 = "#3a393a",

	base08 = "#cbb3bf",
	base09 = "#d5c2cc",
	base0A = "#c7c5cb",
	base0B = "#c7c6d4",
	base0C = "#b9a7b1",
	base0D = "#ababb8",
	base0E = "#46464b",
	base0F = "#adaab3",
})

-- We first theme base16, but we also need to fix some other colors that don't
-- contrast well by default

-- Helper function to set multiple highlight groups at once
local function set_hl_mutliple(groups, value)
	for _, v in pairs(groups) do
		vim.api.nvim_set_hl(0, v, value)
	end
end

-- Make selected text stand out more
vim.api.nvim_set_hl(0, "Visual", {
	bg = "#ababb8",
	fg = "#1f212b", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#b695a6",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#919096",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#d5c2cc",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#c7c5cb",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#5d5e69",
})
