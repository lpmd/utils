#!/usr/bin/env python3

import os.path, os, sys
from copy import deepcopy

#
# Syntax and definitions
#
defaultPrefix = '/usr/local'
defaultInstall = 'install'
pythonlib = [x for x in sys.path if 'python%d.%d' % (sys.version_info[0:2]) in x and 'pymodules' not in x][0]

defaultLanguages = ['c', 'c++', 'd', 'python', 'lpunit', 'plugcode']

compiledLanguages = ['c', 'c++', 'd', 'lpunit', 'plugcode']

headerExtensions = { 'c': ('h',) , 'c++': ('h', 'hpp'), 'd': (), 'lpunit': ('h', 'hpp'), 'plugcode': () }

languageCompilation = { 'c++': '%(compiler)s %(compilerflags)s -c %(source)s -o %(object)s',
                        'c': '%(compiler)s %(compilerflags)s -c %(source)s -o %(object)s',
                        'd': '%(compiler)s %(compilerflags)s -c %(source)s -o %(object)s',
                        'lpunit': '%(compiler)s %(source)s - | %(cpp_compiler)s %(compilerflags)s -x c++ -c -o %(object)s -',
                        'plugcode': '%(compiler)s %(source)s - | %(c_compiler)s %(compilerflags)s -x c -c -o %(object)s -' }

languageStaticLibraryPacking  = { 'c++': 'ar rcs %(target)s %(object)s',
                                  'c': 'ar rcs %(target)s %(object)s',
                                  'd': 'ar rcs %(target)s %(object)s',
                                  'lpunit': 'ar rcs %(target)s %(object)s' }

openmpFlags = None
languageLinking = None
defaultCompiler = None
defaultLinker = None 
libraryNamePattern = None
librarySemiNamePattern = None
libraryExtensions = None
librarySharedFlags = None
librarySharedLinkerFlags = None 
moduleSharedFlags = None 
moduleSharedLinkerFlags = None 

languageFields =  ['flags', 'libraries', 'compiler', 'linker', 'openmpflags']
targetFields = ['test', 'language', 'sources', 'headers', 'installpath', 'pkgconfig', 'expand', 'version', 'openmp'] + languageFields
targetKinds = ['binary', 'script', 'library', 'staticlibrary', 'headers', 'module', 'file']
globaltags = ['name', 'fullname', 'version', 'author', 'prefix', 'openmp', 'mainfirst']
blocktags = ['language', 'directory'] + targetKinds
commontags = ['openmp']
reserved_keywords = [x for x in (blocktags + targetFields + targetKinds) if x not in commontags]

#
# Auxiliary functions
#
def ignorable(x): return x.strip() == '' or x.strip().startswith('#')

def removequotes(x):
    if x.startswith('\"'): return x.strip('\"')
    if x.startswith('\''): return x.strip('\'')
    return x

def appendunique(li, item):
    if item not in li: li.append(item)

def uniquelist(li):
    tmp = []
    for x in li: appendunique(tmp, x)
    return tmp

def anyof(seq, func):
    for x in seq:
        if func(x): return True
    return False

def ObjectFromSource(s): 
    for ext in libraryExtensions:
        if s.endswith('.'+ext): return s
    return s.replace(os.path.splitext(s)[1], '.o')

def FileExtension(path): return path.split('.')[-1]

def ReplaceExtension(path, ext):
    e = FileExtension(path)
    return path.replace('.'+e, '.'+ext)

def OutputFromCommand(cmd): return os.popen(cmd+' 2>/dev/null', 'r').read().strip()

#
#
#
class UnknownLanguage(Exception):
    def __init__(self, lang): self.lang = lang
    def __repr__(self): return '[Error] Unknown language, %s' % self.lang
    def __str__(self): return repr(self)

class MissingComponent(Exception):
    def __init__(self, comptype, name): self.comptype, self.name = comptype, name
    def __repr__(self): return '[Error] Missing %s, %s' % (self.comptype, self.name)
    def __str__(self): return repr(self)

class UnknownPlatform(Exception):
    def __init__(self, plat): self.plat = plat
    def __repr__(self): return '[Error] Unknown platform, %s' % self.plat
    def __str__(self): return repr(self)

class SyntaxError(Exception):
    def __init__(self, msg): self.msg = msg
    def __repr__(self): return '[Error] %s' % self.msg
    def __str__(self): return repr(self)

#
#
#
class Block(dict):

    def __init__(self, header):
        self.header = header

class Item:

    def __init__(self, name, fields, kwargs):
        self.name = name
        self.fields = fields
        for k in self.fields:
            if k in kwargs: setattr(self, k, kwargs[k])

