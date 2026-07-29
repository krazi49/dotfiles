require("base16-colorscheme").setup({
	base00 = "#1b110b",
	base01 = "#160c06",
	base02 = "#241912",
	base03 = "#574336",
	base04 = "#dec1b0",
	base05 = "#f4ded3",
	base06 = "#3a2e26",
	base07 = "#44372f",

	base08 = "#8acb9d",
	base09 = "#9cd3ac",
	base0A = "#b9cda0",
	base0B = "#bac3ff",
	base0C = "#1b5032",
	base0D = "#364280",
	base0E = "#3b4c29",
	base0F = "#a0bb7f",
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
	bg = "#364280",
	fg = "#dee1ff", -- normal text contrast
})

-- Make "string" text contrast better
set_hl_mutliple({ "String", "TSString" }, {
	fg = "#67bb80",
})

-- Grey out comments
set_hl_mutliple({ "TSComment", "Comment" }, {
	fg = "#a58c7c",
	italic = true,
})

-- Color in other highlight groups as you see fit!

set_hl_mutliple({ "TSMethod", "Method" }, {
	fg = "#9cd3ac",
})

set_hl_mutliple({ "TSFunction", "Function" }, {
	fg = "#b9cda0",
})

set_hl_mutliple({ "Keyword", "TSKeyword", "TSKeywordFunction", "TSRepeat" }, {
	fg = "#4e5a9a",
})
