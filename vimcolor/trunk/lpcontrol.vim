" Vim syntax file
" Language: LPMD control file code
" Maintainer: GNM <gnm@gnm.cl>
" Filename: *.control
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
" Numerical information for control files                    "
"------------------------------------------------------------"

" Integer with - + or nothing in front
syn match lpcontrolNumber contained '\d\+'
syn match lpcontrolNumber contained '[-+]\d\+'
" Floating point number with decimal no E or e (+,-)
syn match lpcontrolNumber contained '\d\+\.\d*'
syn match lpcontrolNumber contained '[-+]\d\+\.\d*'
" Floating point like number with E and no decimal point (+,-)
syn match lpcontrolNumber contained '[-+]\=\d[[:digit:]]*[eE][\-+]\=\d\+'
syn match lpcontrolNumber contained '\d[[:digit:]]*[eE][\-+]\=\d\+'
" Floating point like number with E and decimal point (+,-)
syn match lpcontrolNumber contained '[-+]\=\d[[:digit:]]*\.\d*[eE][\-+]\=\d\+'
syn match lpcontrolNumber contained '\d[[:digit:]]*\.\d*[eE][\-+]\=\d\+'

"------------------------------------------------------------"
" Keywords control files                                     "
"------------------------------------------------------------"

syn keyword lpcontrolMainKw contained cell input output steps monitor average 
syn keyword lpcontrolMainKw contained prepare cellmanager potential integrator
syn keyword lpcontrolMainKw contained apply property visualize use enduse

syn keyword lpcontrolPlugKw contained file open start end each average cutoff
syn keyword lpcontrolPlugKw contained input output from to sigma epsilon rcut
syn keyword lpcontrolPlugKw contained dt

"------------------------------------------------------------"
" Regions in control files                                   "
"------------------------------------------------------------"

syn region lpcontrolPlugBlock start="use" end="enduse" fold contains=lpcontrolPlugKw,lpcontrolNumber

syn match lpcontrolNoPlug /^[^use]/ contains=lpcontrolMainKw

"------------------------------------------------------------"
" Comments for control files                                 "
"------------------------------------------------------------"

syn keyword lpcontrolTodo contained TODO FIXME XXX NOTE
syn match lpcontrolComment "#.*$" contains=lpcontrolTodo

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
  HiLink lpcontrolTodo        Todo
  HiLink lpcontrolComment     Comment
  HiLink lpcontrolPlugBlock   Statement
  HiLink lpcontrolMainKw      Keyword
  HiLink lpcontrolNoPlug      SpecialChar
  HiLink lpcontrolPlugKw      SpecialChar
  HiLink lpcontrolString      Constant
  HiLink lpcontrolDescString  PreProc
  HiLink lpcontrolNumber      Constant
  delcommand HiLink
endif


let b:current_syntax = "lpcontrol"

let &cpo = s:cpo_save
unlet s:cpo_save
