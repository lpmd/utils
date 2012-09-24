" Vim syntax file
" Language: LPMD plugin code
" Maintainer: GNM <gnm@gnm.cl>
" Latest Revision: September 24th 2012

if exists("b:current_syntax")
  finish
endif

" Integer with - + or nothing in front
syn match lpplugcodeNumber '\d\+'
syn match lpplugcodeNumber '[-+]\d\+'

" Floating point number with decimal no E or e (+,-)
syn match lpplugcodeNumber '\d\+\.\d*'
syn match lpplugcodeNumber '[-+]\d\+\.\d*'

" Floating point like number with E and no decimal point (+,-)
syn match lpplugcodeNumber '[-+]\=\d[[:digit:]]*[eE][\-+]\=\d\+'
syn match lpplugcodeNumber '\d[[:digit:]]*[eE][\-+]\=\d\+'

" Floating point like number with E and decimal point (+,-)
syn match lpplugcodeNumber '[-+]\=\d[[:digit:]]*\.\d*[eE][\-+]\=\d\+'
syn match lpplugcodeNumber '\d[[:digit:]]*\.\d*[eE][\-+]\=\d\+'

"Keywords
syn keyword lpplugcodeLanguageKeywords @plugin @version @author

"Regions
syn region lpplugcodeDescBlock start="@example" end="@end" fold transparent

"Comments
syn keyword lpplugcodeTodo contained TODO FIXME XXX NOTE
syn match lpplugcodeComment "//.*$" contains=plugcodeTodo

"----------------------------------------------------------------------------/
"  Setup syntax highlighting
"----------------------------------------------------------------------------/

let b:current_syntax = "plugcode"

hi def link lpplugcodeTodo          Todo
hi def link lpplugcodeComment       Comment
hi def link lpplugcodeStarBlockCmd  Statement
hi def link lpplugcodeMainKw        Keyword
hi def link lpplugcodeMainInnerKw   Special
hi def link lpplugcodeEllOrbitCmd   Statement
hi def link lpplugcodeHIPNumber     Type
hi def link lpplugcodeString        Constant
hi def link lpplugcodeDescString    PreProc
hi def link lpplugcodeNumber        Constant
