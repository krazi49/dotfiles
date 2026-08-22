require("base16-colorscheme").setup({
	base00 = "#151312",
	base01 = "#100e0d",
	base02 = "#1d1b1a",
	base03 = "#4f4540",
	base04 = "#d2c3be",
	base05 = "#e8e1df",
	base06 = "#33302f",
	base07 = "#3c3837",

	base08 = "#c3bc9e",
	base09 = "#cdc7ae",
	base0A = "#d2c3be",
	base0B = "#dcc1b5",
	base0C = "#322f1e",
	base0D = "#3c2b23",
	base0E = "#4f4540",
	base0F = "#bda7a0",
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
	bg = "#3c2b23",
	fg = "#d2b7ab", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#b0a67f",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#9b8e89",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#cdc7ae",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#d2c3be",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#6f5a50",
})
