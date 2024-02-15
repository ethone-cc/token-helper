"""
Full credit for the code below to https://github.com/yllhwa
Issue link: https://github.com/r0x0r/pywebview/issues/1310#issue-2089437915
"""

import ctypes
import ctypes.wintypes
import win32process, win32gui
import os

def DwmSetWindowAttribute(hwnd, attr, value, size=4):
    DwmSetWindowAttribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
    DwmSetWindowAttribute.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.DWORD, ctypes.c_void_p, ctypes.wintypes.DWORD]
    return DwmSetWindowAttribute(hwnd, attr, ctypes.byref(ctypes.c_int(value)), size)

def ExtendFrameIntoClientArea(hwnd):

    class _MARGINS(ctypes.Structure):
        _fields_ = [("cxLeftWidth", ctypes.c_int),
                    ("cxRightWidth", ctypes.c_int),
                    ("cyTopHeight", ctypes.c_int),
                    ("cyBottomHeight", ctypes.c_int)
                    ]

    DwmExtendFrameIntoClientArea = ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea
    m = _MARGINS()
    m.cxLeftWidth = 1
    m.cxRightWidth = 1
    m.cyTopHeight = 1
    m.cyBottomHeight = 1
    return DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(m))

def get_hwnds_for_pid(pid):
    hwnds = []
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
            return True
    win32gui.EnumWindows(callback, hwnds)
    return hwnds

def setup_all_windows_borderless():
    hwnds = get_hwnds_for_pid(os.getpid())
    print(hwnds)
    for hwnd in hwnds:
        DwmSetWindowAttribute(hwnd, 2, 2, 4)
        ExtendFrameIntoClientArea(hwnd)