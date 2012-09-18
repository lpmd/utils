#!/usr/bin/env python

import os, sys, socket, getopt, tempfile

#
#
#

programHelp = "lpmd-installer [ -i <branch or version> | -u ] [-v] [-p <prefix>] [-P <package>] [-s <server>] [-S <suffix>] [ -d <sources dir>] [-t] [-O] [-C <compiler>]"

programVersion = '0.8.4'

class ConnectionError(Exception):
    def __init__(self, server): self.server = server 
    def __repr__(self): return "[Error] Could not connect to server \'%s\'" % self.server
    def __str__(self): return repr(self)

class ProtocolError(Exception):
    def __init__(self, cmd): self.cmd = cmd 
    def __repr__(self): return "[Error] Protocol error when doing \'%s\' (this should not happen!)" % self.cmd
    def __str__(self): return repr(self)

#
#
#
def ConnectToServer(server, port=56737):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      s.connect((server, port))
    except socket.error: raise ConnectionError(server)
    header = s.recv(1024)
    if not header.startswith('LPIP server at '): 
       s.close()
       return None
    return s

def SendCommand(s, cmd):
    s.send(cmd+'\n')
    data = s.recv(1024)
    if data.startswith('FAIL'): raise ProtocolError(cmd)
    if cmd != 'exit' and data.startswith('BYE'): raise ProtocolError(cmd)
    if cmd == 'exit' and not data.startswith('BYE'): raise ProtocolError(cmd)
    if cmd == 'exit': return '' 
    return data[2:].strip()

def transf(x):
    if '>' not in x: return (x+' >/dev/null 2>&1')
    else: return x

def execute(cmd, verbose):
    status = None
    if verbose: status = os.system(cmd)
    else:
       newcmd = '; '.join([(('echo \"  %s\"' % x.strip()+';')+transf(x.strip())) for x in cmd.split(';')])
       status = os.system(newcmd)
    return (int(status) == 0)

class Installer(dict):

    def __init__(self, server):
        self.server = server
        self['try'] = False
        self['verbose'] = False
        self['openmp'] = False
        self['dir'] = ''

    def Install(self, newversion, prefix, suffix, package, compiler):
        print "Preparing to install %s %s" % (package, newversion)
        tmpdir = ''
        if not self['try']:
           if not os.path.exists(prefix):
              try: os.makedirs(prefix)
              except OSError: raise OSError('[Error] You do not have permission to install on %s' % prefix)
           else:
              if not os.access(prefix, os.W_OK):
                 raise OSError('[Error] You do not have permission to install on %s' % prefix)
        s = ConnectToServer(self.server)
        if s == None: raise ConnectionError(self.server)
        data = SendCommand(s, 'branches %s' % package)
        branches = data.split()
        if newversion in branches:
           # installing latest from branch
           newversion = SendCommand(s, 'latest %s %s' % (package, newversion))
        elif newversion == 'stable':
           stable = SendCommand(s, 'stable %s' % package)
           newversion = SendCommand(s, 'latest %s %s' % (package, stable))
        # installing specific version
        simmode = ''
        if self['try']: simmode = '(simulated mode)'
        print "About to install %s %s" % (newversion, simmode)
        data = SendCommand(s, 'sources %s %s' % (package, newversion))
        self['currentdir'] = os.getcwd()
        if self['dir'] != '':
           self['dir'] = os.path.realpath(self['dir'])
           if self['try']:
              print "\nChanging to directory %s:\n" % self['dir']
              print "  ", "cd %s" % self['dir']
           else:
              os.chdir(self['dir'])   
        else:
           tmpdir = tempfile.mkdtemp()
           if not self['try']: os.chdir(tmpdir)
           else: print "\nChanging to temporary directory: %s" % tmpdir
        print "[*] Downloading or updating sources and patches"
        if self['try']:
           for x in data.split('\n'): print "  ", x
        else:
           bigcmd = '; '.join(data.split('\n'))
           status = execute(bigcmd, self['verbose'])
           if status == False: return False
        data = SendCommand(s, 'install %s %s' % (package, newversion))
