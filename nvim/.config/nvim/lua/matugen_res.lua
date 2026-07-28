require("base16-colorscheme").setup({
	base00 = "#111411",
	base01 = "#0c0f0b",
	base02 = "#191c19",
	base03 = "#414940",
	base04 = "#c1c9bd",
	base05 = "#e1e3dd",
	base06 = "#2e312d",
	base07 = "#373a36",

	base08 = "#70cae4",
	base09 = "#85d2e8",
	base0A = "#b6cdb2",
	base0B = "#9dd49d",
	base0C = "#4c9bb0",
	base0D = "#699d6b",
	base0E = "#384c38",
	base0F = "#99b993",
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
	bg = "#699d6b",
	fg = "#000000", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#45badc",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#8b9388",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#85d2e8",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#b6cdb2",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#37693c",
})
