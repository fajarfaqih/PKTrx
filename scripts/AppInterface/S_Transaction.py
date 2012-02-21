import com.ihsan.foundation.pobjecthelper as phelper
import sys

def GetInfoTransaction(config, params, returns):
  status = returns.CreateValues(
    ['Is_Error',0],['Error_Message',''],['TransactionNo', '']
  )
  config.BeginTransaction()
  try:
    helper = phelper.PObjectHelper(config)

    JournalBlockId = params.FirstRecord.id_journalblock
    oTransaction = helper.GetObjectByNames('Transaction',{'JournalBlockId' : JournalBlockId})

    if oTransaction.isnull : raise '','Info Transaksi Tidak Ditemukan'
    status.TransactionNo = oTransaction.TransactionNo

  except:
    config.Rollback()
    status.Is_Error = 1
    status.Error_Message = str(sys.exc_info()[1])
    config.SendDebugMsg(status.Error_Message)