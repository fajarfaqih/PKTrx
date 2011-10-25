# example to read from log file and stream it to the console continously
# written by IK

LOG_FILE_BASE = "c:\\logs\\console\\logsvr\\"
APPSERVER_FILE_BASE = "c:\\logs\\appserver\\dafsocksvr.exe\\"

import pywintypes
import win32file
import time

def DAFScriptMain(config, parameter, returnpacket):
  app = config.AppObject
  app.ConCreate()

  logChannelName = parameter.FirstRecord.logChannelName
  logServerPort = parameter.FirstRecord.logServerPort
  if logChannelName == '@': #appserver log
    sdatetime = config.FormatDateTime('yyyy|mmm|dd', config.Now())
    sPath = '\\'.join(sdatetime.split('|'))
    logFileName = APPSERVER_FILE_BASE + sPath + '.log'
  else:
    logFileName = LOG_FILE_BASE + logChannelName + "\\" + str(logServerPort) + ".log"
  #--

  uLogFileName = pywintypes.Unicode(logFileName)
  logFile = win32file.CreateFile(uLogFileName, win32file.GENERIC_READ, win32file.FILE_SHARE_WRITE | win32file.FILE_SHARE_READ,
    None, win32file.OPEN_EXISTING, 0, None)

  app.ConWriteln("Log file opened")
  app.ConWriteln("---------------")
  
  try:
    win32file.SetFilePointer(logFile, 0, win32file.FILE_END)
    while 1:
      readRes = win32file.ReadFile(logFile, 512)
      if readRes[0] == 0:
        sRes = readRes[1]
        if len(sRes) != 0:
          app.ConWrite(readRes[1])
        else:
          time.sleep(0.5)
          pos = win32file.SetFilePointer(logFile, 0, win32file.FILE_CURRENT)
          size = win32file.GetFileSize(logFile)
          if pos > size:
            win32file.SetFilePointer(logFile, 0, win32file.FILE_END)
          #-- if
        #-- else
      else:
        break
      #-- else
    # -- while
  finally:
    logFile.Close()
  #--
  return 1
#-- def
