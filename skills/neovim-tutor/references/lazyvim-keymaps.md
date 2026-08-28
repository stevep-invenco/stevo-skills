# LazyVim keymaps + this user's customizations

Leader = `Space`. This is the user's actual setup: stock LazyVim defaults plus
the personal overrides in the last section. When in doubt about a custom key,
the live source of truth is which-key (press `<leader>` and wait) or
`<leader>sk` (search keymaps); the live config is under `~/.config/nvim/`.

These are LazyVim defaults as of Neovim 0.12 / current LazyVim. If a key seems
off, verify in-editor rather than trust this sheet blindly.

## Contents
- Core motions & editing (vanilla)
- Text objects
- Files / search / pickers
- Buffers & windows
- LSP / code
- Diagnostics & Trouble
- Git
- Flash (motion plugin)
- Toggles (UI)
- Sessions / misc
- This user's customizations

## Core motions & editing (vanilla Vim - portable everywhere)
- `h j k l` - left/down/up/right
- `w` / `b` / `e` - next word start / prev word start / word end; `W B E` = WORD (whitespace-delimited)
- `0` / `^` / `$` - line start / first non-blank / line end
- `gg` / `G` - top / bottom of file; `{count}G` or `:{count}` - go to line
- `f{c}` / `t{c}` - jump to / before next char on line; `;` `,` repeat fwd/back; `F` `T` backward
- `{` `}` - prev/next paragraph; `(` `)` - sentence; `%` - matching bracket
- `Ctrl-d` / `Ctrl-u` - half page down/up; `Ctrl-f` / `Ctrl-b` - full page; `zz` center cursor
- `*` / `#` - search word under cursor fwd/back; `n` `N` repeat search
- `d` `c` `y` - delete / change / yank operators (combine with motion: `dw`, `ci(`, `y$`)
- `dd` `yy` `cc` - whole line; `D` `C` `Y` - to end of line
- `x` `r{c}` `s` - delete char / replace char / substitute char
- `p` `P` - paste after / before; `o` `O` - open line below / above
- `u` / `Ctrl-r` - undo / redo; `.` - repeat last change
- `>>` `<<` - indent / dedent line; `==` - auto-indent
- `~` `gu{motion}` `gU{motion}` - toggle / lower / upper case
- `v` `V` `Ctrl-v` - visual char / line / block; `gv` - reselect last
- `qa` ... `q` then `@a` - record macro to reg a / replay; `@@` replay last
- `m{a}` / `` `{a} `` - set mark a / jump to it; `Ctrl-o` `Ctrl-i` - jump list back/fwd
- `"{r}y` - yank to register r; `"0p` - paste yank register; `"+y` - yank to system clipboard

## Text objects (use with operators or visual: `di(`, `ci"`, `vat`, `yip`)
- `iw` / `aw` - inner / a word; `iW` `aW` - WORD
- `i(` `i)` `ib` - inside parens; `a(` includes parens; same for `{` `}` `B`, `[` `]`, `<` `>`
- `i"` `i'` `` i` `` - inside quotes; `a"` includes quotes
- `it` / `at` - inside / around HTML/XML tag
- `ip` / `ap` - inner / a paragraph
- mini.ai extends these: `ia` `aa` - argument; `if` `af` - function; `ic` `ac` - class; `{count}` and next/last via `in(`, `il(`

## Files / search / pickers (snacks.nvim picker)
- `<leader><space>` - find files (project root) **most-used**
- `<leader>ff` - find files (root); `<leader>fF` - find files (cwd)
- `<leader>fr` - recent files; `<leader>fb` - buffers; `<leader>fp` - projects
- `<leader>fc` - find config file
- `<leader>/` or `<leader>sg` - live grep (root); `<leader>sG` - grep (cwd)
- `<leader>sw` - grep word/selection under cursor
- `<leader>sb` - search lines in current buffer; `<leader>ss` - document symbols
- `<leader>sk` - keymaps; `<leader>sh` - help pages; `<leader>sH` - highlights
- `<leader>sd` - diagnostics; `<leader>sm` - marks; `<leader>sR` - resume last picker
- `<leader>:` - command history; `<leader>,` - switch buffer
- `<leader>e` - file explorer (root); `<leader>E` - explorer (cwd)
- `<leader>n` - notification history
- inside a picker: `<c-j>/<c-k>` move, `<c-t>` open in new tab, `<c-s>` split, `<c-v>` vsplit, `<c-q>` send to quickfix

## Buffers & windows
- `<S-h>` / `<S-l>` - prev / next buffer; `[b` `]b` same
- `<leader>bd` - delete buffer; `<leader>bo` - delete other buffers; `<leader>bp` - toggle pin; `<leader>bP` - delete non-pinned
- `<leader>`` ` - switch to other (alternate) buffer
- `<C-h/j/k/l>` - move to window left/down/up/right
- `<leader>-` - split below; `<leader>|` - split right; `<leader>wd` - delete window; `<leader>wm` - maximize toggle
- `<C-Up/Down/Left/Right>` - resize window
- `<leader><tab>` group - tabs: `<leader><tab><tab>` new, `<leader><tab>d` close, `[ ]` cycle

