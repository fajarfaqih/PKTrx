import com.ihsan.foundation.pobjecthelper as phelper
import sys
import simplejson


def FormSetDataEx(uideflist, params) :
  config = uideflist.config
  helper = phelper.PObjectHelper(config)

  if params.GetDatasetByName('trparam') != None :
    oForm = helper.CreateObject('FormTransaksi')
    oForm.SetDataEx(uideflist,params)

    # Set value for data from obselete form
    param = params.FirstRecord
    rec = uideflist.uipTransaction.Dataset.GetRecord(0)

    oCTran = helper.GetObjectByNames('AccountTransactionItem',
      { 'MutationType' : 'C',
        'AccountNo' : rec.GetFieldByName('LCashAccountSource.AccountNo'),
        'TransactionId' : param.TransactionId
        })
    rec.SourceRate = oCTran.Rate
    rec.SourceAmount = oCTran.Amount
    rec.ActualDate = oCTran.LTransaction.GetAsTDateTime('ActualDate')
    
    oDTran = helper.GetObjectByNames('AccountTransactionItem',
      { 'MutationType' : 'D',
        'AccountNo' : rec.GetFieldByName('LCashAccountDestination.AccountNo'),
        'TransactionId' : param.TransactionId
        })
    rec.DestRate = oDTran.Rate
    rec.DestAmount = oDTran.Amount


    return

  Now = int(config.Now())
  rec = uideflist.uipTransaction.Dataset.AddRecord()
  rec.Inputer = str(config.SecurityContext.UserId)
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])
  rec.TransactionDate = Now
  rec.FloatTransactionDate = Now
  rec.ActualDate = Now
  rec.Rate = 1.0
  rec.Amount = 0.0

  # Set Transaction Number
  oService = helper.LoadScript('Transaction.TransactionHelper')
  rec.TransactionNo = '<AUTOGENERATED>' #oService.GetTransactionNumber(config)

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
    request['ActualDate'] = oTransaction.ActualDate
    request['SourceAccountNo'] = oTransaction.GetFieldByName('LCashAccountSource.AccountNo')
    request['DestAccountNo'] = oTransaction.GetFieldByName('LCashAccountDestination.AccountNo')
    request['TransactionNo'] = oTransaction.TransactionNo


    request['ReferenceNo'] = oTransaction.ReferenceNo
    request['Description'] = oTransaction.Description
    request['TranCurrencyCode'] = oTransaction.TranCurrencyCode
    request['Amount'] = oTransaction.Amount
    request['Rate'] = oTransaction.Rate
    request['Inputer'] = config.SecurityContext.InitUser
    request['BranchCode'] = config.SecurityContext.GetUserInfo()[4]


    request['SourceCurrencyCode'] = oTransaction.GetFieldByName('LCashAccountSource.CurrencyCode')
    request['SourceAmount'] = oTransaction.SourceAmount
    request['SourceRate'] = oTransaction.SourceRate

    sRequest = simplejson.dumps(request)

    oService = helper.LoadScript('Transaction.GeneralTransaction')

    TransactionCode = 'TI'
    if oTransaction.ShowMode == 1:
      response = oService.CreateTransaction(TransactionCode, config, sRequest, params)
    else:
      response = oService.UpdateTransaction(TransactionCode, config, sRequest, params)

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


