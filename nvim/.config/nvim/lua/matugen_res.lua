require("base16-colorscheme").setup({
	base00 = "#f7fafb",
	base01 = "#ffffff",
	base02 = "#f2f4f5",
	base03 = "#bfc8cc",
	base04 = "#3f484c",
	base05 = "#191c1d",
	base06 = "#eff1f2",
	base07 = "#f7fafb",

	base08 = "#654774",
	base09 = "#735184",
	base0A = "#49626b",
	base0B = "#0e677b",
	base0C = "#c19ad2",
	base0D = "#6ab2c8",
	base0E = "#c9e4ee",
	base0F = "#34464d",
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
	bg = "#6ab2c8",
	fg = "#002129", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#4a3455",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#6f797c",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#735184",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#49626b",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#89d1e8",
})
