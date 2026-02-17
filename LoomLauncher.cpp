#include <windows.h>
#include <stdlib.h>

int APIENTRY WinMain(HINSTANCE hInst, HINSTANCE hPrev, LPSTR lpCmd, int nShow) {
    // This looks for Launcher.py in the same folder as the .exe
    // 'pythonw' ensures the app runs without a black console window popping up
    system("start /b pythonw Launcher.py");
    return 0;
}