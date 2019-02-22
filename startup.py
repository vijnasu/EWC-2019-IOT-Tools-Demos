# -*- coding: UTF-8 -*-
###############################################################################
# Copyright © 2010 2011 2016 Intel Corporation All Rights Reserved.
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material may contain trade secrets and propri-
# etary information of Intel Corporation and its suppliers
# and licensors, and is protected by worldwide copyright and trade secret laws
# and treaty provisions. No part of the Material may be used, copied,
# reproduced, modified, published, uploaded, posted, transmitted, distributed,
# or disclosed in any way without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be ex-
# press and approved by Intel in writing.
###############################################################################

import __builtin__
import __main__
import sys
import os, os.path
import platform
try:
    import pkg_resources
except ImportError:
    raise ImportError("setuptools does not seem to be installed on this system.  Please use 'pip install setuptools' to install.")

try:
    import clr
except ImportError:
    raise ImportError("Python.Net was not found on this system. Please install a version of python.Net appropriate for the DAL")
import System

# Interactive session startup script

def _getPythonBitsize():
    """Get the bit size of the python runtime (32 or 64) by determining
    the size of a pointer, which is in bytes.
    """

    # This trick works in all pythons, including IronPython.

    import struct as _struct;
    return 8 * _struct.calcsize("P")


def _machine():
    """Return type of machine."""

    # 7/19/2012 (splepist):
    # Python 2.7 and later fixed a bug where machine() would not
    # actually query the operating system but instead would query
    # the python runtime itself.  This is an issue only on Windows.
    # Python issue: http://bugs.python.org/issue7860
    if os.name == 'nt' and sys.version_info[:2] < (2,7):
        # Look for PROCESSOR_ARCHITEW6432 and if not found then
        # PROCESSOR_ARCHITECTURE; otherwise, return empty string.
        return os.environ.get("PROCESSOR_ARCHITEW6432", os.environ.get('PROCESSOR_ARCHITECTURE', ''))
    else:
        return platform.machine()


def _getOSBitsize():
    """Get the bit size of the underlying operating system (32 or 64).
    Returns None if the information cannot be identified.
    """

    # 7/19/2012 (splepist):
    # Note: Yes, this is a hack but python does not provide a clean way
    # of determining operating size that is consistent across operating systems
    # and python versions.
    # For details, see
    # http://stackoverflow.com/questions/7164843/in-python-how-do-you-determine-whether-the-kernel-is-running-in-32-bit-or-64-bi
    machine2bits = {'AMD64': 64, 'x86_64': 64, 'i386': 32, 'x86': 32}
    machine = _machine()
    return machine2bits.get(machine, None)


def _processModule(script):
    """Given a module with possible path, add the module's full path to
    the sys.path and then import that module into the __main__ namespace.
    """
    script = os.path.abspath(script)
    modulePath = os.path.dirname(script)
    (moduleName, ext) = os.path.splitext(os.path.basename(script))
    if modulePath not in sys.path:
        sys.path.append(modulePath)
    print("Importing module %s..."%moduleName)
    try:
        __builtin__.__import__(moduleName)
        if moduleName in sys.modules:
            setattr(__main__, moduleName, sys.modules[moduleName])
    except ImportError, e:
        print("  Failed to import: %s"%e)
        print("  Skipping module %s"%moduleName)


def _processStartupModule(module):
    """Import the specified module if it exists."""
    script = os.path.abspath(module)
    modulePath = os.path.dirname(script)
    (moduleName, ext) = os.path.splitext(os.path.basename(script))
    if modulePath not in sys.path:
        sys.path.append(modulePath)
    try:
        __builtin__.__import__(moduleName)
        if moduleName in sys.modules:
            setattr(__main__, moduleName, sys.modules[moduleName])
            print("Successfully imported \"%s\""%script)
    except:
        pass # Ignore errors


def _processStartupModules():
    """Search for startup modules in a specific order and import them
    one at a time.  If a startup module does not exist, skip it.

    Startup Module file name in the DAL folder: dalstartup.(.py, pyc)
    Startup Module file name in the user folder: daluserstartup.(.py, pyc)

    Note: the file names have to be different as python distinguishes module
    by the base file name.

    Search and execute order:
      1. Dal Install folder
      2. User's folder

    """
    dalStartupFilename = "dalstartup"
    dalUserStartupFilename = "daluserstartup"
    # Installation folder (which is already at the start of the sys.path)
    path = dalStartupFilename
    _processStartupModule(path)

    # User's home folder
    path = os.path.expanduser("~")
    if path != "~":
        path = os.path.join(path, dalUserStartupFilename)
        _processStartupModule(path)


