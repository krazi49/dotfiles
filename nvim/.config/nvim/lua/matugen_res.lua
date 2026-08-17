require("base16-colorscheme").setup({
	base00 = "#181210",
	base01 = "#120d0b",
	base02 = "#201a18",
	base03 = "#52443e",
	base04 = "#d7c2ba",
	base05 = "#ece0dc",
	base06 = "#362f2c",
	base07 = "#3f3835",

	base08 = "#cbc06e",
	base09 = "#d2c881",
	base0A = "#e5beae",
	base0B = "#feb695",
	base0C = "#b6ad68",
	base0D = "#c58466",
	base0E = "#5e4337",
	base0F = "#d99f87",
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
	bg = "#c58466",
	fg = "#000000", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#beaf49",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#9f8d85",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#d2c881",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#e5beae",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#885036",
})
