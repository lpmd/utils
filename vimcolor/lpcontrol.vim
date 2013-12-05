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
syn keyword lpcontrolMainKw apply property visualize set filter periodic monitor

syn keyword lpcontrolBlock use enduse

syn keyword lpcontrolInside start end each module symbol nx ny nz file a b c angle

syn keyword lpcontrolPlugin addvelocity angdist angularmomentum atomenergy atomtrail average
syn keyword lpcontrolPlugin beeman berendsen box buckingham
syn keyword lpcontrolPlugin cellscaling centrosymmetry cna cone constantforce cordnum cordnumfunc
syn keyword lpcontrolPlugin crystal2d crystal3d crystal cylinder density densityprofile displace
syn keyword lpcontrolPlugin dlpoly element euler ewald external fastlj finnissinclair finnissinclair-ext
syn keyword lpcontrolPlugin gdr gupta harmonic index lcbinary leapfrog lennardjones lennardjonesMod
syn keyword lpcontrolPlugin linkedcell localpressire lpmd mcy metropolis minimumimage mol2 moleculecm
syn keyword lpcontrolPlugin morse msd nosehoover null osciforce pairdistance pdb pinatoms
syn keyword lpcontrolPlugin printatoms propertycolor quenchedmd random rawbinary replicate rotate
syn keyword lpcontrolPlugin rvcorr setcolor settag setvelocity shear simplebond sitecoord skewstart
syn keyword lpcontrolPlugin sphere suttonchen tabulatedpair tag temperature tempprofile tempscaling test
syn keyword lpcontrolPlugin undopbc vacf varstep vasp veldist velocityverlet verlet verletlist voronoi
syn keyword lpcontrolPlugin xyz
syn keyword lpcontrolPlugin cubic centeratoms fcc

"------------------------------------------------------------"
" Regions in control files                                   "
"------------------------------------------------------------"

"syn match lpcontrolNoPlug /^[^u].*$/ contains=lpcontrolNumber,lpcontrolMainKw,lpcontrolInside
"syn match lpcontrolNoPlug /^*/ contains=lpcontrolNumber,lpcontrolMainKw,lpcontrolInside

"syn match PlugBlock "((\_.\{-}:" contains=lpcontrolPlugKw
"syn region lpcontrolPlugBlock matchgroup=Block start="use" end="enduse" contains=lpcontrolPlugKw
"syn region lpcontrolPlugBlock2 start=/{/ end=/}/ contains=lpcontrolPlugKw 

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
  HiLink lpcontrolPlugin      Identifier
"  HiLink lpcontrolPlugBlock2  Statement
"  HiLink lpcontrolInside      SpecialChar
"  HiLink lpcontrolNoPlug      SpecialChar
"  HiLink lpcontrolString      Constant
"  HiLink lpcontrolDescString  PreProc
  HiLink lpcontrolNumber      Constant
  delcommand HiLink
endif


let b:current_syntax = "lpcontrol"

let &cpo = s:cpo_save
unlet s:cpo_save