class Language(Item):

    def __init__(self, name, setup, **kwargs):
        self.name, self.setup = name, setup
        if self.IsCompiled(): 
           self.compiler = defaultCompiler[name]
           self.libraries = ''
           self.flags = ''
        Item.__init__(self, name, languageFields, kwargs)
        if self.IsCompiled() and not hasattr(self, 'linker'): 
           self.linker = defaultLinker[name]

    def Update(self, d):
        for k in self.fields:
            if k in d: setattr(self, k, d[k])

    def IncludeDirectories(self, flags):
        incdirs = []
        for token in flags.split():
            if token.startswith('-I'):
               if token[2:] not in incdirs: incdirs.append(token[2:])
        return incdirs

    def SourcesIncludedIn(self, filename, includedirs):
        inc = []
        for line in open(filename, 'r'):
            line = line.strip()
            if line.startswith('#include'):
               remainder = line[8:].strip()
               if remainder.startswith('\"') and remainder.endswith('\"'):
                  includedname = remainder[1:-1]
                  if includedname not in inc: inc.append(includedname)
               elif remainder.startswith('<') and remainder.endswith('>'):
                  includedname = remainder[1:-1]
                  if includedname not in inc: 
                     for d in includedirs: 
                         if os.path.exists(os.path.join(d, includedname)): inc.append(os.path.join(d, includedname))
               else: assert False
        return inc
 
    def IsCompiled(self): return (self.name in compiledLanguages)

    def IsFileCompilable(self, name):
        if not self.IsCompiled(): return False
        for x in headerExtensions[self.name]:
            if name.lower().endswith('.'+x): return False
        return True

    def SupportsOpenMP(self): 
        return hasattr(self, 'openmpflags') and (self.openmpflags != '' or self.openmplibraries != '')

    def Apply(self, pattern, target, sources=[], objects=[]):
        if not self.IsCompiled(): return None
        compilableSources = [x for x in sources if self.IsFileCompilable(x)]
        installname = target.name
        if hasattr(target, 'installname') and target.installname != '': installname = target.installname
        return pattern % {'target': installname, 'cpp_compiler': self.setup.language['c++'].compiler, 
                          'c_compiler': self.setup.language['c'].compiler,
                          'compiler': self.setup.actualpath[target.compiler] if target.compiler in self.setup.actualpath else target.compiler, 
                          'linkflags': target.libraries, 'compilerflags': target.flags, 'linker': target.linker, 
                          'source': ' '.join(compilableSources), 'prefix': target.setup.prefix, 'object': ' '.join(objects)}

class Target(Item):

    def __init__(self, setup, directory, targettype, name, **kwargs):
        if targettype == 'staticlibrary': name += ('.'+libraryExtensions[0])
        elif targettype == 'library': name += ('.'+libraryExtensions[1])
        Item.__init__(self, name, targetFields, kwargs)
        self.setup = setup
        self.targettype = targettype
        if self.targettype in ('binary', 'script'):
           if not hasattr(self, 'test'): self.test = False
           else: self.test = (str(self.test).lower() == 'true')
        self.sources = [x.strip() for x in self.sources.split()]
        if hasattr(self, 'language'): 
           self.language = setup.language[self.language]
           if not hasattr(self, 'flags') and hasattr(self.language, 'flags'):
              self.flags = self.language.flags
              if self.targettype == 'library': self.flags += librarySharedFlags
              elif self.targettype == 'module': self.flags += moduleSharedFlags
           if not hasattr(self, 'libraries') and hasattr(self.language, 'libraries'):
              self.libraries = self.language.libraries
              if self.targettype == 'library': 
                 if not hasattr(self, 'version'): self.version = '1.0.0'
                 self.major, self.minor, self.revision = [int(z) for z in self.version.split('.')]
                 namesplit = name.split('.')
                 if len(namesplit) > 2: raise SyntaxError('A library or sharedlibrary name should not include any extension')
                 base_name, extension = name.split('.')
                 self.installname = libraryNamePattern % {'name': base_name, 'extension': extension, 'major': int(self.major), 'minor': int(self.minor), 'revision': int(self.revision)}
                 self.semiinstallname = librarySemiNamePattern % {'name': base_name, 'extension': extension, 'major': int(self.major), 'minor': int(self.minor), 'revision': int(self.revision)}
                 self.libraries += (librarySharedLinkerFlags % {'shortname': name, 'major': int(self.major), 'minor': int(self.minor), 'output': self.installname})
              elif self.targettype == 'module': self.libraries += moduleSharedLinkerFlags
           if not hasattr(self, 'compiler') and hasattr(self.language, 'compiler'):
              self.compiler = self.language.compiler
           if not hasattr(self, 'linker') and hasattr(self.language, 'linker'):
              self.linker = self.language.linker
        if not hasattr(self, 'pkgconfig'): self.pkgconfig = ''
        if '+(flags)' in kwargs: 
           self.flags += (' '+kwargs['+(flags)']) 
           self.flags = self.flags.strip()
        if '+(libraries)' in kwargs: 
           self.libraries += (' '+kwargs['+(libraries)']) 
           self.libraries = self.libraries.strip()
        if '+(pkgconfig)' in kwargs:
           self.pkgconfig += (' '+kwargs['+(pkgconfig)'])
           self.pkgconfig = self.pkgconfig.strip()
        if hasattr(self, 'installpath') and not self.installpath.startswith('/'):
           self.installpath = os.path.join(setup.prefix, self.installpath)
        # Expands pkgconfig into flags and libraries
        for pc in self.pkgconfig.split(): 
            os.environ['PKG_CONFIG_PATH'] = os.path.join(setup.prefix, 'lib/pkgconfig')+':'+os.getenv('PKG_CONFIG_PATH', '')
            self.flags += (' '+OutputFromCommand('pkg-config --cflags %s' % pc)+' ')
            self.libraries += (' '+OutputFromCommand('pkg-config --libs %s' % pc)+' ')
            self.flags = self.flags.strip()
            self.libraries = self.libraries.strip()
        # Once the flags are expanded, we can search for included sources
        if hasattr(self, 'language') and self.language.name in compiledLanguages:
           incdirs = []
           self.sourcesfrom = {}
           if hasattr(self, 'flags'): incdirs = self.language.IncludeDirectories(self.flags)
           newsources = []
           for x in self.sources:
               if x.endswith('.a') or x.endswith('.so'): continue
               if x not in self.sourcesfrom: self.sourcesfrom[x] = []
               for y in self.language.SourcesIncludedIn(os.path.join(directory.name, x), incdirs):
                   if y not in newsources: newsources.append(y)
                   if y not in self.sourcesfrom[x]: self.sourcesfrom[x].append(y)
           self.sources += newsources

