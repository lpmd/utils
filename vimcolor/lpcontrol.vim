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
syn match lpcontrolNumber  '\d\+'
syn match lpcontrolNumber  '[-+]\d\+'
" Floating point number with decimal no E or e (+,-)
syn match lpcontrolNumber  '\d\+\.\d*'
syn match lpcontrolNumber  '[-+]\d\+\.\d*'
" Floating point like number with E and no decimal point (+,-)
syn match lpcontrolNumber  '[-+]\=\d[[:digit:]]*[eE][\-+]\=\d\+'
syn match lpcontrolNumber  '\d[[:digit:]]*[eE][\-+]\=\d\+'
" Floating point like number with E and decimal point (+,-)
syn match lpcontrolNumber  '[-+]\=\d[[:digit:]]*\.\d*[eE][\-+]\=\d\+'
syn match lpcontrolNumber  '\d[[:digit:]]*\.\d*[eE][\-+]\=\d\+'

"------------------------------------------------------------"
" Keywords control files                                     "
"------------------------------------------------------------"

syn keyword lpcontrolMainKw  cell input output steps monitor average 
syn keyword lpcontrolMainKw  prepare cellmanager potential integrator as
syn keyword lpcontrolMainKw  apply property visualize set filter periodic monitor

syn keyword lpcontrolInside  start end each module symbol nx ny nz file a b c angle
syn keyword lpcontrolInside  step total-energy temperature potential-energy kinetic-energy
syn keyword lpcontrolInside  pressure interval

syn keyword lpcontrolPlugin  contained addvelocity angdist angularmomentum atomenergy atomtrail average
syn keyword lpcontrolPlugin  contained beeman berendsen box buckingham
syn keyword lpcontrolPlugin  contained cellscaling centrosymmetry cna cone constantforce cordnum cordnumfunc
syn keyword lpcontrolPlugin  contained crystal2d crystal3d crystal cylinder density densityprofile displace
syn keyword lpcontrolPlugin  contained dlpoly element euler ewald external fastlj finnissinclair finnissinclair-ext
syn keyword lpcontrolPlugin  contained gdr gupta harmonic index lcbinary leapfrog lennardjones lennardjonesMod
syn keyword lpcontrolPlugin  contained linkedcell localpressire lpmd mcy metropolis minimumimage mol2 moleculecm
syn keyword lpcontrolPlugin  contained morse msd nosehoover null osciforce pairdistance pdb pinatoms
syn keyword lpcontrolPlugin  contained printatoms propertycolor quenchedmd random rawbinary replicate rotate
syn keyword lpcontrolPlugin  contained rvcorr setcolor settag setvelocity shear simplebond sitecoord skewstart
syn keyword lpcontrolPlugin  contained sphere suttonchen tabulatedpair tag temperature tempprofile tempscaling test
syn keyword lpcontrolPlugin  contained undopbc vacf varstep vasp veldist velocityverlet verlet verletlist voronoi
syn keyword lpcontrolPlugin  contained xyz
syn keyword lpcontrolPlugin  contained cubic centeratoms fcc

"------------------------------------------------------------"
" Regions in control files                                   "
"------------------------------------------------------------"

"syn match lpcontrolNoPlug /^[^u].*$/ contains=lpcontrolNumber,lpcontrolMainKw,lpcontrolInside
"syn match lpcontrolNoPlug /^*/ contains=lpcontrolNumber,lpcontrolMainKw,lpcontrolInside

"syn match PlugBlock "((\_.\{-}:" contains=lpcontrolPlugKw
"syn region lpcontrolPlugBlock matchgroup=Block start="use" end="enduse" contains=lpcontrolPlugKw
"syn region lpcontrolPlugBlock2 start=/{/ end=/}/ contains=lpcontrolPlugKw 

"------------------------------------------------------------"
" PLUGINS highlighting                                       "
"------------------------------------------------------------"

syn include @PLUGIN syntax/lpplugin.vim
syn region Plugregion matchgroup=Snip start="use" end="enduse" contains=@PLUGIN,lpcontrolPlugin,lpcontrolMainKw
"hi link Snip PreProc


"------------------------------------------------------------"
" Comments for control files                                 "
"------------------------------------------------------------"

syn keyword lpcontrolTodo contained TODO FIXME XXX NOTE
syn match lpcontrolComment "#.*$" contains=lpcontrolTodo
"syn match lpcontrolLine '*.*$' contains=lpcontrolPlugin
"syn cluster RegLine contains=lpcontrolMainKw,lpcontrolPlugin

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
  HiLink lpcontrolInside      SpecialComment
  HiLink lpcontrolNumber      Constant
  HiLink Snip PreProc
  delcommand HiLink
endif


let b:current_syntax = "lpcontrol"

let &cpo = s:cpo_save
unlet s:cpo_save
