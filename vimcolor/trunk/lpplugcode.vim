" Vim syntax file
" Language: LPMD plugcode file code
" Maintainer: GNM <gnm@gnm.cl>
" Filename: *.plugcode
" Latest Revision: September 24th 2012

" Initialization
" ==============
" For version 5.x: Clear all syntax items
" For version 6.x: Quit when a syntax file was already loaded
if version < 600
  syntax clear
elseif exists("b:current_syntax")
    finish
endif

let s:cpo_save = &cpo
set cpo&vim

"Ignore case
syn case ignore

"------------------------------------------------------------"
" C highlighting                                             "
"------------------------------------------------------------"

syn include @CPP syntax/c.vim
syn region CPPregion matchgroup=Snip start=/{/ end=/}/ contains=@CPP
"hi link Snip SpecialComment

"------------------------------------------------------------"
" Numerical information for control files                    "
"------------------------------------------------------------"

" Integer with - + or nothing in front
syn match lpplugcodeNumber contained '\d\+'
syn match lpplugcodeNumber contained '[-+]\d\+'
" Floating point number with decimal no E or e (+,-)
syn match lpplugcodeNumber contained '\d\+\.\d*'
syn match lpplugcodeNumber contained '[-+]\d\+\.\d*'
" Floating point like number with E and no decimal point (+,-)
syn match lpplugcodeNumber contained '[-+]\=\d[[:digit:]]*[eE][\-+]\=\d\+'
syn match lpplugcodeNumber contained '\d[[:digit:]]*[eE][\-+]\=\d\+'
" Floating point like number with E and decimal point (+,-)
syn match lpplugcodeNumber contained '[-+]\=\d[[:digit:]]*\.\d*[eE][\-+]\=\d\+'
syn match lpplugcodeNumber contained '\d[[:digit:]]*\.\d*[eE][\-+]\=\d\+'

"------------------------------------------------------------"
" Keywords control files                                     "
"------------------------------------------------------------"

syn keyword lpplugcodeMainKw contained include plugin version author parameter example
syn keyword lpplugcodeMainKw contained slot end test beforetest aftertest function
syn keyword lpplugcodeMainKw contained global

syn keyword lpplugcodePlugKw contained file open start end each average cutoff
syn keyword lpplugcodePlugKw contained input output from to sigma epsilon rcut
syn keyword lpplugcodePlugKw contained dt

"------------------------------------------------------------"
" Regions in control files                                   "
"------------------------------------------------------------"

"syn region lpplugcodePlugBlock start="{" end="}" fold contains=lpplugcodePlugKw,lpplugcodeNumber

syn match lpplugcodeNoPlug /^@\w/ contains=lpplugcodeMainKw
syn match lpplugcodeNoPlug /^[^\s*]@\w/ contains=lpplugcodeMainKw

"------------------------------------------------------------"
" Comments for control files                                 "
"------------------------------------------------------------"

syn keyword lpplugcodeTodo contained TODO FIXME XXX NOTE
syn match lpplugcodeComment "#.*$" contains=lpplugcodeTodo
syn match lpplugcodeComment "//.*$" contains=lpplugcodeTodo

"------------------------------------------------------------"
" Setup syntax highlighting                                  "
"------------------------------------------------------------"

" Define the default highlighting.
" For version 5.7 and earlier: only when not done already
" For version 5.8 and later: only when an item doesn't have highlighting yet
if version >= 508 || !exists("did_bib_syn_inits")
  if version < 508
    let did_bib_syn_inits = 1
    command -nargs=+ HiLink hi link <args>
  else
    command -nargs=+ HiLink hi def link <args>
  endif
  HiLink lpplugcodeTodo        Todo
  HiLink lpplugcodeComment     Comment
  HiLink lpplugcodePlugBlock   Statement
  HiLink lpplugcodeMainKw      Keyword
  HiLink lpplugcodeNoPlug      SpecialChar
  HiLink lpplugcodePlugKw      SpecialChar
  HiLink lpplugcodeString      Constant
  HiLink lpplugcodeDescString  PreProc
  HiLink lpplugcodeNumber      Constant
  HiLink Snip                  SpecialComment
  delcommand HiLink
endif


let b:current_syntax = "lpplugcode"

let &cpo = s:cpo_save
unlet s:cpo_save
