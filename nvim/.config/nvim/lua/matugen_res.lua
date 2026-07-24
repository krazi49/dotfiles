require("base16-colorscheme").setup({
	base00 = "#181306",
	base01 = "#120e03",
	base02 = "#201b0d",
	base03 = "#4d4635",
	base04 = "#d0c6af",
	base05 = "#ede1ca",
	base06 = "#363020",
	base07 = "#3f3928",

	base08 = "#c1c46f",
	base09 = "#c9cb81",
	base0A = "#d2c78f",
	base0B = "#efc100",
	base0C = "#484a0d",
	base0D = "#574500",
	base0E = "#4e471b",
	base0F = "#c3b56b",
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
	bg = "#574500",
	fg = "#ffe086", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#b2b54b",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#99907c",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#c9cb81",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#d2c78f",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#735c00",
})
