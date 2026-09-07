require("base16-colorscheme").setup({
	base00 = "#131313",
	base01 = "#0e0e0e",
	base02 = "#1c1b1c",
	base03 = "#45474a",
	base04 = "#c5c6ca",
	base05 = "#e5e2e1",
	base06 = "#313030",
	base07 = "#3a3939",

	base08 = "#c0b6be",
	base09 = "#ccc4ca",
	base0A = "#c7c6c8",
	base0B = "#c5c6cb",
	base0C = "#110e12",
	base0D = "#0c0f12",
	base0E = "#48494a",
	base0F = "#aeacaf",
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
	bg = "#0c0f12",
	fg = "#9b9da1", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#a99ba5",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#8f9194",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#ccc4ca",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#c7c6c8",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#5c5f62",
})
