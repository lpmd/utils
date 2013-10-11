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
syn keyword lpplugcodeMainKw contained global require

syn keyword lpplugcodePlugKw contained file open start end each average cutoff
syn keyword lpplugcodePlugKw contained input output from to sigma epsilon rcut
syn keyword lpplugcodePlugKw contained dt

syn keyword lpplugcodePlCode contained AtomSelection AtomSet RawAtomSet PutTaskValue GetTaskValue
syn keyword lpplugcodePlCode contained BasicCell Buffer NonOrthogonalCell Cell CellTopology Topology
syn keyword lpplugcodePlCode contained Vector VectorFormat Dot Cross RawMatrix MatrixFromHeap
syn keyword lpplugcodePlCode contained ParseIntegerKeyword ParseRealKeyword ParseVectorKeyword
syn keyword lpplugcodePlCode contained ParseStringKeyword ParseTagKeyword ParseBooleanKeyword Deallocate
syn keyword lpplugcodePlCode contained EndWithError ShowWarning NotImplemented InvalidOperation RuntimeError
syn keyword lpplugcodePlCode contained SystemError FileNotFound SyntaxError PluginError InvalidRequest
syn keyword lpplugcodePlCode contained MissingComponent CutoffTooLarge NonOrthogonalCell OrthogonalCell
syn keyword lpplugcodePlCode contained AtomData Region ReturnValue Selector RawTag Tag TaskReturnValue
syn keyword lpplugcodePlCode contained SetValue GetValue Timer Topolgy ToString GenericVector
syn keyword lpplugcodePlCode contained LogMessage GetArrays Get ArraysByName AddAtom
syn keyword lpplugcodePlCode contained GetArray SetArrays LocalSize ExtendedLocalSize 
syn keyword lpplugcodePlCode contained TotalSize GetTotalArray ReturnValue GetNeighborList
syn keyword lpplugcodePlCode contained GetCenterOfMass Rank NumberOfRanks AtomBelongsToRank
syn keyword lpplugcodePlCode contained OrthoDistance GetLocalCell GetCartesian GetFractional
syn keyword lpplugcodePlCode contained Initialize Destroy HasTag SetTag UnsetTag VectorFormat


syn keyword lpplugcodeASetCd contained ASet_LogMessage ASet_GetArrays ASet_Get ArraysByName ASet_AddAtom
syn keyword lpplugcodeASetCd contained ASet_GetArray ASet_SetArrays ASet_LocalSize ASet_ExtendedLocalSize 
syn keyword lpplugcodeASetCd contained ASet_TotalSize ASet_GetTotalArray ASet_ReturnValue ASet_GetNeighborList
syn keyword lpplugcodeASetCd contained ASet_GetCenterOfMass ASet_Rank ASet_NumberOfRanks Cell_AtomBelongsToRank
syn keyword lpplugcodeASetCd contained Cell_OrthoDistance Cell_GetLocalCell Cell_GetCartesian Cell_GetFractional
syn keyword lpplugcodeASetCd contained Matrix_Initialize Matrix_Destroy HasTag SetTag UnsetTag


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
" C highlighting                                             "
"------------------------------------------------------------"

syn include @C syntax/c.vim
syn include @CPP syntax/cpp.vim
syn region Cregion matchgroup=Snip start=/{/ end=/}/ contains=@C,@CPP,lpplugcodePlCode
"hi link Snip SpecialComment

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
  HiLink lpplugcodePlCode      Identifier
  HiLink lpplugcodeDescString  PreProc
  HiLink lpplugcodeNumber      Constant
  HiLink Snip                  SpecialComment
  delcommand HiLink
endif


let b:current_syntax = "lpplugcode"

let &cpo = s:cpo_save
unlet s:cpo_save
