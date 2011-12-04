import com.ihsan.foundation.pobjecthelper as phelper
import sys
import simplejson


def FormSetDataEx(uideflist, params) :
  config = uideflist.config
  helper = phelper.PObjectHelper(config)

  if params.GetDatasetByName('trparam') != None :
    oForm = helper.CreateObject('FormTransaksi')
    st = oForm.SetDataEx(uideflist,params)

    return st

  Now = config.Now()
  rec = uideflist.uipTransaction.Dataset.AddRecord()
  rec.Inputer = str(config.SecurityContext.UserId)
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])
  rec.TransactionDate = int(Now)
  rec.FloatTransactionDate = int(Now)
  rec.ActualDate = int(Now)
  rec.Amount = 0.0
  rec.ReceivedFrom = rec.Inputer
  
  # Set Transaction Number
  #oService = helper.LoadScript('Transaction.TransactionHelper')
  rec.TransactionNo = '<AUTOGENERATED>' #oService.GetTransactionNumber(config,'CA')
  
def SimpanData(config, params, returns):
  IsErr = 0
  ErrMessage = ''
  TransactionNo = ''
  StreamName = ''
  
  helper = phelper.PObjectHelper(config)
  try :
    oTransaction = params.uipTransaction.GetRecord(0)

    request = {}
    request['ActualDate'] = oTransaction.ActualDate
    request['CashAccountNo'] = oTransaction.GetFieldByName('LCashAccount.AccountNo')
    request['Amount'] = oTransaction.Amount
    request['ReferenceNo'] = oTransaction.ReferenceNo
    request['Description'] = oTransaction.Description
    request['Rate'] = 1.0
    request['Inputer'] = config.SecurityContext.InitUser
    request['BranchCode'] = config.SecurityContext.GetUserInfo()[4]
    request['TransactionNo'] = oTransaction.TransactionNo
    request['ReceivedFrom'] = oTransaction.ReceivedFrom
    request['CostAccountNo'] = oTransaction.GetFieldByName('LCostAccount.Account_Code')
    request['CPIACatId'] = oTransaction.GetFieldByName('LCPIACategory.CPIACatId')
    request['HasContract'] = oTransaction.HasContract
    request['ContractNo'] = oTransaction.ContractNo
    request['ContractEndDate'] = oTransaction.ContractEndDate

    sRequest = simplejson.dumps(request)


    oService = helper.LoadScript('Transaction.GeneralTransaction')

    TransactionCode = 'CPIA'
    if oTransaction.ShowMode == 1:
      response = oService.CreateTransaction(TransactionCode, config, sRequest, params)
    else:
      response = oService.UpdateTransaction(TransactionCode, config, sRequest, params)
    # end if

    response = simplejson.loads(response)
    TransactionNo = response[u'TransactionNo']

    filename = response[u'FileKwitansi']

    sw = returns.AddStreamWrapper()
    sw.Name = 'Kwitansi'
    sw.LoadFromFile(filename)
    #sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(filename)
    sw.MIMEType = 'application/msword'
    
    StreamName = sw.Name

    IsErr = response[u'Status']
    ErrMessage = response[u'ErrMessage']
    
  except :
    IsErr = 1
    ErrMessage = str(sys.exc_info()[1])

  returns.CreateValues(
     ['IsErr', IsErr],
     ['ErrMessage', ErrMessage],
     ['TransactionNo',TransactionNo],
     ['StreamName',StreamName],
     )

