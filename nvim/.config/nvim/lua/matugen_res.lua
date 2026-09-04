require("base16-colorscheme").setup({
	base00 = "#fff8f6",
	base01 = "#ffffff",
	base02 = "#fcf1ee",
	base03 = "#d5c3bb",
	base04 = "#51443e",
	base05 = "#1f1b19",
	base06 = "#f9efeb",
	base07 = "#fff8f6",

	base08 = "#544f2a",
	base09 = "#655f33",
	base0A = "#705a4e",
	base0B = "#7c523b",
	base0C = "#b4ad79",
	base0D = "#986a52",
	base0E = "#fbdcce",
	base0F = "#524239",
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
	bg = "#986a52",
	fg = "#ffffff", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#322f19",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#83746d",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#655f33",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#705a4e",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#f2bb9e",
})
