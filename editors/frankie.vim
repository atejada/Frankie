" Vim syntax file for Frankie (.fk)
" Language: Frankie
" Maintainer: Claude & Blag Aka. Alvaro Tejada Galindo
" Version: 1.3.0
"
" Installation:
"   Copy to ~/.vim/syntax/frankie.vim
"   Add to ~/.vim/filetype.vim:
"     au BufRead,BufNewFile *.fk set filetype=frankie

if exists("b:current_syntax")
  finish
endif

" Keywords
syn keyword frankieKeyword    def end if elsif else unless while until for in
syn keyword frankieKeyword    do case when begin rescue ensure return next break
syn keyword frankieKeyword    require raise

" Boolean / nil constants
syn keyword frankieBoolean    true false nil

" Logical operators
syn keyword frankieOperator   and or not

" Built-in functions
syn keyword frankieBuiltin    puts print p input input_int input_float
syn keyword frankieBuiltin    to_int to_float to_str length
syn keyword frankieBuiltin    sum mean median stdev variance min max
syn keyword frankieBuiltin    abs sqrt floor ceil clamp seq linspace rep vec
syn keyword frankieBuiltin    paste sprintf
syn keyword frankieBuiltin    matches match match_all sub gsub regex
syn keyword frankieBuiltin    file_read file_write file_append file_lines file_exists file_delete
syn keyword frankieBuiltin    json_parse json_dump json_read json_write
syn keyword frankieBuiltin    csv_parse csv_dump csv_read csv_write
syn keyword frankieBuiltin    now today date_from date_parse
syn keyword frankieBuiltin    http_get http_post http_put http_delete url_encode url_decode
syn keyword frankieBuiltin    db_open exit argv env
syn keyword frankieBuiltin    is_integer is_float is_string is_vector is_nil is_bool

" Strings — double quoted with interpolation
syn region  frankieString     start=+"+  skip=+\\"+  end=+"+  contains=frankieInterp,frankieEscape
syn region  frankieString     start=+'+  skip=+\\'+  end=+'+  contains=frankieEscape
syn region  frankieString     start=+"""+            end=+"""+  contains=frankieInterp,frankieEscape

" String interpolation #{...}
syn region  frankieInterp     contained start=+#{+ end=+}+ contains=ALL

" Escape sequences
syn match   frankieEscape     contained +\\[ntrb\\"']+

" Comments
syn match   frankieComment    "#.*$"

" Numbers
syn match   frankieNumber     "\b\d\+\(\.\d\+\)\?\b"

" Operators
syn match   frankieOp         "|>"
syn match   frankieOp         "\.\.\."
syn match   frankieOp         "\.\."
syn match   frankieOp         "\*\*"
syn match   frankieOp         "//"
syn match   frankieOp         "=~"
syn match   frankieOp         "==\|!=\|<=\|>=\|<\|>"

" Method definitions
syn match   frankieDefName    "\(def \)\@<=\w\+"

" Method calls with ? or !
syn match   frankieMethod     "\.\w\+[?!]\?"

" Assign highlighting
highlight def link frankieKeyword    Keyword
highlight def link frankieBoolean    Boolean
highlight def link frankieOperator   Operator
highlight def link frankieBuiltin    Function
highlight def link frankieString     String
highlight def link frankieInterp     Special
highlight def link frankieEscape     SpecialChar
highlight def link frankieComment    Comment
highlight def link frankieNumber     Number
highlight def link frankieOp         Operator
highlight def link frankieDefName    Function
highlight def link frankieMethod     Identifier

let b:current_syntax = "frankie"
