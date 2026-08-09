require("base16-colorscheme").setup({
	base00 = "#171309",
	base01 = "#110e05",
	base02 = "#1f1b10",
	base03 = "#4e4632",
	base04 = "#d1c6ab",
	base05 = "#ebe2d0",
	base06 = "#353024",
	base07 = "#3e392c",

	base08 = "#d2fa4c",
	base09 = "#d8fb65",
	base0A = "#dec47a",
	base0B = "#ffebb8",
	base0C = "#bcde4b",
	base0D = "#fbcb02",
	base0E = "#594707",
	base0F = "#d4b251",
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
	bg = "#fbcb02",
	fg = "#4b3b00", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#c5f91a",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#9a9078",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#d8fb65",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#dec47a",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#735c00",
})
