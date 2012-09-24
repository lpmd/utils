" Vim syntax file
" Language: LPMD control file code
" Maintainer: GNM <gnm@gnm.cl>
" Latest Revision: September 24th 2012

if exists("b:current_syntax")
  finish
endif

"------------------------------------------------------------"
" Numerical information for control files                    "
"------------------------------------------------------------"

" Integer with - + or nothing in front
syn match lpcontrolNumber '\d\+'
syn match lpcontrolNumber '[-+]\d\+'
" Floating point number with decimal no E or e (+,-)
syn match lpcontrolNumber '\d\+\.\d*'
syn match lpcontrolNumber '[-+]\d\+\.\d*'
" Floating point like number with E and no decimal point (+,-)
syn match lpcontrolNumber '[-+]\=\d[[:digit:]]*[eE][\-+]\=\d\+'
syn match lpcontrolNumber '\d[[:digit:]]*[eE][\-+]\=\d\+'
" Floating point like number with E and decimal point (+,-)
syn match lpcontrolNumber '[-+]\=\d[[:digit:]]*\.\d*[eE][\-+]\=\d\+'
syn match lpcontrolNumber '\d[[:digit:]]*\.\d*[eE][\-+]\=\d\+'

"------------------------------------------------------------"
" Keywords control files                                     "
"------------------------------------------------------------"

syn keyword lpcontrolMainKw cell input output steps monitor average 
syn keyword lpcontrolMainKw prepare cellmanager potential integrator
syn keyword lpcontrolMainkw apply property visualize use enduse

syn keyword lpcontrolPlugkw file open start end each average cutoff
syn keyword lpcontrolPlugkw from to

"------------------------------------------------------------"
" Regions in control files                                   "
"------------------------------------------------------------"

syn region lpcontrolEquaBlock start='"' end=' ' contained
syn region lpcontrolPlugBlock start="use" end="enduse" fold transparent contains=lpcontrolPlugkw

"------------------------------------------------------------"
" Comments for control files                                 "
"------------------------------------------------------------"

syn keyword lpcontrolTodo contained TODO FIXME XXX NOTE
syn match lpcontrolComment "#.*$" contains=lpcontrolTodo

"------------------------------------------------------------"
" Setup syntax highlighting                                  "
"------------------------------------------------------------"

let b:current_syntax = "lpcontrol"

hi def link lpcontrolTodo          Todo
hi def link lpcontrolComment       Comment
hi def link lpcontrolEquaBlock     Statement
hi def link lpcontrolPlugBlock     SpecialChar
hi def link lpcontrolMainKw        Keyword
hi def link lpcontrolString        Constant
hi def link lpcontrolDescString    PreProc
hi def link lpcontrolNumber        Constant