#        x.replace('$(PREFIX)', prefix).replace('$(SUFFIX)', suffix).replace('$(OPENMP)', openmp).replace('$COMPILER)', compiler)
        if self['openmp']:
         instcmd = [x.replace('$(PREFIX)', prefix).replace('$(OPENMP)','--openmp').replace('$(SUFFIX)', suffix).replace('$(COMPILER)', "--"+compiler) for x in data.split('\n')]
        else:
         instcmd = [x.replace('$(PREFIX)', prefix).replace('$(OPENMP)','').replace('$(SUFFIX)', suffix).replace('$(COMPILER)', "--"+compiler) for x in data.split('\n')]
        cleancmd = [x for x in instcmd if x.startswith('rm ')]
        instcmd = [x for x in instcmd if x not in cleancmd]
        print "[*] Compiling and installing"
        if self['try']:
           for x in instcmd: print "  ", x
        else:
           bigcmd = '; '.join(instcmd)
           status = execute('mkdir -p %s' % prefix, self['verbose'])
           if status == False: return False
           status = execute(bigcmd, self['verbose'])
           if status == False: return False
        if self['dir'] == '':
           print "[*] Cleaning up the installation"
           if self['try']:
              for x in cleancmd: print "  ", x
           else:
              bigcmd = '; '.join(cleancmd)
              status = execute(bigcmd, self['verbose'])
              if status == False: return False
        if self['dir'] != '':
           if self['try']:
              print "\nChanging to original directory: %s\n" % self['currentdir']
              print "  ", "cd %s" % self['currentdir']
           else:
              os.chdir(self['currentdir'])
        else:
           if not self['try']: os.chdir(self['currentdir']) 
           else: print "\nReturning to original directory: %s\n" % self['currentdir']
           print "[*] Deleting temporary directory"
           status = execute('rm -fr %s' % tmpdir, self['verbose'])
           if status == False: return False
        SendCommand(s, 'exit')
        s.close()
        print "[*] Finished installation"

    def ListVersions(self, package):
        s = ConnectToServer(self.server)
        if s == None: raise ConnectionError(self.server)
        print "These are the available versions of package %s:" % package
        data = SendCommand(s, 'branches %s' % package)
        branches = data.split()
        for b in branches:
            print "\nFrom branch %s: " % b
            data = SendCommand(s, 'versions %s %s' % (package, b))
            v = data.split()
            for version in v: print "    %s" % version
        SendCommand(s, 'exit')
        s.close()

    def Update(self, prefix, suffix, package):
        current = ''
        print "Checking for %s in %s" % (package, prefix)
        if package == 'lpmd':
           try:
              p = os.popen("%s/bin/lpmd 2>&1 | egrep '^LPMD version'" % prefix, 'r')
              current = ' '.join(p.readline().strip().split()[2:])
              p.close()
           except: pass
        if current.strip() == '': sys.exit('[Error] Could not detect your version of %s on %s' % (package, prefix))
        print "Detected version", current
        s = ConnectToServer(self.server)
        if s == None: raise ConnectionError(self.server)
        data = SendCommand(s, 'branch %s %s' % (package, current))
        latest = SendCommand(s, 'latest %s %s' % (package, data))
        print "Latest version from this branch is", latest
        SendCommand(s, 'exit')
        s.close()
        if latest == current: 
           sys.exit("You are currently at the latest version. No need to update!")
        result = self.Install(latest, prefix, suffix, package)
        if result == False: print '[Error] Update failed. Search the output above for errors'

if __name__ == '__main__':
    mode, toinstall = '', ''
    server = 'arpa.ciencias.uchile.cl'
    package, prefix, suffix = 'lpmd', '/usr/local', ''
    compiler = ''
    opts, args = getopt.getopt(sys.argv[1:], 'hloutvd:i:s:p:S:P:c:', 
          ['install=', 'list', 'openmp', 'update', 'verbose', 'dir=' 'server=', 'prefix=', 'suffix=', 'package=', 'try', 'compiler='] )
    optdict, ecode, ivars = dict(opts), '', []
    if '-h' in optdict: sys.exit(programHelp)
    elif '-i' in optdict: mode, toinstall = 'install', optdict['-i']
    elif '--install' in optdict: mode, toinstall = 'install', optdict['--install']
    elif '-u' in optdict: mode = 'update'
    elif '--update' in optdict: mode = 'update'
    elif '-l' in optdict: mode = 'list'
    elif '--list' in optdict: mode = 'list'
    elif '-o' in optdict: mode = 'openmp'
    elif '--openmp' in optdict: mode = 'openmp'
    
    if mode == '': sys.exit(programHelp)
    for opt in ('-s', '--server'):
        if opt in optdict: server = optdict[opt]
    
    installer = Installer(server)

    for opt in ('-p', '--prefix'):
        if opt in optdict: prefix = optdict[opt]
    for opt in ('-S', '--suffix'):
        if opt in optdict: suffix = optdict[opt]
    for opt in ('-P', '--package'):
        if opt in optdict: package = optdict[opt]
    for opt in ('-t', '--try'):
        if opt in optdict: installer['try'] = True
    for opt in ('-d', '--dir'):
        if opt in optdict: installer['dir'] = optdict[opt]
    for opt in ('-v', '--verbose'):
        if opt in optdict: installer['verbose'] = True
    for opt in ('-o', '--openmp'):
        if opt in optdict: installer['openmp'] = True
    for opt in ('-c', '--compiler'):
        if opt in optdict: compiler = optdict[opt]

    try:
       if mode == 'install': 
          result = installer.Install(toinstall, prefix, suffix, package, compiler)
          if result == False: print '[Error] Installation failed. Search the output above for errors'
       elif mode == 'update': installer.Update(prefix, suffix, package)
       elif mode == 'list': installer.ListVersions(package)
    except ConnectionError, e: print e
    except ProtocolError, e: print e
    except EnvironmentError, e: print e

