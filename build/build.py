import os
import datetime
import subprocess
import shutil
import zipfile
import sys
import json
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
import platform
import glob

class BuildSystemConfig:
    def __init__(self, operatingSystem, rootPath, buildNumber, buildServer, timestamp, stampBuildWithVersion, productsDir, msbuildExe, innoSetupExe, xcodeBuildExe, copyArtifacts, copyArtifactsDir):
        self.operatingSystem = operatingSystem
        self.rootPath = rootPath
        self.buildNumber = buildNumber
        self.buildServer = buildServer
        self.timestamp = timestamp
        self.stampBuildWithVersion = stampBuildWithVersion
        self.productsDir = productsDir
        self.msbuildExe = msbuildExe
        self.innoSetupExe = innoSetupExe
        self.xcodeBuildExe = xcodeBuildExe
        self.copyArtifacts = copyArtifacts
        self.copyArtifactsDir = copyArtifactsDir

    def verify(self):
        error = False

        error |= isPathMissing(self.rootPath)
        error |= isPathMissing(self.productsDir)
        if self.operatingSystem == 'win':
            error |= isPathMissing(self.msbuildExe)
            error |= isPathMissing(self.innoSetupExe)
        else:
            error |= isPathMissing(self.xcodeBuildExe)

        if self.copyArtifacts:
            error |= isPathMissing(self.copyArtifactsDir)

        if error:
            raise Exception('Missing paths, unable to continue')

    def printSettings(self):
        printFlush("Root Path:          " + self.rootPath)
        printFlush("Root Path (Full):   " + os.path.abspath(self.rootPath))
        printFlush("Build Server:       " + self.buildServer)
        printFlush("Build Number:       " + self.buildNumber)
        printFlush("Timestamp:          " + self.timestamp)
        printFlush("Stamp Build:        " + str(self.stampBuildWithVersion))
        printFlush("Products Dir:       " + self.productsDir)
        if operatingSystem == 'win':
            printFlush("MS Build:           " + self.msbuildExe)
            printFlush("Inno Setup:         " + self.innoSetupExe)
        else:
            printFlush("XCode Build:        " + self.xcodeBuildExe)
        printFlush("Copy Artifacts:     " + str(self.copyArtifacts))
        printFlush("Copy Artifacts Dir: " + self.copyArtifactsDir)


class ProductConfig:

    def __init__(self, productToBuild, buildName, solutionPath, clean, configuration, logDestPath, installerFile, installerName, installerExe, macInstallerDir, schemes, contents):
        self.productToBuild = productToBuild
        self.buildName = buildName
        self.solutionPath = solutionPath
        self.clean = clean
        self.configuration = configuration
        self.logDestPath = logDestPath
        self.installerFile = installerFile
        self.installerName = installerName
        self.installerExe = installerExe
        self.macInstallerDir = macInstallerDir
        self.schemes = schemes
        self.contents = contents

    def verify(self):
        error = False

        if error:
            raise Exception('Missing paths, unable to continue')

    def printSettings(self):
        printFlush("Product:            " + self.productToBuild)
        printFlush("Build Name:         " + self.buildName)
        printFlush("Solution:           " + self.solutionPath)
        printFlush("Clean:              " + str(self.clean))
        printFlush("Configuration:      " + self.configuration)
        printFlush("Log Path:           " + self.logDestPath)
        printFlush("Installer Config:   " + self.installerFile)
        printFlush("Installer Name:     " + self.installerName)
        printFlush("Installer Exe:      " + self.installerExe)
        printFlush("Mac Installer Dir:  " + self.macInstallerDir)
        printFlush("Schemes:            " + str(self.schemes))
        printFlush("Contents:           " + str(self.contents))


def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)


def exitIfPathMissing(dir):
    if not os.path.exists(dir):
        raise Exception('Path missing: ' + dir)


def ensureExists(dir):
    if not os.path.exists(dir):
        print("Creating " + dir)
        os.makedirs(dir)


def printFlush(s):
    print(s)
    sys.stdout.flush()


def makeBuildName(rootPath, productName, buildNumber, timestamp):
    releaseNumber = open(os.path.join(rootPath, "products", productName, "releaseNumber.txt"), 'r').read().strip()
    buildNameWithoutRelease = timestamp + "-" + buildNumber
#    buildNameWithRelease = datetime.datetime.today().strftime('%Y%m%d-%H%M%S') + "-" + buildNumber + "-" + releaseNumber
    return buildNameWithoutRelease


def copyToOutputDir(buildName, installerPath, logFile, outputDir):

    ensureExists(outputDir)

    fullOutputPath = os.path.join(outputDir, buildName)
    ensureExists(fullOutputPath)

    shutil.copy(installerPath, fullOutputPath)
    shutil.copy(logFile, fullOutputPath)

