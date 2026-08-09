; Inno Setup script — Richard OS installer (produces RichardOS_Setup.exe on Windows)
; Build with:  iscc RichardOS_Setup.iss   (Inno Setup 6, https://jrsoftware.org/isinfo.php)
#define MyAppName "Richard OS"
#define MyAppVersion "7.2.1"
#define MyAppPublisher "Sujith Richard"
#define MyAppExeName "native_launcher.py"

[Setup]
AppId={{RICHARD-OS-7A2B-4C3D-9E1F-000000000001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Richard OS
DefaultGroupName=Richard OS
OutputDir=.\output
OutputBaseFilename=Richard_OS_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: selected
Name: "startmenuicon"; Description: "Create a Start-menu shortcut"; Flags: selected

[Files]
; include the whole richard-os folder (the server + UI + install/linux script)
Source: "..\..\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs; Excludes: ".venv,target,.git,__pycache__"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{python}\python.exe"; Parameters: "{app}\scripts\desktop_launcher.py"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{python}\python.exe"; Parameters: "{app}\scripts\desktop_launcher.py"; Tasks: desktopicon

[Run]
Filename: "{cmd}"; Parameters: "/c cd /d ""{app}"" && python -m venv .venv && .venv\\Scripts\\pip install -r requirements.txt"; Flags: runhidden; WorkingDir: "{app}"
Filename: "{cmd}"; Parameters: "/c cd /d ""{app}"" && .venv\\Scripts\\python scripts\\verify_install.py"; Flags: runhidden; WorkingDir: "{app}"; StatusMsg: "Verifying installation..."

[Code]
// STAGE 1: Terms & Conditions — accept checkbox before continuing
procedure InitializeWizard();
var
  Page: TWizardPage;
  AgreeBox: TNewCheckBox;
begin
  Page := CreateCustomPage(wpWelcome, 'Terms and Conditions', 'Please accept to continue');
  AgreeBox := TNewCheckBox.Create(Page);
  AgreeBox.Parent := Page.Surface;
  AgreeBox.Left := 8; AgreeBox.Top := 8; AgreeBox.Width := 480;
  AgreeBox.Caption := 'I agree to the MIT License and terms in docs/PORTFOLIO.md (Richard OS).';
  Page.Enabled := False;  // block Next until accepted? (see NextButton logic)
end;
