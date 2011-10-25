import com.ihsan.foundation.pobjecthelper as phelper
import sys
import simplejson


def FormSetDataEx(uideflist, params) :
  config = uideflist.config
  helper = phelper.PObjectHelper(config)

  rec = uideflist.uipTransaction.Dataset.AddRecord()
  rec.Inputer = str(config.SecurityContext.UserId)
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])
  rec.TransactionDate = int(config.Now())
  rec.FloatTransactionDate = int(config.Now())
  rec.Amount = 0.0
  rec.TransactionType = 'P'
  
  # Set Transaction Number
  oService = helper.LoadScript('Transaction.TransactionHelper')
  rec.TransactionNo = oService.GetTransactionNumber(config,'EAR')

def SimpanData(config, params, returns):
  IsErr = 0
  ErrMessage = ''
  helper = phelper.PObjectHelper(config)
  try :
    oTransaction = params.uipTransaction.GetRecord(0)

    request = {}
    request['BatchId'] = oTransaction.GetFieldByName('LBatch.BatchId')
    request['EmployeeId'] = oTransaction.GetFieldByName('LEmployee.Nomor_Karyawan')
    request['EmployeeName'] = oTransaction.EmployeeName
    transactionType = oTransaction.TransactionType
    request['CashAccountNo'] = oTransaction.GetFieldByName('LCashAccount.AccountNo')
    request['Amount'] = oTransaction.Amount
    request['ReferenceNo'] = oTransaction.ReferenceNo
    request['Description'] = oTransaction.Description
    request['Rate'] = 1.0
    request['Inputer'] = config.SecurityContext.InitUser
    request['BranchCode'] = config.SecurityContext.GetUserInfo()[4]
    request['TransactionNo'] = oTransaction.TransactionNo
    
    sRequest = simplejson.dumps(request)

    oService = helper.LoadScript('Transaction.GeneralTransaction')
    if transactionType == 'P':
      oService.EmployeeAR(config, sRequest)
    elif transactionType == 'B':
      oService.PayEmployeeAR(config, sRequest)
  except :
    IsErr = 1
    ErrMessage = str(sys.exc_info()[1])

  returns.CreateValues(['IsErr', IsErr], ['ErrMessage', ErrMessage])