def buildWindows(buildSystemConfig, productConfig):
    if productConfig.clean:
        commandClean = "{} \"{}\" -target:Clean /p:Configuration={}".format(buildSystemConfig.msbuildExe, productConfig.solutionPath, productConfig.configuration)
        printFlush(commandClean)
        subprocess.check_call(commandClean)

    commandBuild = "{} \"{}\" -target:Build /p:Configuration={} -fileLogger1 -flp1:LogFile={};Verbosity=normal".format(buildSystemConfig.msbuildExe, productConfig.solutionPath, productConfig.configuration, productConfig.logDestPath)
    printFlush(commandBuild)
    subprocess.check_call(commandBuild)

    commandInstaller = "{} /Dconfiguration={} {}".format(buildSystemConfig.innoSetupExe, productConfig.configuration, productConfig.installerFile)
    printFlush(commandInstaller)
    subprocess.check_call(commandInstaller)

def buildMac(buildSystemConfig, productConfig):

    for scheme in productConfig.schemes:
        # temp - clean debug build
        #        commandBuild = "{} -configuration Debug -workspace {} -scheme \"{}\" clean".format(buildSystemConfig.xcodeBuildExe, productConfig.solutionPath, scheme)
        #        printFlush(commandBuild)
        #subprocess.check_call(commandBuild, shell=True)
        
        #        commandBuild = "{} -configuration {} -workspace {} -scheme \"{}\" clean".format(buildSystemConfig.xcodeBuildExe, productConfig.configuration, productConfig.solutionPath, scheme)
        #printFlush(commandBuild)
        #subprocess.check_call(commandBuild, shell=True)

        commandBuild = "{} -configuration {} -workspace {} -scheme \"{}\"".format(buildSystemConfig.xcodeBuildExe, productConfig.configuration, productConfig.solutionPath, scheme)
        printFlush(commandBuild)
        subprocess.check_call(commandBuild, shell=True)

        folders = productConfig.contents[scheme]

        appName = folders["appName"]
        
        for folder in folders["folders"]:
            print(str(folder))
            src = folder["srcDir"]
            dest = folder["destDir"]
    
            srcDir = os.path.join(buildSystemConfig.productsDir, productConfig.productToBuild, src)
            destDir = os.path.join(productConfig.macInstallerDir, "application", dest)
            
            print("Folder: " + str(folder))
            print(srcDir)
            print(destDir)

            if os.path.exists(destDir):
                print("Removing: " + destDir)
                shutil.rmtree(destDir)
            
            printFlush("Copying from " + os.path.abspath(srcDir) + " to " + os.path.abspath(destDir))
            #            parent = os.path.abspath(os.path.join(destDir, os.pardir))
            #if not os.path.exists(parent):
            #   os.makedirs(parent)
            
            shutil.copytree(srcDir, destDir)

    pathBefore = os.getcwd()
    dirToRunScript = os.path.join(productConfig.macInstallerDir)
    print("Running script from:" + os.path.abspath(dirToRunScript))
    os.chdir(dirToRunScript)

    commandInstaller = "./build-macos-x64.sh {} {}".format(productConfig.productToBuild, productConfig.buildName)
    printFlush(commandInstaller)
    subprocess.check_call(commandInstaller, shell=True)

    os.chdir(pathBefore)

    print(os.getcwd())
    destDir = os.path.join(buildSystemConfig.productsDir, productConfig.productToBuild)
    for file in glob.glob(os.path.join(productConfig.macInstallerDir, "target", "pkg", "*.pkg")):
        print("moving " + file + " to " + destDir)
        shutil.move(file, destDir)

def build(buildSystemConfig, productConfig):

    ensureExists(os.path.split(productConfig.logDestPath)[0])

    if buildSystemConfig.operatingSystem == 'win':
        buildWindows(buildSystemConfig, productConfig)
    elif buildSystemConfig.operatingSystem == 'mac':
        buildMac(buildSystemConfig, productConfig)