class Makefile:

    def __init__(self):
        self.code = ""
        self.variables, self.values = [], { }
        self.targets, self.phonytargets = [], []

    def AddVariable(self, varname, value):
        self.variables.append(varname)
        self.values[varname] = value

    def AddTarget(self, targetname, dependencies, rules):
        if type(rules) != list: rules = [ rules ]
        self.targets.append((targetname, dependencies, rules))

    def AddPhonyTarget(self, targetname, dependencies, rules):
        self.phonytargets.append(targetname)
        self.AddTarget(targetname, dependencies, rules)

    def Render(self):
        for var in self.variables:
            self.code += ('%s=%s\n\n' % (var, self.values[var]))
        for t in self.targets:
            if t[0] not in self.phonytargets:
               self.code += ('%s: %s\n%s\n\n' % (t[0], (' '.join(t[1])).strip(), '\n'.join(['\t'+x for x in t[2]])))
        self.code += '\n'
        if len(self.phonytargets) > 0:
           self.code += ('.PHONY: '+' '.join(self.phonytargets)+'\n')
        self.code += '\n'
        for t in self.targets:
            if t[0] in self.phonytargets:
               self.code += ('%s: %s\n%s\n\n' % (t[0], (' '.join(t[1])).strip(), '\n'.join(['\t'+x for x in t[2]])))
        return self.code

