##A simple CI system for cross platform builds of JUCE apps and audio plugins.##

Developed at Iceberg Audio for automated CI builds that build on Azure, teamcity or desktop. This builds a collection of products including their installers.

Requirements:
* Python 3 (e.g. Anaconda). Developed using python 3.7.1
* (Windows) InnoSetup

Add repo to Azure to build Windows and Mac example installers.

Or build on the command line (windows example)
# cd iceberg-ci
# python build\build.py <build machine> <root directory> <build number> <products>

build machine: one of the configurations in builds\iceberg-ci.json. Use this to specify your build tools.
root directory: root folder of the repo
build number: the build number (can auto increment in Azure)
products: space separated list of products to build

e.g.
python build\build.py desktop . 1 example


