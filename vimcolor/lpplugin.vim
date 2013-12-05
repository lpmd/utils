" Vim syntax file
" Language: LPMD control plugin embedded settings
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

syn keyword lpcontrolPlugKw file open start end each average cutoff a b c
syn keyword lpcontrolPlugKw input output from to sigma epsilon rcut
syn keyword lpcontrolPlugKw dt axis bins range module nx ny nz key
syn keyword lpcontrolPlugKw value tag velocity color mode quality properties paused
syn keyword lpcontrolPlugKw azimuth zenith

"------------------------------------------------------------"
" Regions in control files                                   "
"------------------------------------------------------------"

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
  HiLink lpcontrolPlugKw      SpecialChar
  HiLink lpcontrolNumber      Constant
  delcommand HiLink
endif


let b:current_syntax = "lpplugin"

let &cpo = s:cpo_save
unlet s:cpo_save
