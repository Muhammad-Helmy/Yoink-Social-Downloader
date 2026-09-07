; Inno Setup Script for Yoink Social
; Made by Heru
; Target: Windows 10/11 (x64)

#define MyAppName "Yoink Social"
#define MyAppVersion "1.0"
#define MyAppPublisher "Heru"
#define MyAppExeName "YoinkSocial.exe"
#define MyAppAssocName MyAppName + " Video Downloader"

[Setup]
AppId={{E1A78B42-4931-4F25-86FA-E923C91079F2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Yoink Social
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\dist_installer
OutputBaseFilename=YoinkSocial_Setup_v1.0
SetupIconFile=..\assets\icons\app_icon.ico
WizardSmallImageFile=..\assets\icons\wizard_small.bmp
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Dist files compiled by PyInstaller (onedir mode)
Source: "..\dist\YoinkSocial\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Ensure standalone app_icon.ico exists directly in {app}\assets\icons for external shortcut references
Source: "..\assets\icons\app_icon.ico"; DestDir: "{app}\assets\icons"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; AppUserModelID: "yoink.social.downloader.pro.1.0"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; AppUserModelID: "yoink.social.downloader.pro.1.0"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
