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

  param = parameter.FirstRecord
    
  oTran = helper.GetObject('Transaction',param.TransactionId)

  if oTran.isnull : raise '','Data Transaksi Tidak Ditemukan'
    
  oTran.DeleteJournal()

  config.BeginTransaction()
  try:
    # oInbox = helper.GetObjectByNames('InboxTransaction',{'TransactionId':oTran.TransactionId})
    # if not oInbox.isnull :      
    #   oInbox.Delete()
    # oTran.DeleteTransactionItem()
    
    # sSQL = "delete from transaction.transaction where transactionid=%d" % oTran.TransactionId
    # sqlRes = config.ExecSQL(sSQL)
    # if sqlRes == -9999:
    #   raise "SQL Error", config.GetDBConnErrorInfo()
    oTran.Delete()
    
    config.Commit()
  except :
    config.Rollback()
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
  #--end try

  return 1
