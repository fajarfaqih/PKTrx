import com.ihsan.foundation.pobjecthelper as phelper
import sys
import simplejson


def FormSetDataEx(uideflist, params) :
  config = uideflist.config
  helper = phelper.PObjectHelper(config)
  Now = config.Now()
  
  if params.GetDatasetByName('trparam') != None :
    oForm = helper.CreateObject('FormTransaksi')
    st = oForm.SetDataEx(uideflist,params)

    rec = uideflist.uipTransaction.Dataset.GetRecord(0)

    oTran = helper.GetObjectByNames('Transaction',{'TransactionNo' : rec.TransactionNo})
    rec.ActualDate = oTran.GetAsTDateTime('ActualDate')
    
    # Get Period Id
    tahun = int(config.FormatDateTime('yyyy',Now))
    oBudgetPeriod = helper.GetObjectByNames('BudgetPeriod', {'PeriodValue': tahun})
    rec.PeriodId = oBudgetPeriod.PeriodId
    
    if rec.CurrencyCode in ['',None]:
      rec.CurrencyCode = '000'
      rec.CurrencyName = 'IDR'
      rec.Rate = 1.0
      rec.AmountEkuivalen = rec.Amount


    return st

  rec = uideflist.uipTransaction.Dataset.AddRecord()
  rec.Inputer = str(config.SecurityContext.UserId)
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])
  rec.TransactionDate = int(Now)
  rec.FloatTransactionDate = int(Now)
  rec.ActualDate = int(Now)
  rec.Amount = 0.0
  rec.ReceivedFrom = rec.Inputer
  
  # Set Transaction Number
  oService = helper.LoadScript('Transaction.TransactionHelper')
  rec.TransactionNo = '<AUTOGENERATED>' #oService.GetTransactionNumber(config,'CA')
  
  # Get Period Id
  tahun = int(config.FormatDateTime('yyyy',Now))
  oBudgetPeriod = helper.GetObjectByNames('BudgetPeriod', {'PeriodValue': tahun})
  rec.PeriodId = oBudgetPeriod.PeriodId


def SimpanData(config, params, returns):
  IsErr = 0
  ErrMessage = ''
  TransactionNo = ''
  StreamName = ''
  
  helper = phelper.PObjectHelper(config)
  try :
    oTransaction = params.uipTransaction.GetRecord(0)

    request = {}
    #request['BatchId'] = oTransaction.GetFieldByName('LBatch.BatchId')
    request['EmployeeId'] = oTransaction.EmployeeId #oTransaction.GetFieldByName('LEmployee.Nomor_Karyawan')
    request['EmployeeName'] = oTransaction.EmployeeName
    request['CashAccountNo'] = oTransaction.GetFieldByName('LCashAccount.AccountNo')
    request['CurrencyCode'] = oTransaction.GetFieldByName('LCashAccount.CurrencyCode')
    request['Amount'] = oTransaction.Amount
    request['ReferenceNo'] = oTransaction.ReferenceNo
    request['Description'] = oTransaction.Description
    request['Rate'] = oTransaction.Rate
    request['Inputer'] = config.SecurityContext.InitUser
    request['BranchCode'] = config.SecurityContext.GetUserInfo()[4]
    request['TransactionNo'] = oTransaction.TransactionNo
    request['ReceivedFrom'] = oTransaction.ReceivedFrom
    request['BudgetCode'] = oTransaction.BudgetCode or ''
    request['BudgetId'] = oTransaction.BudgetId or 0
    request['FundEntity'] = oTransaction.FundEntity or 4
    request['DistributionTransferId'] = oTransaction.DistributionId or 0
    request['ActualDate'] = oTransaction.ActualDate
    
    sRequest = simplejson.dumps(request)

    oService = helper.LoadScript('Transaction.GeneralTransaction')
    
    TransactionCode = 'CA'
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

