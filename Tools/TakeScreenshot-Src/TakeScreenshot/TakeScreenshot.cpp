// TakeScreenshot.cpp : Definiert den Einstiegspunkt für die Konsolenanwendung.
//
// Original example written by Ted Burke - last updated 17-4-2012

#include "stdafx.h"

// Because the SendInput function is only supported in
// Windows 2000 and later, WINVER needs to be set as
// follows so that SendInput gets defined when windows.h
// is included below.
//#define WINVER 0x0500
#include <windows.h>

int _tmain(int argc, _TCHAR* argv[])
{	
	// This structure will be used to create the keyboard
    // input event.
    INPUT ip;
 
    //Sleep(1000);
 
    // Set up a generic keyboard event.
    ip.type = INPUT_KEYBOARD;
    ip.ki.wScan = 0; // hardware scan code for key
    ip.ki.time = 0;
    ip.ki.dwExtraInfo = 0;
 
    // Press the "Print Screen" key
    //ip.ki.wVk = 0x41; // virtual-key code for the "a" key
	ip.ki.wVk =  0x2C; // Print Screen code
    ip.ki.dwFlags = 0; // 0 for key press
    SendInput(1, &ip, sizeof(INPUT));
 
	Sleep(100);
    // Release the key
    ip.ki.dwFlags = KEYEVENTF_KEYUP; // KEYEVENTF_KEYUP for key release
    SendInput(1, &ip, sizeof(INPUT));
 
    // Exit normally
    return 0;
}

