Sub Start()
	On Error Resume Next 
	Set fso = CreateObject("Scripting.FileSystemObject")
	address = "C:\Users\zachary.t.thoroughgo\DES\Demo\start.bat"
	If fso.FileExists(address) Then
		Rem MsgBox("This Address Exists")
		Set shell = WScript.CreateObject("WScript.shell")
		shell.Run(address), 0, True
		WScript.quit
	Else
		MsgBox("Address of file is Wrong")
		WScript.quit
	End If
End Sub
Start