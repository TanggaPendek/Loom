# Deployment Strategy

This document outlines the future deployment strategy for packaging Loom as a single executable application for Windows.

> [!NOTE]
> This is a **planning document only**. Implementation will occur in a future development phase after core features are stable.

## Goals

Create a comprehensive single-app installation that:
- Pulls code from GitHub repository for updates
- Runs backend server (serves both API and frontend static files)
- Backend manages engine execution as subprocess
- Packages as Windows .exe executable
- Provides auto-update capability
- Enables one-click installation

##Architecture

```
Loom.exe
├── Backend (FastAPI)
│   ├── Serves Frontend (static files from /frontend/dist)
│   ├── API endpoints (/api/*)
│   └── Manages Engine subprocess
└── Engine (Python subprocess)
    └── Executes node graphs with virtual environments
```

### Component Breakdown

#### 1. Backend Server
- **Framework**: FastAPI (current)
- **Responsibilities**:
  - Serve frontend static files
  - Handle API requests
  - Manage engine subprocess lifecycle
  - Update check and download
- **Port**: 8000 (configurable via settings)

#### 2. Frontend
- **Build Process**: `npm run build` in `/frontend`
- **Output**: Static files in `/frontend/dist`
- **Served by**: Backend at `/` path
- **API Calls**: Relative paths to `/api/*`

#### 3. Engine
- **Launch**: Subprocess via `subprocess.Popen`
- **Communication**: File-based (state.json, logs.json)
- **Isolation**: Runs in project-specific virtual environments

## Packaging Strategy

### Technology Choice: PyInstaller vs Nuitka

| Feature | PyInstaller | Nuitka |
|---------|-------------|---------|
| Compilation Speed | Fast | Slow (first time) |
| Executable Size | ~150MB | ~80MB |
| Startup Time | ~2-3s | ~1s |
| Python Compat | Excellent | Good |
| Maintenance | Active | Active |
| **Recommendation** | ✅ Use This | Future consideration |

**Decision**: Use PyInstaller for initial release due to:
- Faster iteration during development
- Better Python 3.11+ compatibility
- Simpler build configuration
- Well-documented Flask/FastAPI packaging

### PyInstaller Configuration

```python
# loom.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Collect all data files
frontend_dist = Tree('frontend/dist', prefix='frontend/dist')
nodebank = Tree('nodebank', prefix='nodebank')
executor = Tree('executor', prefix='executor')

a = Analysis(
    ['backend/src/main_backend.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('frontend/dist', 'frontend/dist'),
        ('nodebank', 'nodebank'),
        ('executor', 'executor'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops.auto',
        'uvicorn.protocols.http.auto',
        'fastapi',
        'pydantic',
        'multipart',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Loom',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/loom_icon.ico',
    version='version_info.txt'
)
```

### Build Command

```bash
# Install pyinstaller
pip install pyinstaller

# Build executable
pyinstaller loom.spec --clean

# Output: dist/Loom.exe (~150MB)
```

## Frontend Integration

### Build Process

1. **Build frontend**:
   ```bash
   cd frontend
   npm install
   npm run build
   # Outputs to frontend/dist/
   ```

2. **Backend serves static files**:
   ```python
   # backend/src/main_backend.py
   from fastapi.staticfiles import StaticFiles
   from pathapi import HTMLResponse
   import os
   
   # Determine if running as exe or dev
   if getattr(sys, 'frozen', False):
       # Running as exe
       frontend_path = Path(sys._MEIPASS) / "frontend" / "dist"
   else:
       # Running from source
       frontend_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
   
   # Serve frontend
   app.mount("/assets", StaticFiles(directory=frontend_path / "assets"), name="assets")
   
   @app.get("/", response_class=HTMLResponse)
   async def serve_frontend():
       index_file = frontend_path / "index.html"
       return index_file.read_text()
   
   # Catch-all for SPA routing
   @app.get("/{full_path:path}", response_class=HTMLResponse)
   async def serve_spa(full_path: str):
       # Return index.html for all non-API routes
       if not full_path.startswith("api"):
           index_file = frontend_path / "index.html"
           return index_file.read_text()
   ```

### Frontend Build Configuration

Update `vite.config.js` for relative paths:

```javascript
// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',  // Served from root by backend
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // Generate source maps for debugging
    sourcemap: true,
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

## Auto-Update Mechanism

### GitHub Releases Integration

```python
# backend/src/modules/updater.py
import requests
import subprocess
import sys
from pathlib import Path
from packaging import version as pkg_version

class AutoUpdater:
    GITHUB_REPO = "YourUsername/Loom"
    CURRENT_VERSION = "1.0.0"  # Read from version file
    
    def check_for_updates(self) -> dict:
        """Check GitHub for newer releases."""
        try:
            url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"
            response = requests.get(url, timeout=5)
            release = response.json()
            
            latest_version = release['tag_name'].lstrip('v')
            
            if pkg_version.parse(latest_version) > pkg_version.parse(self.CURRENT_VERSION):
                return {
                    "update_available": True,
                    "version": latest_version,
                    "download_url": self._get_download_url(release),
                    "release_notes": release['body']
                }
            
            return {"update_available": False}
        except Exception as e:
            print(f"Update check failed: {e}")
            return {"update_available": False, "error": str(e)}
    
    def _get_download_url(self, release: dict) -> str:
        """Extract Windows .exe download URL from release assets."""
        for asset in release.get('assets', []):
            if asset['name'].endswith('.exe'):
                return asset['browser_download_url']
        return None
    
    def download_and_install(self, download_url: str):
        """Download new version and trigger installation."""
        temp_path = Path.home() / "Downloads" / "Loom_Update.exe"
        
        # Download
        response = requests.get(download_url, stream=True)
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Launch installer and exit current app
        subprocess.Popen([str(temp_path), '/SILENT'])
        sys.exit(0)
```

### Update UI Flow

1. **On Startup**: Check for updates (async, non-blocking)
2. **Notification**: Show toast/modal if update available
3. **User Action**: "Update Now" button
4. **Download**: Progress bar in modal
5. **Install**: Close app \u2192 launch installer \u2192 installer replaces .exe

## Installation Package

### Inno Setup Configuration

```ini
; installer.iss
[Setup]
AppName=Loom
AppVersion=1.0.0
DefaultDirName={autopf}\Loom
DefaultGroupName=Loom
OutputDir=installer_output
OutputBaseFilename=Loom_Setup_1.0.0
Compression=lzma2/max
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Files]
Source: "dist\Loom.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Loom"; Filename: "{app}\Loom.exe"
Name: "{autodesktop}\Loom"; Filename: "{app}\Loom.exe"
Name: "{group}\Uninstall Loom"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\Loom.exe"; Description: "Launch Loom"; Flags: postinstall nowait skipifsilent

[Code]
// Custom code to create userdata folder on first run
procedure CurStepChanged(CurStep: TSetupStep);
var
  UserDataPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    UserDataPath := ExpandConstant('{localappdata}\Loom\userdata');
    ForceDirectories(UserDataPath);
  end;
end;
```

### Build Installer

```bash
# Install Inno Setup
# Download from: https://jrsoftware.org/isinfo.php

# Compile installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss

# Output: installer_output/Loom_Setup_1.0.0.exe
```

## Deployment Workflow

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/release.yml
name: Build and Release

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install Python dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install pyinstaller
    
    - name: Build frontend
      run: |
        cd frontend
        npm install
        npm run build
    
    - name: Build executable
      run: |
        pyinstaller loom.spec --clean
    
    - name: Build installer
      run: |
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
    
    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: |
          installer_output/Loom_Setup_*.exe
          dist/Loom.exe
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Release Process

1. **Version Bump**: Update version in `version.txt`
2. **Tag Release**: `git tag v1.0.0 && git push origin v1.0.0`
3. **GitHub Action**: Automatically builds and creates release
4. **Manual QA**: Test installer on clean Windows machine
5. **Publish**: Make release public on GitHub

## Configuration Management

### User Settings Location

```python
# Determine userdata path based on environment
import os
from pathlib import Path

def get_userdata_path() -> Path:
    if getattr(sys, 'frozen', False):
        # Running as exe - use AppData
        return Path(os.getenv('LOCALAPPDATA')) / 'Loom' / 'userdata'
    else:
        # Running from source - use project folder
        return Path(__file__).parent.parent.parent / 'userdata'

