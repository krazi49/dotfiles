require("base16-colorscheme").setup({
	base00 = "#1a1111",
	base01 = "#140c0c",
	base02 = "#221919",
	base03 = "#554242",
	base04 = "#dbc0bf",
	base05 = "#f0dfde",
	base06 = "#382e2e",
	base07 = "#413736",

	base08 = "#e4be3b",
	base09 = "#e7c551",
	base0A = "#f3b8b7",
	base0B = "#ffb5b4",
	base0C = "#caaa38",
	base0D = "#fa8e8e",
	base0E = "#653b3b",
	base0F = "#ec8d8b",
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
	bg = "#fa8e8e",
	fg = "#4a050d", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#cfa71d",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#a38b8a",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#e7c551",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#f3b8b7",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#9a4244",
})
