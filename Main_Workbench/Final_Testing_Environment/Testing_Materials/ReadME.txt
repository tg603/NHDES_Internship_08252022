Instructions for my tasks:
Inside task scheduler I need two tasks,

the first needs to be called Automatic PA Pull
	In the general tab:
		it needs to run whether the user is logged on or not 
		Configure for Windows 10 or whatever the server is 
	In the trigger tab:
		Needs to start today and run every ten minutes
		Please make the time start off by 1 minute like: 10:01:00 AM 
		Recurs Daily and repeat task every 10 minutes
		Stop task if it runs longer than 30 minutes
		The duration needs to be indefinently
	In the action tab:
		Start a program
		This program will be the starter.vbs inside the S: drive shortcut
		Leave add arguments and start in blank
	In the conditions tab
		You'll know more then me on this but I believe a server runs all the time
		I don't think you'll need to wake the computer to run this task?
		This program needs to run overnight.
	In the settings tab:
		Run the task as soon as possible after a scheduled start is missed
		Stop the task if it runs longer than 1 hour

the second needs to be called Automatic PA Archive
	In the general tab:
		it needs to run whether the user is logged on or not 
		Configure for Windows 10 or whatever the server is 
	In the trigger tab:
		Needs to start today at 11:55:00 PM
		Recurs Daily once a day at this scheduled time
		Stop task if it runs longer than 30 minutes
	In the action tab:
		Start a program
		This program will be the move.bat inside the S: drive shortcut
		Leave add arguments and start in blank
	In the conditions tab
		You'll know more then me on this but I believe a server runs all the time
		I don't think you'll need to wake the computer to run this task?
		This program needs to run overnight.
	In the settings tab:
		Stop the task if it runs longer than 1 hour