def _getDALVersion():
    versionInfo = System.Diagnostics.FileVersionInfo.GetVersionInfo("Intel.DAL.Services.CommandsLibrary.dll")
    dalversion = versionInfo.ProductVersion
    dalcomments =versionInfo.Comments
    return("Intel DAL %s %s" % (dalversion, dalcomments))


def _getPythonPackageVersion(package_name):
    """Returns a string containing the version of the given python package name.
    Returns None if the package is not installed."""
    try:
        # Returns pkg_resources.DistributionData object
        package_data = pkg_resources.get_distribution(package_name)
        return package_data.parsed_version.public
    except pkg_resources.DistributionNotFound:
        pass
    return None


def _getPyreadlineVersion():
    """Get the version of pyreadline installed on this system.  Returns a
    string containing the version or None, if the package is not installed.

    Note: pyreadline is expected to be found only on Windows.
    """
    return _getPythonPackageVersion("pyreadline")


def _getPythonNetVersion():
    """Get the version of python.Net installed on this system.  Returns a
    string containing the version or None, if the package is not installed.

    Note: 'python.Net-python27' is version 2.0.19 or earlier while 'pythonnet'
    is 2.1 or later.
    """
    version = _getPythonPackageVersion("pythonnet")
    if not version:
        version = _getPythonPackageVersion("python.Net-python27")
    return version


def _getPythonVersion():
    clrstring = ""
    pyreadlineVersion = ""
    exe = os.path.basename(sys.executable)
    pyname = exe
    if exe in ["python.exe", "python", "masterframe.hostpython.exe", "masterframe.hostpython"]:
        pythonnetVersion = _getPythonNetVersion()
        if pythonnetVersion:
            clrstring = ", Python.NET " + pythonnetVersion
        else: #if we don't find the pip package we just take the runtime version
            executingAssembly = System.Reflection.Assembly.GetExecutingAssembly()       
            pythonRuntime = executingAssembly.GetModule("Python.Runtime.dll")
            if pythonRuntime != None:
                version = pythonRuntime.Assembly.GetName().Version
                clrstring = ", Python.NET runtime %s.%s.%s.%s" % (version.Major, version.Minor, version.Build, version.Revision)

        pylinever = _getPyreadlineVersion()
        if pylinever:
            pyreadlineVersion = ", pyreadline %s" % pylinever

    elif exe in ["ipy.exe", "ipy64.exe", "ipy", "ipy64"]:
        pyname = "IronPython"

    pybitness = platform.architecture()[0]
    pyversion = ".".join(map(str,sys.version_info[:3]))
    netversion = System.Environment.Version

    return("%s %s (%s), .NET %s%s%s" % (pyname, pyversion, pybitness, netversion, clrstring, pyreadlineVersion))

def _printTargetConfiguration(itpii):
    import Intel.DAL.Services.TargetTopology as topology
    from itpii.datatypes import Icast as _icast
    masterFrame = itpii.cmdsControl._getMasterFrame()
    topologyService = None
    if masterFrame is not None:
        topologyService = _icast(masterFrame.GetService[topology.IServiceTargetTopology](), topology.IServiceTargetTopology)
    if topologyService is not None:
        targetConfigName = topologyService.GetTargetConfigurationName()
        if targetConfigName is not None:
            print("Using %s" % targetConfigName)

def _warnIfLoggingEnabled(itpii):
    #clr.AddReference("Intel.DAL.Services.InternalLogging")
    import Intel.DAL.Services.InternalLogging as logging
    from itpii.datatypes import Icast as _icast
    masterFrame = itpii.cmdsControl._getMasterFrame()
    loggingService = None
    if masterFrame is not None:
        loggingService = _icast(masterFrame.GetService[logging.IServiceInternalLogging](), logging.IServiceInternalLogging)
    if loggingService is not None:
        # force refresh if it has been 15 seconds since log4net configuration was read from disk
        loggingService.Refresh(15000)
        enabledLogFiles = []
        files = loggingService.GetLoggerFileNames()
        for file in files:
            if loggingService.IsLoggingEnabled(file):
                loggers = loggingService.GetLoggerNames(file)
                for logger in loggers:
                    if loggingService.GetLevel(file, logger)!="OFF":
                        enabledLogFiles.append(file)
                        break
        if len(enabledLogFiles):
            print '\nWarning: DAL Logging is enabled for:',
            print enabledLogFiles[0],
            for file in enabledLogFiles[1:-1]:
                print '\b,',
                print file,
            if len(enabledLogFiles)>1:
                print '\b and',
                print enabledLogFiles[-1],
            print '\n\nLogging may impact performance. Use itp.loggeroff() to disable logging.'
