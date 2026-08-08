require("base16-colorscheme").setup({
	base00 = "#17120f",
	base01 = "#120d0a",
	base02 = "#201b17",
	base03 = "#51443a",
	base04 = "#d5c3b6",
	base05 = "#ebe0da",
	base06 = "#352f2b",
	base07 = "#3e3833",

	base08 = "#bfc372",
	base09 = "#c7cb84",
	base0A = "#e1c0a5",
	base0B = "#f8ba82",
	base0C = "#a3a764",
	base0D = "#d09762",
	base0E = "#5c4430",
	base0F = "#d4a57f",
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
	bg = "#d09762",
	fg = "#271200", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#afb44e",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#9e8e82",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#c7cb84",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#e1c0a5",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#825425",
})
