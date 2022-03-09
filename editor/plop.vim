" Vim syntax file
" Language:         Plop
" Maintainer:       Suirabu <suirabu.dev@gmail.com>
" Latest Revision:  2-22-2022

" Usage:
" Put this file in your `~/.vim/syntax/` directory
" Add the line:
"
"     au BufRead,BufNewFile *.plop set filetype=plop
"
" into your .vimrc

if exists("b:current_syntax")
    finish
endif

syn keyword plopTodo TODO
syn match plopComment "#.*$" contains=plopTodo
syn match plopEscapes display contained "\\[nrt]"
syn region plopString start='"' end='"' contains=plopEscapes
syn keyword plopKeyword exit print println read var const if else while proc
syn match plopNumber "\d+"

hi def link plopTodo Todo
hi def link plopComment Comment
hi def link plopEscapes SpecialChar
hi def link plopString String
hi def link plopKeyword Keyword
hi def link plopNumber Number

let b:current_syntax = "plop"