class Directory(dict):

    def __init__(self, setup, name, targets):
        self.name, self.targets, self.sortedtargets, self.tests = name, { }, [], []
        self.setup = setup
        for k in targetKinds:
            setattr(self, k, {})
            self.targets[k] = []
        for target in targets:
            hspl = target.header.split()
            targetobj = Target(setup, self, hspl[0], hspl[1], **target)
            getattr(self, targetobj.targettype)[targetobj.name] = targetobj
            self.sortedtargets.append(targetobj.name)
            self[targetobj.name] = targetobj
            if targetobj.targettype in targetKinds: self.targets[hspl[0]].append(targetobj.name)
            if hasattr(targetobj, 'test') and targetobj.test: self.tests.append(targetobj.name)

    def UsedLanguages(self):
        return [lang for lang in self.setup.languages if lang in [self[t].language.name for t in self.sortedtargets]]

    def RenderMakefile(self, subdirs):
        already_included_dependencies = []
        setuppath = './setup'
        if self.name != '.':
           assert not '/' in self.name
           setuppath = '../setup'
        mf = '#\n#\n#\n\n'
        makefile = Makefile()
        if hasattr(self.setup, 'version'): makefile.AddVariable('VERSION', '\"%s\"' % self.setup.version)
        makefile.AddVariable('TARGETS', ' '.join([z for z in self.sortedtargets if not hasattr(self[z], 'test') or not self[z].test]))
        mf += makefile.Render()
        if len(subdirs) > 0:
           makefile = Makefile()
           recursive_order = ['subdirs', '$(TARGETS)']
           if self.setup.mainfirst: recursive_order.reverse()
           makefile.AddTarget('all', recursive_order, [])
           if self.name == '.':
              makefile.AddTarget('Makefile', ['packagesetup'], '%s %s' % (setuppath, self.setup.fulloptions))
           mf += makefile.Render()
           mf += 'subdirs:\n'
           for d in subdirs: mf += ('\tcd %s && $(MAKE)\n' % d)
           mf += '\n'
           mf += 'install: subdirs-install $(TARGETS)\n'
        else:
           mf += 'all: $(TARGETS)\n\n'
           if self.name == '.':
              mf += 'Makefile: packagesetup\n'
              mf += ('\t%s --prefix=%s\n\n' % (setuppath, self.setup.prefix))
           mf += 'install: $(TARGETS)\n'
        pathlist = uniquelist([self[t].installpath for t in self.sortedtargets if hasattr(self[t], 'installpath')])
        #mf += '\n'
        uninstall_files, uninstall_dirs = [], []
        for p in pathlist:
            # INSTALL: creating an installation directory 
            mf += ('\t%s -v -d %s\n' % (self.setup.install, p))
            uninstall_dirs.append(p)
        mf += '\n'
        ldconfig_libs = []
        for t in self.sortedtargets:
            if hasattr(self[t], 'installpath'):
               realtarget = [ t ]
               if self[t].targettype == 'headers': realtarget = self[t].sources
               elif hasattr(self[t], 'installname'): realtarget = [ self[t].installname ]
               for rt in realtarget:
                  # INSTALL: file installation
                  mf += ('\t%s -v -D %s %s\n' % (self.setup.install, rt, self[t].installpath))
                  uninstall_files.append(os.path.join(self[t].installpath, rt))
               if hasattr(self[t], 'installname') and self[t].installname != t:
                  # INSTALL: alternative name installation
                  mf += ('\t%s %s %s\n' % ('cp -vd', t, self[t].installpath))
                  uninstall_files.append(os.path.join(self[t].installpath, t))
               if hasattr(self[t], 'semiinstallname') and self[t].semiinstallname != t:
                  # INSTALL: alternative name installation
                  mf += ('\t%s %s %s\n' % ('cp -vd', self[t].semiinstallname, self[t].installpath))
                  uninstall_files.append(os.path.join(self[t].installpath, self[t].semiinstallname))
               if self[t].targettype == 'library' and self[t].installpath not in ldconfig_libs:
                  ldconfig_libs.append(self[t].installpath)
        if self.setup.platform == 'linux':
           for ld in ldconfig_libs: mf += ('\t%s -n %s\n' % (self.setup.actualpath['ldconfig'], ld))
        mf += '\n'
        #
        #  'uninstall' target
        #
        if len(subdirs) > 0: mf += '\nuninstall: subdirs-uninstall\n'
        else: mf += '\nuninstall:\n'
        for x in uninstall_files: mf += ('\trm -vf %s\n' % x)
        for x in uninstall_dirs: mf += ('\t(rmdir %s || true) 2>/dev/null\n' % x)
        mf += '\n'
        #
        objects = []
        for t in self.sortedtargets: 
            dependencies = self[t].sources
            if not hasattr(self[t], 'language') or not self[t].language.IsCompiled(): 
               #
               # Non-compilable targets 
               #
               mf += ('%s: %s\n' % (t, ' '.join(dependencies)))
               if hasattr(self[t], 'expand'):
                  varstoexpand = self[t].expand.split()
                  varexpr = ','.join([('%s=%s' % (x, getattr(self.setup, x))) for x in varstoexpand])
                  mf += ('\tcat %s | %s --expand=\"%s\" > %s\n' % (' '.join(dependencies), setuppath, varexpr, t))
               elif self[t].targettype == 'headers': mf += '\n'
               else: 
                  if len(dependencies) == 1 and dependencies[0] == t: mf += '\n\n'
                  else: mf += ('\tcat %s > %s\n' % (' '.join(dependencies), t))
               if self[t].targettype == 'script': mf += ('\tchmod "u+x" %s\n' % t)
               mf += '\n'
            else:
              if self[t].language.IsCompiled(): 
                 dependencies = [ObjectFromSource(x) for x in dependencies if self[t].language.IsFileCompilable(x)]
                 if self.setup.openmp:
                    if not hasattr(self[t].language, 'openmpflags') and self[t].language.name in openmpFlags:
                       self[t].language.openmpflags = openmpFlags[self[t].language.name]
                    if not hasattr(self[t].language, 'openmplibraries') and self[t].language.name in openmpLibraries:
                       self[t].language.openmplibraries = openmpLibraries[self[t].language.name]
                    if self[t].language.SupportsOpenMP() and (not hasattr(self[t], 'openmp') or self[t].openmp == True):
                       self[t].flags += ' '+self[t].language.openmpflags+' '
                       self[t].libraries += ' '+self[t].language.openmplibraries+' '
              for s in self[t].sources:
                  if s in already_included_dependencies or not self[t].language.IsFileCompilable(s): continue
                  sources_from_s = []
                  if s in self[t].sourcesfrom: sources_from_s = self[t].sourcesfrom[s]
                  mf += ((ObjectFromSource(s)+': '+s+' '+(' '.join(sources_from_s))).rstrip()+'\n')
                  lapply = self[t].language.Apply(languageCompilation[self[t].language.name], self[t], sources=[s], objects=[ObjectFromSource(s)])
                  if lapply != None: mf += ('\t'+lapply+'\n')
                  mf += '\n'
                  already_included_dependencies.append(s)
              explicit_libraries = [ lib for lib in self[t].libraries.split() if FileExtension(lib) in libraryExtensions]
              if hasattr(self[t], 'installname') and self[t].installname.strip() != '': 
                 explicit_libraries = [ x for x in explicit_libraries if x != self[t].installname ]
              mf += (t+': '+(' '.join(dependencies)+' '+' '.join(explicit_libraries)).strip()+'\n')
              if self[t].language.IsCompiled():
                 objlist = dependencies
                 if self[t].targettype == 'binary' or self[t].targettype == 'module':
                    #
                    # Build binaries or modules
                    # 
                    lapply = self[t].language.Apply(languageLinking[self[t].language.name], self[t], objects=objlist)
                    if lapply != None: mf += ('\t'+lapply+'\n')
                    if hasattr(self[t], 'installname') and self[t].installname != t:
                       mf += ('\trm -f %s\n\tln -s %s %s\n' % (t, self[t].installname, t))
                    mf += '\n'
                 elif self[t].targettype == 'library':
                    #
                    # Build shared libraries
                    #
                    lapply = self[t].language.Apply(languageLinking[self[t].language.name], self[t], objects=objlist)
                    if lapply != None: mf += ('\t'+lapply+'\n')
                    mf += ('\trm -f %s\n\tln -s %s %s\n' % (t, self[t].installname, t))
                    mf += ('\trm -f %s\n\tln -s %s %s\n' % (self[t].semiinstallname, self[t].installname, self[t].semiinstallname))
                    mf += '\n'
                 elif self[t].targettype == 'staticlibrary':
                    #
                    # Build static libraries
                    #
                    lapply = self[t].language.Apply(languageStaticLibraryPacking[self[t].language.name], self[t], objects=objlist)
                    if lapply != None: mf += ('\t'+lapply+'\n\n')
                    #
                 for obj in objlist:
                     if obj not in objects: objects.append(obj)
        checktargets = [t for t in self.sortedtargets if hasattr(self[t], 'test') and self[t].test]
        library_targets = [t for t in self.sortedtargets if self[t].targettype == 'library']
        cleanables = objects+checktargets+[self[x].installname for x in library_targets]+[self[x].semiinstallname for x in library_targets]
        makefile = Makefile()
        if len(subdirs) > 0:
           makefile.AddPhonyTarget('subdirs-install', [], [('cd %s && $(MAKE) install' % d) for d in subdirs])
           if anyof([self.setup.directory[x] for x in subdirs], lambda x: len(x.tests) > 0):
              makefile.AddPhonyTarget('subdirs-check', [], [('cd %s && $(MAKE) check' % d) for d in subdirs])
              makefile.AddPhonyTarget('check', checktargets+['subdirs-check'], [('- ./'+x) for x in checktargets])
           else:
              makefile.AddPhonyTarget('check', checktargets, [('- ./'+x) for x in checktargets])
           makefile.AddPhonyTarget('subdirs-clean', [], [('cd %s && $(MAKE) clean' % d) for d in subdirs])
           makefile.AddPhonyTarget('clean', ['subdirs-clean'], 'rm -f $(TARGETS) %s' % (' '.join(cleanables)))
           makefile.AddPhonyTarget('subdirs-uninstall', [], [('cd %s && $(MAKE) uninstall' % d) for d in subdirs])
        else:
           makefile.AddPhonyTarget('check', checktargets, [('- ./'+x) for x in checktargets])
           makefile.AddPhonyTarget('clean', [], 'rm -f $(TARGETS) %s' % (' '.join(cleanables)))
        mf += makefile.Render()
        return mf

