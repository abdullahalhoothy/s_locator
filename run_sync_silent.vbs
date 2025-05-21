' Silent PowerShell Script Runner for s_locator sync
' Runs the sync script without any visible windows

Dim objShell
Set objShell = CreateObject("WScript.Shell")

' Run PowerShell script completely hidden
objShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File ""F:\git\s_locator\sync.ps1""", 0, False

Set objShell = Nothing
