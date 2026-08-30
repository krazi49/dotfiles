require("base16-colorscheme").setup({
	base00 = "#10131a",
	base01 = "#0b0e15",
	base02 = "#191b22",
	base03 = "#424753",
	base04 = "#c2c6d6",
	base05 = "#e1e2ec",
	base06 = "#2e3038",
	base07 = "#363941",

	base08 = "#99b5f7",
	base09 = "#b1c6f9",
	base0A = "#e7b9d6",
	base0B = "#afd282",
	base0C = "#304671",
	base0D = "#334e0d",
	base0E = "#5e3c53",
	base0F = "#da93c0",
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
	bg = "#334e0d",
	fg = "#cbee9b", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#6a92f4",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#8c909f",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#b1c6f9",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#e7b9d6",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#4a6724",
})
