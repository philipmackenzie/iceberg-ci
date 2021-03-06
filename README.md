## A simple CI system for cross platform builds ##

Developed at Iceberg Audio for automated CI builds for audio products using the JUCE library.

Commit to git and get cross-platform installers built in parallel.

### Requirements ###
* Python 3 (e.g. Anaconda). Developed using python 3.7.1
* (Windows) InnoSetup

### How To Use ###
Add repo to Azure to build Windows and Mac example installers.

Or build on the command line (Windows example)
* cd iceberg-ci
* python build\build.py <build machine> <root directory> <build number> <products>

* build machine: one of the configurations in builds\iceberg-ci.json. Use this to specify your build tools.
* root directory: root folder of the repo
* build number: the build number (can auto increment in Azure)
* products: space separated list of products to build

e.g.
python build\build.py desktop . 1 example

### Licence ###

JUCE is owned by ROLI is included as a submodule https://juce.com/juce-5-license
