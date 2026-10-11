; Inno Setup Script for AlchMate - OSRS High Alchemy & Crafting Profit Dashboard
; Download Inno Setup from: https://jrsoftware.org/isdl.php

#define MyAppName "AlchMate"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "AlchMate"
#define MyAppURL "https://github.com/jef11222/osrs-alch-tracker"
#define MyAppExeName "AlchMate.exe"

[Setup]
; App Metadata
AppId={{9FA16BAF-A2EA-4125-83A8-B6E8D1B33BF9}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases

; Default Installation Directory: %LocalAppData%\Programs\... (No Admin Rights Required)
DefaultDirName={localappdata}\Programs\AlchMate
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output Settings
OutputDir=dist
OutputBaseFilename=AlchMate_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; Windows Settings
PrivilegesRequired=lowest
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "bridge_plugin\AlchBridgePlugin.jar"; DestDir: "{app}\plugins"; Flags: ignoreversion
Source: "bridge_plugin\AlchBridgePlugin.jar"; DestDir: "{%USERPROFILE}\.runelite\plugins"; Flags: ignoreversion; Check: DirExists(ExpandConstant('{%USERPROFILE}\.runelite\plugins'))
Source: "README.md"; DestDir: "{app}"; Flags: isreadme
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  UninstPath: String;
  ResultCode: Integer;
  MsgRes: Integer;
begin
  Result := True;
  UninstPath := ExpandConstant('{localappdata}\Programs\AlchMate\unins000.exe');
  if not FileExists(UninstPath) then
    UninstPath := ExpandConstant('{localappdata}\Programs\OSRS Alch Tracker\unins000.exe');

  if FileExists(UninstPath) then
  begin
    MsgRes := MsgBox(
      'An existing installation of AlchMate / OSRS Alch Tracker was detected on your PC.' + #13#10 + #13#10 +
      'What would you like to do?' + #13#10 + #13#10 +
      '• Click YES to REPAIR / REINSTALL (fixes files and restores shortcuts)' + #13#10 +
      '• Click NO to UNINSTALL (removes the app from your computer)' + #13#10 +
      '• Click CANCEL to exit',
      mbConfirmation,
      MB_YESNOCANCEL
    );

    if MsgRes = IDYES then
    begin
      // Continue installation to repair and overwrite
      Result := True;
    end
    else if MsgRes = IDNO then
    begin
      // Launch uninstaller
      Exec(UninstPath, '', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
      Result := False; // Exit setup wizard after uninstalling
    end
    else
    begin
      // User clicked Cancel
      Result := False;
    end;
  end;
end;