def buildProduct(buildSystemConfig, productToBuild):

    productToBuildDir = os.path.join(buildSystemConfig.productsDir, productToBuild)
    logDestPath = os.path.join(productToBuildDir, productToBuild + ".log")
    installerFile = os.path.join(productToBuildDir, 'installers', 'win-x64', 'installer.iss')

    buildConfig = os.path.join(productToBuildDir, 'build.json')
    print("Current working directory: " + os.getcwd())
    print("Reading build config from: " + buildConfig)
    print("Reading build config from: " + os.path.abspath(buildConfig))
    f = open(buildConfig)
    jsonConfig = json.load(f)
    f.close()

    config = jsonConfig[buildSystemConfig.operatingSystem]

    solutionPath = os.path.abspath(os.path.join(productToBuildDir, config["solution"]))
    installerName = config["installerName"]
    installerExe = os.path.join(productToBuildDir, installerName)

    clean = config["clean"]
    configuration = config["configuration"]
    
    if buildSystemConfig.operatingSystem == 'mac':
        schemes = config["schemes"]
        contents = config["contents"]
        macInstallerDir = os.path.abspath(os.path.join(productToBuildDir, config["macInstallerDir"]))
    else:
        schemes = []
        contents = []
        macInstallerDir = ""

    buildName = makeBuildName(buildSystemConfig.rootPath, productToBuild, buildSystemConfig.buildNumber, buildSystemConfig.timestamp)

    if buildSystemConfig.stampBuildWithVersion:
        appVersionHeaderFile = os.path.join(productToBuildDir, 'JuceLibraryCode', 'AppConfig.h')
        JUCE_LINE = """ #define JucePlugin_VersionString          \"1.0.0\""""
        replacement = JUCE_LINE.replace("1.0.0", buildName + " (" + buildServer + ")")
        replace(appVersionHeaderFile, JUCE_LINE, replacement)

    productConfig = ProductConfig(productToBuild, buildName, solutionPath, clean, configuration, logDestPath, installerFile, installerName, installerExe, macInstallerDir, schemes, contents)
    productConfig.printSettings()
    productConfig.verify()

    build(buildSystemConfig, productConfig)

    if buildSystemConfig.copyArtifacts:
        copyToOutputDir(productConfig.buildName, productConfig.installerExe, productConfig.logDestPath, buildSystemConfig.copyArtifactsDir)


def readConfig():

    configFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iceberg-ci.json')

    f = open(configFile)
    config = json.load(f)
    f.close()

    print(config)
    return config


def isPathMissing(p):
    if not os.path.exists(p):
        print("Path does not exist: " + p)
        return True

    return False


def readBuildSystemConfig(operatingSystem, buildServer, rootPath, buildNumber):
    exitIfPathMissing(rootPath)

    config = readConfig()

    productsDir = os.path.join(rootPath, config["productsDir"])

    timestamp = datetime.datetime.today().strftime(config["timestampFormat"])

    buildServerConfig = config["buildServers"][buildServer]

    if operatingSystem == 'win':
        msbuildExe = buildServerConfig["msbuildExe"]
        innoSetupExe = buildServerConfig["innoSetupExe"]
        xcodeBuildExe = ''
    else:
        msbuildExe = ''
        innoSetupExe = ''
        xcodeBuildExe = buildServerConfig["xcodeBuildExe"]

    stampBuild = buildServerConfig["stampBuildWithVersion"]

    copyArtifacts = buildServerConfig["copyArtifacts"]
    copyArtifactsDir = ""
    if copyArtifacts and "copyArtifactsDir" in buildServerConfig:
        copyArtifactsDir = buildServerConfig["copyArtifactsDir"]

    buildSystemConfig = BuildSystemConfig(operatingSystem, rootPath, buildNumber, buildServer, timestamp, stampBuild, productsDir, msbuildExe, innoSetupExe, xcodeBuildExe, copyArtifacts, copyArtifactsDir)
    buildSystemConfig.verify()
    buildSystemConfig.printSettings()
    return buildSystemConfig


def getDrives():
    import string
    from ctypes import windll

    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    return drives

# Routine for checking windows dirs on azure
def checkWindowsDirs():
    dirs = []
    print("Drives:")
    for drive in getDrives():
        print(drive)

    dirs.append("""c:\program files""")
    dirs.append("""C:\Program Files (x86)""")

    print("Directory contents:")
    for dir in dirs:
        print(dir)
        contents = os.listdir(dir)
        for content in contents:
            print("\t" + content)
            if content.lower().startswith("inno"):
                print("\t\tInno Setup found")
                innoDirContents = os.listdir(os.path.join(dir, content))
                for d in innoDirContents:
                    print("\t\t\t" + d)


    print("PATH:")
    paths = os.getenv('PATH')
    dirs = paths.split(';')
    for dir in dirs:
        print(dir)

def printSystemInfo(operatingSystem):

    if operatingSystem == 'win':
        checkWindowsDirs

    # Print platform info
    print("System:    " + platform.system())
    print("Release:   " + platform.release())
    print("Version:   " + platform.version())
    print("Processor: " + platform.processor())
    print("Python:    " + str(platform.python_build()))

if __name__=="__main__":

    buildServer = sys.argv[1]
    rootPath = sys.argv[2]
    buildNumber = sys.argv[3]

    system = platform.system()
    if system == 'Darwin':
        operatingSystem = 'mac'
    elif system == 'Windows':
        operatingSystem = 'win'
    else:
        print("Unsupported OS " + system)
        sys.exit(1)

    printSystemInfo(operatingSystem)

    buildSystemConfig = readBuildSystemConfig(operatingSystem, buildServer, rootPath, buildNumber)

    for i in range(4, len(sys.argv)):
        buildProduct(buildSystemConfig, sys.argv[i])
