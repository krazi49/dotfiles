require("base16-colorscheme").setup({
	base00 = "#1f0f0d",
	base01 = "#190a08",
	base02 = "#281714",
	base03 = "#5d3f3b",
	base04 = "#e6bdb6",
	base05 = "#fcdbd6",
	base06 = "#3f2b28",
	base07 = "#493431",

	base08 = "#ffae3e",
	base09 = "#ffb957",
	base0A = "#ffb4a8",
	base0B = "#ffb4a8",
	base0C = "#c48319",
	base0D = "#ff5541",
	base0E = "#871f15",
	base0F = "#ff8875",
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
	bg = "#ff5541",
	fg = "#000000", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#ff990b",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#ad8882",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#ffb957",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#ffb4a8",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#bf0603",
})
