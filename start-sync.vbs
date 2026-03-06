Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell.exe -ExecutionPolicy Bypass -File ""C:\Users\Sam\Desktop\hkt\autosync.ps1""", 0, False
