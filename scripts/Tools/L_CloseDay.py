import com.ihsan.foundation.pobjecthelper as phelper
import time
import sys
import com.ihsan.util.logsvrclient as lclib


def Main(config,param):
  helper = phelper.PObjectHelper(config)
    
  # Validasi parameter input  
  if param.LastCloseDate >= param.ProcessDate :
    raise 'PERINGATAN','Tanggal proses harus lebih besar dari tanggal tutup buku terakhir'

  if param.ProcessDate > config.Now():
    raise 'PERINGATAN','Tanggal proses tidak boleh lebih besar dari tanggal hari ini'

  app = config.AppObject
  params = app.CreateValues(["param_date",param.ProcessDate])
  

  oBP = helper.CreateObject("BPHelper")  
  oBP.DoExecute("CLOSEDAY",params)
      
def DAFScriptMain(config,params,returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message','']
  )

  param = params.FirstRecord
  config.BeginTransaction()
  try:
    Main(config,param)
    config.Commit()
  except:
    config.Rollback()
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])

  
def DAFLongScriptMain(config, parameter, pid, monfilename):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # pid: Process ID of this script
  # monfilename: Monitor file name to store status
  
  app = config.AppObject
  consoleID = 'closeday_' + str(pid)
  
  sJobName = '%s. TaskID = %s ' % ('Proses Tutup Buku Accounting',pid)  
  app.WriteConsole(sJobName + ': Proses akan dimulai\r\n')
  param = params.FirstRecord
  #config.BeginTransaction()
  #helper = phelper.PObjectHelper(config)
  try:  
        
    app.CreateConsole(consoleID, 'progress')
    try:      
      app.SwitchDefaultConsole(consoleID)      
      progress = config.ProgressTracker
      progress.ProgressLevel1()

      app.WriteConsole(sJobName + ': Proses Tutup Buku akan dimulai\r\n')
      progress.SetProgressInfo2(1, 'Proses Tutup Buku akan dimulai')
      time.sleep(4)
                  
      #main task right here      
      for i in range(10):
        app.WriteConsole(sJobName + 'Memproses ke-%d \r\n' % (i+1))
        progress.SetProgressInfo2(1, 'Memproses ke-%d' % (i+1))
        time.sleep(2)

      app.WriteConsole(sJobName + ': telah selesai\r\n')
    finally:
      app.CloseConsole(consoleID)
  except:
    app.WriteConsole(sJobName + ': Error\r\n' + str(sys.exc_info()[1]) + '\r\n')
    raise
    