class SetupHandler:

    language, directory, actualpath = { }, { }, { }

    def __getdirectories(self): return list(self.directory.keys())
    def __getlanguages(self): return list(self.language.keys())
    directories = property(__getdirectories, None)
    languages = property(__getlanguages, None)

    def __init__(self, psetup='packagesetup', options={}):
        self.ignore = []
        self.prefix = defaultPrefix
        self.install = defaultInstall
        self.topsrc = os.getcwd()
        self.mainfirst = False
        self.openmp = False
        for opt in options:
            if opt not in reserved_keywords: setattr(self, opt, options[opt])
            else: sys.stderr.write('[Warning] Ignoring invalid command line option, --%s\n' % opt)
        if self.ignore != []: self.ignore = [x.strip() for x in self.ignore.split(',')]
        self.SetupPlatformSpecificOptions()
        self.librarypath = []
        self.AddToLibraryPath('/usr/local/lib')
        self.AddToLibraryPath('/usr/lib')
        for thing in os.listdir('/usr/lib'):
            dirthing = os.path.join('/usr/lib', thing)
            if os.path.isdir(dirthing): self.AddToLibraryPath(dirthing)
        for lang in defaultLanguages: self.language[lang] = Language(lang, self)
        self.ParsePackageSetup(psetup, options)
        self.fulloptions = options.fulloptions 
        #
        self.AddToLibraryPath(os.path.join(self.prefix, 'lib'))
        #
        # Detect other library paths
        #
        for d in self.directories:
            for t in self.directory[d].sortedtargets:
                if not hasattr(self.directory[d][t], 'libraries'): continue
                libs = [x.strip().replace('-L', '') for x in self.directory[d][t].libraries.split() if x.strip().startswith('-L')]
                for library in libs: self.AddToLibraryPath(library) 

    def SetupPlatformSpecificOptions(self):
        global defaultCompiler, defaultLinker, libraryExtensions, libraryNamePattern
        global librarySharedFlags, moduleSharedFlags, languageLinking, openmpFlags, openmpLibraries
        global librarySharedLinkerFlags, moduleSharedLinkerFlags, librarySemiNamePattern
        #
        defaultCompiler = { 'c++': 'g++', 'd': 'gdc', 'c': 'gcc', 'lpunit': 'lpmaketest', 'plugcode': 'plugmaker' }
        defaultLinker = { 'c++': 'g++', 'd': 'gdc', 'c': 'gcc', 'lpunit': 'g++', 'plugcode': 'gcc' }
        if not hasattr(self, 'platform'): self.CheckPlatform()
        if self.platform == 'linux':
           sys.stdout.write('* Detected Linux platform\n\n') 
           libraryNamePattern = '%(name)s.%(extension)s.%(major)d.%(minor)d.%(revision)d'
           librarySemiNamePattern = '%(name)s.%(extension)s.%(major)d'
           libraryExtensions = ['a', 'so']
           librarySharedFlags = ' -fPIC -shared '
