require("base16-colorscheme").setup({
	base00 = "#181212",
	base01 = "#120d0d",
	base02 = "#201a1a",
	base03 = "#534342",
	base04 = "#d8c1c0",
	base05 = "#ede0de",
	base06 = "#362f2e",
	base07 = "#3f3737",

	base08 = "#dfba60",
	base09 = "#e3c375",
	base0A = "#e7bcba",
	base0B = "#ffb3b1",
	base0C = "#bd9f55",
	base0D = "#db8e8c",
	base0E = "#604140",
	base0F = "#da9794",
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
	bg = "#db8e8c",
	fg = "#330609", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#d6a735",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#a08c8b",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#e3c375",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#e7bcba",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#8c4c4b",
})
