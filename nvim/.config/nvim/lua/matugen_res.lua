require("base16-colorscheme").setup({
	base00 = "#1a120e",
	base01 = "#140c09",
	base02 = "#221a16",
	base03 = "#55433b",
	base04 = "#dbc1b7",
	base05 = "#f0dfd9",
	base06 = "#382e2a",
	base07 = "#413733",

	base08 = "#c8c547",
	base09 = "#cecb5b",
	base0A = "#f3baa2",
	base0B = "#ffb596",
	base0C = "#aba93d",
	base0D = "#ee8b5e",
	base0E = "#673f2d",
	base0F = "#ed9875",
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
	bg = "#ee8b5e",
	fg = "#330e00", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#aaa733",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#a38c83",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#cecb5b",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#f3baa2",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#974720",
})