#FIXME  #librarySharedLinkerFlags = ' -shared -Wl,-export-dynamic -Wl,-soname,%(shortname)s.%(major)d'
           librarySharedLinkerFlags = ' -shared -Wl,-soname,%(shortname)s.%(major)d'
           moduleSharedFlags = ' -fPIC -shared '
           moduleSharedLinkerFlags = ' -fPIC -shared '
           languageLinking = { 'c++': '%(linker)s -o %(target)s %(object)s -Wl,-rpath,%(prefix)s/lib %(linkflags)s',
                               'd': '%(linker)s -o %(target)s %(object)s -Wl,-rpath,%(prefix)s/lib %(linkflags)s',
                               'c': '%(linker)s -o %(target)s %(object)s -Wl,-rpath,%(prefix)s/lib %(linkflags)s',
                               'lpunit': '%(linker)s -o %(target)s %(object)s -Wl,-rpath,%(prefix)s/lib %(linkflags)s',
                               'plugcode': '%(linker)s -o %(target)s %(object)s -Wl,-rpath,%(prefix)s/lib %(linkflags)s'}
           openmpFlags = { 'c++': '-fopenmp', 'c': '-fopenmp' }
           openmpLibraries = { 'c++': '-lgomp', 'c': '-lgomp' }
        elif self.platform == 'darwin':
           sys.stdout.write('* Detected Mac OS X platform\n\n')
           libraryNamePattern = '%(name)s.%(major)d.%(minor)d.%(revision)d.%(extension)s'
           librarySemiNamePattern = '%(name)s.%(major)d.%(extension)s'
           libraryExtensions = ['a', 'dylib']
           librarySharedFlags = ' -fno-common '
           librarySharedLinkerFlags = ' -Wl,-undefined -Wl,dynamic_lookup -install_name %(output)s -compatibility_version %(major)d -current_version %(major)d.%(minor)d -Wl,-single_module'
           moduleSharedFlags = ' -fno-common -bundle '
           moduleSharedLinkerFlags = '-fno-common -Wl,-undefined -Wl,dynamic_lookup -bundle '
           languageLinking = { 'c++': '%(linker)s -o %(target)s %(object)s %(linkflags)s',
                               'd': '%(linker)s -o %(target)s %(object)s %(linkflags)s',
                               'c': '%(linker)s -o %(target)s %(object)s %(linkflags)s',
                               'lpunit': '%(linker)s -o %(target)s %(object)s %(linkflags)s',
                               'plugcode': '%(linker)s -o %(target)s %(object)s %(linkflags)s' }
           openmpFlags = { 'c++': '-fopenmp', 'c': '-fopenmp' }
           openmpLibraries = { 'c++': '-lgomp', 'c': '-lgomp' }
        else: raise UnknownPlatform(self.platform)

    def AddToLibraryPath(self, d):
        if not d in self.librarypath: self.librarypath.insert(0, d)

    def LibraryPath(self): return self.librarypath

    def ParseBlock(self, header='general'):
        block = Block(header)
        while len(self.linebuffer) > 0:
              line = self.linebuffer.pop(0).strip()
              if line.split()[0] == 'end': break
              elif '+=' in line:
                 tag, value = [x.strip() for x in line.split('+=')]
                 block['+('+tag+')'] = removequotes(value) 
              elif '=' in line: 
                 linesplit = [x.strip() for x in line.split('=')]
                 tag = linesplit[0]
                 value = '='.join(linesplit[1:])
                 block[tag] = removequotes(value)
              elif line.split()[0] in blocktags:
                 tmpblock = self.ParseBlock(line)
                 if not 'blocks' in block: block['blocks'] = []
                 block['blocks'].append(tmpblock)
        return block

    def ReadLineBuffer(self, filename):
        rawdata = open(filename, 'r').read()
        while '\\\n' in rawdata:
              rawdata = rawdata.replace('\\\n', '')
        return [x for x in rawdata.split('\n') if not ignorable(x)]

    def ExpandBackquotes(self):
        for i, z in enumerate(self.linebuffer):
            if '`' in z:
               p0 = z.find('`')
               p1 = z.find('`', p0+1)
               self.linebuffer[i] = z.replace('`%s`' % z[p0+1:p1], OutputFromCommand(z[p0+1:p1]))

    def ExpandConditionals(self, options):
        x = [w for w in self.linebuffer if 'ifdef' in w]
        if len(x) == 0: return False
        #
        def ReadUntilFindPair():
            level, buf = 0, list()
            while len(self.linebuffer) > 0:
                  z = self.linebuffer.pop(0).strip()
                  if level == 0 and ('endif' in z or 'else' in z):
                     self.linebuffer.insert(0, z)
                     return buf
                  if 'ifdef' in z: level += 1
                  elif 'endif' in z: level -= 1
                  buf.append(z)
            raise Exception('Malformed ifdef/else/endif statement')
        #
        lbuf, inside_cond, consider_cond = list(), False, False
        condition = None
        while len(self.linebuffer) > 0:
              z = self.linebuffer.pop(0).strip()
              if z.startswith('ifdef '):
                 inside_cond, condition = True, z.split()[1]
                 consider_cond = (condition in options)
                 buf = ReadUntilFindPair()
                 if consider_cond:
                    for line in buf: lbuf.append(line)
              elif z.startswith('else'):
                 consider_cond = not consider_cond 
                 buf = ReadUntilFindPair()
                 if consider_cond: # Ojo, la condicion se invirtio antes!
                    for line in buf: lbuf.append(line)
              elif z.startswith('endif'):
                 inside_cond = False
                 continue
              elif not inside_cond: lbuf.append(z)
              elif inside_cond and consider_cond: lbuf.append(z)
        self.linebuffer = lbuf
        return True

    def ParsePackageSetup(self, psetup, options):
        self.linebuffer = self.ReadLineBuffer(psetup)
        self.ExpandBackquotes()
        while self.ExpandConditionals(options): pass
        for i, line in enumerate(self.linebuffer):
            self.linebuffer[i] = ExpandVariables(line, options)
        self.block = self.ParseBlock()
        for tag in globaltags: 
            if tag in self.block: setattr(self, tag, self.block[tag])
        # Se asignan de nuevo las opciones, no es un error
        # Es necesario para que las opciones de linea de comandos puedan  
        # redefinir las del packagesetup 
        for opt in options:
            if opt not in reserved_keywords: setattr(self, opt, options[opt])
            else: sys.stderr.write('[Warning] Ignoring invalid command line option, --%s\n' % opt)
        #
        for b in self.block['blocks']:
            hspl = b.header.split()
            if hspl[0] == 'language':
               if hspl[1] not in self.language: raise UnknownLanguage(hspl[1])
               self.language[hspl[1]].Update(b)
            elif hspl[0] == 'directory': self.directory[hspl[1]] = Directory(self, hspl[1], b['blocks'])

    def CreateMakefile(self, d, subdirs):
        mf = d.RenderMakefile(subdirs)
        mfname = os.path.join(d.name, 'Makefile')
        print('   ->', mfname)
        open(mfname, 'w').write(mf)

    def CheckPlatform(self):
        u = OutputFromCommand('uname -a').split()
        if u[0].strip().lower() == 'linux': self.platform = 'linux'
        if u[0].strip().lower() == 'darwin': self.platform = 'darwin'
        if u[0].strip().lower() == 'sunos': self.platform = 'sunos'

    def RequiredLibraries(self):
        librarylist = []
        for d in self.directories:
            for t in self.directory[d].sortedtargets:
                if not hasattr(self.directory[d][t], 'libraries'): continue
                libs = [x.strip().replace('-l', 'lib') for x in self.directory[d][t].libraries.split() if x.strip().startswith('-l')]
                for library in libs: 
                    if library not in librarylist: librarylist.append(library)
        return librarylist

    def RequiredPkgConfigLibraries(self):
        pkgconfiglist = []
        for d in self.directories:
            for t in self.directory[d].sortedtargets:
                if hasattr(self.directory[d][t], 'pkgconfig') and self.directory[d][t].pkgconfig != '':
                   for pc in self.directory[d][t].pkgconfig.split():
                       if pc not in pkgconfiglist: pkgconfiglist.append(pc)
        return pkgconfiglist

    def RequiredCompilers(self):
        compilerlist = []
        for d in self.directories:
            for t in self.directory[d].sortedtargets:
                if not hasattr(self.directory[d][t], 'compiler'): continue
                if self.directory[d][t].compiler not in compilerlist: 
                   compilerlist.append(self.directory[d][t].compiler)
        return compilerlist

    def RequiredUtilities(self):
        utilitylist = ['make', 'install']
        for d in self.directories:
            for t in self.directory[d].sortedtargets:
                if hasattr(self.directory[d][t], 'pkgconfig') and self.directory[d][t].pkgconfig != '':
                   if 'pkg-config' not in utilitylist: utilitylist.append('pkg-config')
                if self.platform == 'linux' and self.directory[d][t].targettype == 'library': 
                   if 'ldconfig' not in utilitylist: utilitylist.append('ldconfig')
        return utilitylist

    def HaveExecutable(self, ex): 
        sys.stdout.write('   '+ex+' ')
        expath = os.popen('PATH=/sbin:$PATH which %s' % ex, 'r').readline().strip()
        if (expath != ''):
           print('->', expath)
           return os.path.abspath(expath)
        else: 
           sys.stdout.write('NOT FOUND\n')
           return None

    def HaveLibrary(self, library):
        sys.stdout.write('   '+library+' ')
        st = False
        for lpath in self.LibraryPath():
            for ext in libraryExtensions:
                if os.path.exists(os.path.join(lpath, library+'.'+ext)):
                   print('->', os.path.join(lpath, library+'.'+ext))
                   st = True
                   break
            if st: break
        if not st:
           if library in ('libdl', 'libm'):
              sys.stdout.write('not found (IGNORED)\n')
              st = True
           else: sys.stdout.write('NOT FOUND\n')
        return st

    def HavePkgConfigLibrary(self, pc):
        sys.stdout.write('   '+pc+' ')
        statuscode = os.popen('pkg-config --exists %s ; echo $?' % pc).readline().strip()
        st = (statuscode == '0')
        if not st: sys.stdout.write('NOT FOUND\n')
        else: 
           cflags = os.popen('pkg-config --cflags %s' % pc).readline().strip()
           libs = os.popen('pkg-config --libs %s' % pc).readline().strip()
           if cflags.startswith('-I'): print('->', os.path.dirname(cflags.replace('-I', '')))
           elif libs.startswith('-L'): print('->', os.path.dirname(libs.replace('-L', '')))
           else: print('->', cflags+' '+libs)
        return st

    def Setup(self):
        if not hasattr(self, 'debug'): self.debug = False
        if self.debug: sys.stdout.write('* IN DEBUG MODE\n')
        self.actualpath = { }
        sys.stdout.write('* Configuring package %s version %s\n\n' % (self.name, self.version))
        sys.stdout.write('* Using installation directory: %s\n\n' % self.prefix)
        sys.stdout.write('* Checking for sources: ')
        genfiles = []
        for d in self.directories:
            for t in self.directory[d].sortedtargets:
                genfiles.append(os.path.abspath(os.path.join(d, t)))
        for d in self.directories:
            for t in self.directory[d].sortedtargets:
                for s in self.directory[d][t].sources:
                    sfile = os.path.join(d, s)
                    if not os.path.abspath(sfile) in genfiles and not os.path.exists(sfile) and sfile not in self.ignore:
                       raise MissingComponent('source file', sfile)
        print('OK')
        print('* Checking for compilers:')
        for comp in self.RequiredCompilers(): 
            if comp.startswith('./') or comp.startswith('../'): continue
            ans = self.HaveExecutable(comp)
            if ans == None and comp not in self.ignore: raise MissingComponent('compiler', comp)
            self.actualpath[comp] = ans
        if self.openmp: print('\n* Using OpenMP directives')
        print('\n* Checking for other utilities:')
        for ut in self.RequiredUtilities():
            ans = self.HaveExecutable(ut)
            if ans == None and ut not in self.ignore: raise MissingComponent('utility', ut)
            self.actualpath[ut] = ans
        if 'pkg-config' in self.RequiredUtilities():
           os.environ['PKG_CONFIG_PATH'] = os.path.join(self.prefix, 'lib/pkgconfig')+':'+os.getenv('PKG_CONFIG_PATH', '')
           print('\n* Checking for pkgconfig libraries')
           for pc in self.RequiredPkgConfigLibraries():
               if not self.HavePkgConfigLibrary(pc) and pc not in self.ignore: 
                  raise MissingComponent('pkgconfig library', pc)
        print()
        rlib = self.RequiredLibraries()
        if len(rlib) > 0: 
           print('* Checking for libraries:')
           for lib in self.RequiredLibraries():
               if not self.HaveLibrary(lib) and lib not in self.ignore: 
                  raise MissingComponent('library', lib)
           print()
        print('* Creating makefiles:')
        toplevelSubdirs = [d for d in self.directories if d != '.']
        for d in self.directories:
            subdirs = []
            if d != '.' and not os.path.exists(d): os.system('mkdir -p %s' % d)
            if d == '.': subdirs = toplevelSubdirs
            self.CreateMakefile(self.directory[d], subdirs)
        print('\nEverything seems ready. Now you can compile %s' % self.name)
        print('with \'make\' and \'make install\' (without quotes)')

