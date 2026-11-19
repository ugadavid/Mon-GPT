#define ProductName "Mon GPT<3"
#define Publisher "Trucabule"
#define Executable "Mon-GPT.exe"
#define AppDirectory "{localappdata}\Programs\Mon GPT"

[Setup]
AppId={{CB03F13E-8F70-49A0-9678-B6D84D760E7D}
AppName={#ProductName}
AppVersion={#ProductVersion}
AppPublisher={#Publisher}
AppPublisherURL=https://www.trucabule.fr/
VersionInfoVersion={#WindowsVersion}
VersionInfoProductVersion={#WindowsVersion}
VersionInfoTextVersion={#WindowsVersion}
VersionInfoProductTextVersion={#ProductVersion}
VersionInfoProductName={#ProductName}
VersionInfoCompany={#Publisher}
DefaultDirName={#AppDirectory}
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64os
ArchitecturesInstallIn64BitMode=x64os
SetupArchitecture=x64
UseSetupLdr=x64
MinVersion=10.0
SetupIconFile={#IconFile}
UninstallDisplayName={#ProductName}
UninstallDisplayIcon={app}\{#Executable}
AppMutex=Local\Trucabule.MonGPT.Running
SetupMutex=Local\Trucabule.MonGPT.Maintenance
CloseApplications=no
RestartApplications=no
WizardStyle=modern
Compression=lzma2
SolidCompression=yes
OutputDir={#OutputDir}
OutputBaseFilename=Mon-GPT-{#ProductVersion}-windows-x64-setup

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Les caractères < et > ne sont pas autorisés dans un nom de fichier Windows.
Name: "{userprograms}\Mon GPT"; Filename: "{app}\{#Executable}"; WorkingDir: "{app}"; IconFilename: "{app}\{#Executable}"; AppUserModelID: "Trucabule.MonGPT"
Name: "{userdesktop}\Mon GPT"; Filename: "{app}\{#Executable}"; WorkingDir: "{app}"; IconFilename: "{app}\{#Executable}"; Tasks: desktopicon; AppUserModelID: "Trucabule.MonGPT"

[Run]
Filename: "{app}\{#Executable}"; Description: "{cm:LaunchProgram,{#ProductName}}"; Flags: nowait postinstall skipifsilent

[Code]
function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  if CompareText(RemoveBackslashUnlessRoot(ExpandConstant('{app}')),
     RemoveBackslashUnlessRoot(ExpandConstant('{#AppDirectory}'))) <> 0 then
    Result := 'Mon GPT<3 doit être installé dans AppData\Local\Programs\Mon GPT.';
end;
