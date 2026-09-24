; installer.iss

[Setup]
AppName=Smart Music and Video Downloader
AppVersion=1.0.0
DefaultDirName={autopf}\SmartMusicVideoDownloader
DefaultGroupName=Smart Music and Video Downloader
OutputBaseFilename=SmartMusicVideoDownloaderSetup
OutputDir=Output
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\SmartMusicVideoDownloader.exe
DisableProgramGroupPage=yes
DisableDirPage=auto

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\SmartMusicVideoDownloader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Smart Music and Video Downloader"; Filename: "{app}\SmartMusicVideoDownloader.exe"; IconFilename: "{app}\SmartMusicVideoDownloader.exe"
Name: "{autodesktop}\Smart Music and Video Downloader"; Filename: "{app}\SmartMusicVideoDownloader.exe"; IconFilename: "{app}\SmartMusicVideoDownloader.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SmartMusicVideoDownloader.exe"; Description: "Launch Smart Music and Video Downloader"; Flags: nowait postinstall skipifsilent
