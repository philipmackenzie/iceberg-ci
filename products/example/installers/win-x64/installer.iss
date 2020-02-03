; Plugin install

[Setup]
AppName=Example
AppVersion=0.1
DefaultDirName={commonpf}\ExampleCompany\Example
DefaultGroupName=Example
UninstallDisplayIcon={app}\Example.exe
Compression=lzma2
SolidCompression=yes
OutputDir=..\..
OutputBaseFilename=ExampleSetup

[Files]
Source: "..\..\Builds\VisualStudio2017\x64\{#configuration}\App\Example.exe"; DestDir: "{app}"; Flags: replacesameversion

; Source: "Readme.txt"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\My Program"; Filename: "{app}\Example.exe"