if __name__ == "__main__":
    from optparse import OptionParser
    _parser = OptionParser()
    _parser.add_option("--mac",
                      action="append", dest="startupScripts", metavar="MODULEPATH",
                      help="A module to be loaded at start up")
    _parser.add_option("--showexceptions",
                      action="store_true", dest="showexceptions", default=False,
                      help = "Enable display of full exception details (turns off the exceptions override enhancement")

    _parser.add_option("--privileged",
                      action="store_true", dest="inprocMF", default=False,
                      help = """Try to accelerate the "Intel (r) DAL Python CLI" by including the DAL in the same process as python.
                      Note that there can only be one "privileged" client at a time on the same system.""")
    _parser.add_option("--diagnostics",
                       action="store_true", dest="rundiagnostics", default=False,
                       help = "Enable diagnostics mode which will display critical python plugins status and .NET platform versions installed.")
    try:
        (_options, args) = _parser.parse_args()
    except SystemExit:
        sys.exit(0)  

    # Warn users if unsupported python version is used
    minorVersion = int(sys.version.split()[0][2])
    if sys.version.split()[0][0] != "2" or minorVersion < 6:
        print("\nWarning: You are running Intel DAL on unsupported %s version of Python. You need 2.6.x version!\n" % (sys.version.split()[0]))

    # Set the PYTHONINSPECT env variable to ensure the script is interactive
    # NOTE: this currently isn't implemented in IronPython 2.6
    os.environ["PYTHONINSPECT"] = "1"

    # Set the sys.path to ensure the itpii module is always found:
    # (Assumption: this file always lives inside of itpii directory)
    abspath = os.path.abspath(sys.argv[0])
    if os.path.dirname(os.path.dirname(abspath)) not in sys.path:
        # Insert at beginning of path so as to override any other DAL
        # install.
        sys.path.insert(0, os.path.dirname(os.path.dirname(abspath)))
    del abspath    

    # Setup the ITP-specific items:
    import itpii
    from itpii import enhancements # Note: IronPython 2.6 does not support "import itpii.enhancements"

    enhancements.enable()
    if _options.showexceptions:
        enhancements.disableExceptionOverride()    

    _diagnostics = 0

    if _options.rundiagnostics:        
       _diagnostics = 1    

    import getDependencies as _getDependencies
    _getDependencies.verifyEnvironment(verbose = _diagnostics)

    ######################################################################
    # import clr and import System has to be called after 
    # _getDependencies.verifyEnvironment
    ######################################################################
    import clr
    import System
    ######################################################################

    print("Using %s" % _getDALVersion())
    print("Using %s" % _getPythonVersion())


    inprocMF = False
    if _options.inprocMF:
        inprocMF = True

    if inprocMF:
        # Privileged mode requested, see if we are going to allow it.
        # If MasterFrame is already in this mode, a warning will be
        # presented later to that fact.
        pythonSize = None
        osSize = None
        try:
            pythonSize = _getPythonBitsize()
            osSize = _getOSBitsize()
            if pythonSize == 32 and osSize == 64:
                print("\nWarning: 'privileged' mode requested but cannot be given when running a 32-bit python on a 64-bit operating system!\n")
                inprocMF = False
        except Exception,e:
            print("\nWarning: 'privileged' mode requested but cannot be given due to an error: %s\n"%(e))
            inprocMF = False
        finally:
            del pythonSize
            del osSize

    itp = itpii.baseaccess(privileged = inprocMF)
    _printTargetConfiguration(itpii)
    _warnIfLoggingEnabled(itpii)
    _processStartupModules()

    if _options.startupScripts != None and len(_options.startupScripts) > 0:
        for _script in _options.startupScripts:
            _processModule(_script)

try:
    sys.path.append(r'.\itpii\dci')
    import dci_utils as dci
except Exception,e:
    # The following warning was removed per HSD#2007356159
    # print("\tWarning: Unable to load DCI utilities - %s"%e)
    pass

try:
    sys.path.append(r'.\itpii\dci')
    import dci_dma as dma
except Exception,e:
    # The following warning was removed per HSD#2007356159
    # print("\tWarning: Unable to load DCI DMA utilities - %s"%e)
    pass

