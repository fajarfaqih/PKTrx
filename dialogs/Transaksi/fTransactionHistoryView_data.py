import com.ihsan.foundation.pobjecthelper as phelper
import sys,os

MAX_TRANSACTION = 20
MAX_DETAIL = 10

def FormSetDataEx(uideflist, parameter):
  config = uideflist.config

  if (parameter.DatasetCount == 0 or
    parameter.GetDataset(0).Structure.StructureName != 'data'):
    return
  else:
    #-- routine untuk SetDataWithParameters
    helper = phelper.PObjectHelper(config, 'default')
    param = parameter.FirstRecord
    TransactionId = param.TransactionId
    uideflist.SetData('uipTransaction','PObj:Transaction#TransactionId=%d ' % TransactionId)
    rec = uideflist.uipTransaction.Dataset.GetRecord(0)
    rec.IsPostedMir = rec.IsPosted
    
    recData = uideflist.uipData.Dataset.AddRecord()
    recData.user_id = config.SecurityContext.InitUser

def JurnalTransaksi(config, params, returns):
  helper = phelper.PObjectHelper(config)
  status = returns.CreateValues(
    ["Is_Err",0],
    ["Err_Message",""])
    
  data = params.FirstRecord
  try :
    oTran = helper.GetObject('Transaction', data.TransactionId)
    #if oTran.IsPosted == 'T':
    #  status.Is_Err = 1
    #  status.Err_Message = 'Transaksi sudah diposting'
    #else:
    st, errmsg = oTran.CreateJournal()
    status.Is_Err = st
    status.Err_Message = errmsg
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
    
def JurnalUlangTransaksi(config, params, returns):
  helper = phelper.PObjectHelper(config)
  status = returns.CreateValues(
    ["Is_Err",0],
    ["Err_Message",""])

  data = params.FirstRecord

  try :
    oTran = helper.GetObject('Transaction', data.TransactionId)
    TranHelper = helper.LoadScript('Transaction.TransactionHelper')
    TranHelper.DeleteTransactionJournal(oTran)
    
    st, errmsg = oTran.CreateJournal()
    status.Is_Err = st
    status.Err_Message = errmsg
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])