class OptionParser(dict):

    def __init__(self, argv):
        self.arguments = []
        self.fulloptions = ' '.join(argv[1:])
        argvs = deepcopy(argv)
        while len(argvs) > 0:
            word = argvs.pop(0)
            if word.startswith('--'): 
               option_name = word[2:]
               if '=' in option_name: self[option_name.split('=')[0]] = '='.join(option_name.split('=')[1:])
               else: self[option_name] = True 

def ExpandVariables(buffer, d):
    for key in d: buffer = buffer.replace('$('+key+')', str(d[key]))
    # Begin automatic variables
    buffer = buffer.replace('$(PYTHONLIB)', pythonlib)
    # End of automatic variables
    return buffer

def ShowHelp():
    sys.stdout.write('Usage: setup [OPTIONS]\n\n')
    sys.stdout.write('\t--help\n')
    sys.stdout.write('\t--prefix=<dir>\n')
    sys.stdout.write('\t--openmp\n')
    sys.stdout.write('\t--platform=<platform>\n')

#
#
#
if __name__ == '__main__':
   try:
      opt = OptionParser(sys.argv)
      if 'expand' in opt:
         sys.stdout.write(ExpandVariables(sys.stdin.read(), dict([x.split('=') for x in opt['expand'].split(',')])))
      elif 'help' in opt: ShowHelp()
      else: SetupHandler('packagesetup', opt).Setup()
   except Exception as e:
      print('\n', e)

