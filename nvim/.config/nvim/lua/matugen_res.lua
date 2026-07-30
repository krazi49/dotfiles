require("base16-colorscheme").setup({
	base00 = "#171215",
	base01 = "#110d10",
	base02 = "#1f1a1e",
	base03 = "#4f434b",
	base04 = "#d3c2cc",
	base05 = "#ebe0e5",
	base06 = "#352f33",
	base07 = "#3e373b",

	base08 = "#ff9a98",
	base09 = "#ffb3b1",
	base0A = "#e0bcd6",
	base0B = "#f7b0ea",
	base0C = "#d27775",
	base0D = "#bd7bb1",
	base0E = "#593e53",
	base0F = "#d099c1",
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
	bg = "#bd7bb1",
	fg = "#000000", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#ff6865",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#9b8d96",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#ffb3b1",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#e0bcd6",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#85497c",
})
