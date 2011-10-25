import com.ihsan.foundation.pobjecthelper as phelper
import sys

def DAFScriptMain(config, parameter, returnpacket):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)

  helper = phelper.PObjectHelper(config)

  status = returnpacket.CreateValues(
        ['Is_Err',0],
        ['Err_Message',''],
      )

  config.BeginTransaction()
  try:
    param = parameter.FirstRecord
    
    oTran = helper.GetObject('Transaction',param.TransactionId)

    if oTran.isnull : raise '','Data Transaksi Tidak Ditemukan'
    oTran.Delete()
    
    config.Commit()
    
  except :
    config.Rollback()
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
  #--end try

  return 1

