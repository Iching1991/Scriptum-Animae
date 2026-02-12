[Setup]
AppName=Scriptum Animae
AppVersion=1.0
DefaultDirName={localappdata}\Programs\Scriptum Animae
DefaultGroupName=Scriptum Animae
OutputDir=installer
OutputBaseFilename=Scriptum_Animae_Setup
SetupIconFile=logo.ico
PrivilegesRequired=lowest
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\scriptum_animae.exe"; DestDir: "{app}"
Source: "logo.ico"; DestDir: "{app}"
Source: "logo.png"; DestDir: "{app}"

[Icons]
Name: "{group}\Scriptum Animae"; Filename: "{app}\scriptum_animae.exe"
Name: "{commondesktop}\Scriptum Animae"; Filename: "{app}\scriptum_animae.exe"

[Run]
Filename: "{app}\scriptum_animae.exe"; Description: "Abrir Scriptum Animae"; Flags: nowait postinstall skipifsilent