## LSP / code
- `gd` - definition; `gr` - references; `gI` - implementation; `gy` - type definition; `gD` - declaration
- `K` - hover docs; `gK` - signature help; `<c-k>` (insert) - signature help
- `<leader>ca` - code action; `<leader>cr` - rename symbol; `<leader>cR` - rename file
- `<leader>cf` - format buffer (conform.nvim); `<leader>cd` - line diagnostics
- `<leader>cc` - run codelens; `<leader>cl` - LSP info; `<leader>cM` - Mason
- `]]` / `[[` - next / prev reference; `gco` `gcO` - add comment below/above; `gcc` - toggle line comment; `gc{motion}` - comment motion
- completion (blink.cmp): `<c-y>`/`<cr>` accept, `<c-n>/<c-p>` or `<tab>/<s-tab>` next/prev, `<c-e>` cancel, `<c-space>` open

## Diagnostics & Trouble
- `]d` / `[d` - next / prev diagnostic; `]e` `[e` - error; `]w` `[w` - warning
- `<leader>cd` - line diagnostics float
- `<leader>xx` - diagnostics (Trouble); `<leader>xX` - buffer diagnostics
- `<leader>xL` - location list; `<leader>xQ` - quickfix list
- `<leader>cs` - symbols (Trouble); `<leader>cS` - LSP references/defs (Trouble)
- `<leader>xt` - todo (todo-comments); `]t` `[t` - next/prev todo comment

## Git
- `<leader>gg` - lazygit (root dir); `<leader>gG` - lazygit (cwd)
- `<leader>gb` - git blame line; `<leader>gB` - git browse (open in browser); `<leader>gf` - current file history; `<leader>gl` - git log
- gitsigns hunks: `]h` `[h` - next/prev hunk; `<leader>ghs` stage, `<leader>ghr` reset, `<leader>ghp` preview, `<leader>ghb` blame line, `<leader>ghu` undo stage, `<leader>ghd` diff this

## Flash (motion plugin - fast jumping)
- `s` - flash jump: type label to leap anywhere on screen (normal/visual/operator)
- `S` - flash treesitter: select expanding syntax nodes
- `r` (operator-pending) - remote flash; `R` - treesitter search
- enhances `f` `t` `F` `T` with multi-line + labels; `;`/`,` still repeat
- inside `/` search: `<c-s>` toggle flash search

## Toggles (UI) - `<leader>u` group
- `<leader>uw` - wrap; `<leader>us` - spelling; `<leader>ul` - line numbers; `<leader>uL` - relative numbers
- `<leader>ud` - diagnostics; `<leader>uh` - inlay hints; `<leader>uc` - conceal
- `<leader>ub` - background dark/light; `<leader>uC` - pick colorscheme
- `<leader>un` - dismiss notifications; `<leader>ur` - redraw / clear hlsearch & diff
- `<leader>uT` - toggle treesitter highlight; `<leader>ug` - indent guides

## Sessions / misc
- `<leader>qq` - quit all; `<leader>qs` - restore session; `<leader>ql` - restore last session; `<leader>qd` - don't save current session
- `<leader>l` - Lazy (plugin manager); `<leader>L` - LazyVim changelog
- `<C-/>` - toggle terminal (root); `<leader>ft` - terminal (root), `<leader>fT` - terminal (cwd)
- `<leader>?` - buffer-local keymaps (which-key); press `<leader>` and wait to browse all
- `<esc>` - clear search highlight
- `<leader>ui` - inspect highlight under cursor; `<leader>uI` - inspect treesitter tree

## This user's customizations (from ~/.config/nvim)
Personal keymaps (`lua/config/keymaps.lua`):
- `<leader>cy` - copy current file's **full absolute path** to system clipboard
- `<leader>cY` - copy current file's path **relative to cwd**

octo.nvim - GitHub PRs/issues inside Neovim (`lua/plugins/git.lua`):
- `<leader>gp` - list PRs; `<leader>gi` - list issues
- default merge method is squash; runs `:Octo` commands

diffview.nvim - side-by-side diffs / file tree (`lua/plugins/diffview.lua`):
- `<leader>gv` - open Diffview; `<leader>gV` - close Diffview
- also powers octo.nvim's PR review diffs

snacks picker (`lua/plugins/snacks.lua`):
- explorer and file pickers show **hidden + git-ignored files** by default
  (so `.env` and friends are visible) - no keybinding, just behavior to know

Notable plugins in the stack (for context when answering): flash, telescope +
snacks pickers, which-key, trouble, conform, nvim-lint, treesitter (+textobjects,
autotag), mini.ai / mini.pairs / mini.icons, blink.cmp, noice, bufferline,
lualine, gitsigns, grug-far (search/replace: `<leader>sr`), persistence,
render-markdown + markdown-preview, todo-comments, catppuccin/tokyonight themes.
