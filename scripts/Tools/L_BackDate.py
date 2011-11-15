import com.ihsan.foundation.pobjecthelper as phelper
import time
import sys
import com.ihsan.util.logsvrclient as lclib


def Main(config,param):
  helper = phelper.PObjectHelper(config)
    
  # Validasi parameter input  
  if param.LastCloseDate < param.ProcessDate :
    raise 'PERINGATAN','Tanggal buka harus lebih kecil atau sama dengan tanggal tutup buku terakhir'

  if param.ProcessDate > config.Now():
    raise 'PERINGATAN','Tanggal proses tidak boleh lebih besar dari tanggal hari ini'

  app = config.AppObject
  params = app.CreateValues(["param_date",param.ProcessDate])
  
  oBP = helper.CreateObject("BPHelper")  
  oBP.DoExecute("BACKDATE",params)
  
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
  