USERDATA_PATH = get_userdata_path()
STATE_PATH = USERDATA_PATH / 'state.json'
SETTINGS_PATH = USERDATA_PATH / 'settings.json'
```

### Settings File

```json
// %LOCALAPPDATA%\Loom\userdata\settings.json
{
  "server": {
    "port": 8000,
    "host": "127.0.0.1",
    "auto_open_browser": true
  },
  "updates": {
    "check_on_startup": true,
    "auto_download": false
  },
  "engine": {
    "max_parallel_projects": 1,
    "default_python_version": "3.11"
  }
}
```

## Distribution

### Hosting Options

1. **GitHub Releases** (Free)
   - Pros: Free, integrated with CI/CD, version control
   - Cons: Rate limiting, large files slow
   - **Recommended for initial release**

2. **SourceForge** (Free)
   - Pros: CDN, fast downloads, reliable
   - Cons: Ads, legacy platform

3. **Custom CDN** (Paid)
   - Pros: Full control, branding, analytics
   - Cons: Costs ~$20/month
   - Use for production after user base grows

### Download Page

Create `loom-website` repo with GitHub Pages:

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
  <title>Loom - Visual Programming Tool</title>
</head>
<body>
  <h1>Download Loom</h1>
  <a href="https://github.com/YourUsername/Loom/releases/latest/download/Loom_Setup.exe">
    <button>Download for Windows</button>
  </a>
  
  <h2>Features</h2>
  <ul>
    <li>Visual node-based programming</li>
    <li>Custom Python nodes</li>
    <li>Real-time execution</li>
  </ul>
</body>
</html>
```

## Security Considerations

### Code Signing

1. **Get Certificate**: Purchase from DigiCert, Sectigo, or use free options
2. **Sign Executable**:
   ```bash
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com /fd SHA256 dist/Loom.exe
   ```
3. **Benefits**: Removes Windows SmartScreen warnings

### User Data Protection

- Store all user data in `%LOCALAPPDATA%\Loom\`
- Never write to Program Files after installation
- Encrypt sensitive settings (future: API keys, credentials)

## Performance Optimization

### Startup Time

- **Current**: ~3 seconds (PyInstaller with all dependencies)
- **Target**: <2 seconds

Optimizations:
1. Lazy-load heavy modules (numpy, pandas)
2. Pre-compile frontend templates
3. Cache node index on first load

### Memory Usage

- **Backend**: ~50MB base + ~20MB per active project
- **Engine**: ~30MB base + variable per venv
- **Total**: ~100MB for typical usage

## Future Enhancements

1. **Cross-Platform**: macOS (.app), Linux (.AppImage)
2. **Plugin System**: Allow third-party node packages
3. **Cloud Sync**: Optional project backup to cloud
4. **Telemetry**: Anonymous usage statistics (opt-in)
5. **License Management**: Commercial vs. free tiers

## Appendix: File Structure of Packaged App

```
Loom.exe                    # Main executable (~150MB)
├── _internal/              # PyInstaller dependencies (hidden)
│   ├── Python311.dll
│   ├── base_library.zip
│   └── ...
└── (embedded data)
    ├── frontend/dist/
    │   ├── index.html
    │   └── assets/
    ├── nodebank/
    ├── executor/
    └── .env.example

# Separate user data directory:
%LOCALAPPDATA%\Loom\
└── userdata/
    ├── state.json
    ├── settings.json
    ├── folderindex.json
    ├── engine_state.json
    └── ProjectName/
        ├── savefile.json
        ├── logs.json
        └── .venv/
```

## Conclusion

This deployment strategy provides a professional, user-friendly installation experience for Windows users. The auto-update mechanism ensures users always have the latest features and bug fixes, while the single-executable approach simplifies distribution.

### Implementation Timeline

- **Phase 1** (Week 1-2): Set up PyInstaller configuration
- **Phase 2** (Week 3): Integrate frontend build process
- **Phase 3** (Week 4): Implement auto-updater
- **Phase 4** (Week 5): Create Inno Setup installer
- **Phase 5** (Week 6): Set up CI/CD pipeline
- **Phase 6** (Week 7): Beta testing with Windows users
- **Phase 7** (Week 8): Code signing and public release
