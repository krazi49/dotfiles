require("base16-colorscheme").setup({
	base00 = "#141314",
	base01 = "#0f0e0f",
	base02 = "#1c1b1c",
	base03 = "#4a454a",
	base04 = "#ccc4ca",
	base05 = "#e6e1e2",
	base06 = "#323031",
	base07 = "#3a3939",

	base08 = "#cfb1b4",
	base09 = "#d9c1c3",
	base0A = "#ccc4ca",
	base0B = "#cfc3cf",
	base0C = "#2a1c1e",
	base0D = "#241d26",
	base0E = "#4a454a",
	base0F = "#b4a9b1",
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
	bg = "#241d26",
	fg = "#b2a7b3", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#bc9295",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#968f94",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#d9c1c3",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#ccc4ca",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#655b66",
})
