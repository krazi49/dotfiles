require("base16-colorscheme").setup({
	base00 = "#131314",
	base01 = "#0e0e0f",
	base02 = "#1b1b1d",
	base03 = "#45474c",
	base04 = "#c6c6cd",
	base05 = "#e4e2e3",
	base06 = "#303031",
	base07 = "#39393a",

	base08 = "#d1afc5",
	base09 = "#dabfd1",
	base0A = "#c4c6cf",
	base0B = "#bec6db",
	base0C = "#533f4e",
	base0D = "#3d4556",
	base0E = "#464950",
	base0F = "#a8abb8",
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
	bg = "#3d4556",
	fg = "#d5ddf2", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#be8fae",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#8f9097",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#dabfd1",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#c4c6cf",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#565e70",
})
