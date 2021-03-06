import com.ihsan.foundation.pobjecthelper as phelper
import sys
import simplejson


def FormSetDataEx(uideflist, params) :
  config = uideflist.config
  helper = phelper.PObjectHelper(config)

  if params.GetDatasetByName('trparam') != None :
    oForm = helper.CreateObject('FormTransaksi')
    oForm.SetDataEx(uideflist,params)
    
    rec = uideflist.uipTransaction.Dataset.GetRecord(0)

    # Set Field For Old Transaction Compatible
    oTran = helper.GetObjectByNames('Transaction',{'TransactionNo' : rec.TransactionNo})
    rec.ActualDate = oTran.GetAsTDateTime('ActualDate')
    rec.TransactionDate = oTran.GetAsTDateTime('TransactionDate')
    rec.BranchId = int(config.SecurityContext.GetUserInfo()[2])
    
    if rec.CurrencyCode in ['',None]:
      rec.CurrencyCode = '000'
      rec.CurrencyName = 'IDR'
      rec.Rate = 1.0
      #rec.AmountEkuivalen = rec.Amount
    #-- end if

    if rec.GetFieldByName('LEmployee.EmployeeName') in ['', None] :
      oTranItem = helper.GetObjectByNames(
         'CAReturnTransactItem',
         {'LTransaction.TransactionNo' : rec.TransactionNo}
      )
      if not oTranItem.isnull :
        rec.SetFieldByName('LEmployee.EmployeeId', oTranItem.LCashAdvanceAccount.EmployeeIdNumber)
        rec.SetFieldByName('LEmployee.EmployeeName', oTranItem.LCashAdvanceAccount.AccountName)
      #-- end if
    #-- end if
    
    TotalRec = uideflist.uipTransactionItem.Dataset.RecordCount
    for idx in range(TotalRec):
      recDetail = uideflist.uipTransactionItem.Dataset.GetRecord(idx)
      if ( recDetail.ItemType == 'D' and
           recDetail.FundEntity == 1 and
           recDetail.Ashnaf == 'L' ):
        recDetail.Ashnaf = 'F'

    return

  Now = int(config.Now())
  rec = uideflist.uipTransaction.Dataset.AddRecord()
  rec.Inputer = str(config.SecurityContext.UserId)
  rec.PaidTo = rec.Inputer
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])
  rec.BranchId = int(config.SecurityContext.GetUserInfo()[2])
  rec.TransactionDate = Now
  rec.FloatTransactionDate = Now
  rec.ActualDate = Now
  rec.Amount = 0.0
  
  # Set Transaction Number
  oService = helper.LoadScript('Transaction.TransactionHelper')
  rec.TransactionNo = '<AUTOGENERATED>' #oService.GetTransactionNumber(config,'CA')

  Now = config.Now()
  bulan = int(config.FormatDateTime('m',Now))
  tahun = int(config.FormatDateTime('yyyy',Now))
  rsPeriod = config.CreateSQL(' \
       select a.periodid from budgetperiod a , budgetperiod b \
       where a.parentperiodid=b.periodid \
           and a.periodvalue=%d and b.periodvalue=%d' % (bulan,tahun)).RawResult
  rec.SetFieldByName('PeriodId', rsPeriod.GetFieldValueAt(0) or 0)
  
def GetInfoRefTransaction(config, params, returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
    ['Amount',0.0],
    ['TransactionDate',0],
    ['Description',''],
    ['TransactionItemId',0],
    
  )

  rec = params.FirstRecord
  
  try:
    helper = phelper.PObjectHelper(config)
    oTran = helper.GetObjectByNames('CATransactItem',{'LTransaction.TransactionNo':rec.TransactionNo})

    if oTran.isnull :
      raise 'PERINGATAN','Data Transaksi Uang Muka Tidak Ditemukan'
      
    if oTran.LCashAdvanceAccount.EmployeeIdNumber != rec.EmployeeId :
      raise 'PERINGATAN','Data Transaksi Uang Muka Milik Karyawan Lain'

    oCAReturnInfo = helper.GetObjectByNames('CashAdvanceReturnInfo',
       {'SourceTransactionId' : oTran.TransactionId}
    )

    if not oCAReturnInfo.isnull :
      raise 'PERINGATAN','Transaksi Referensi Telah Memiliki LPJ'

    status.Amount = oTran.Amount
    status.TransactionDate = oTran.LTransaction.GetAsTDateTime('TransactionDate')
    status.Description = oTran.LTransaction.Description
    status.TransactionItemId = oTran.TransactionItemId
    
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
    
def SimpanData(config, params, returns):
  IsErr = 0
  ErrMessage = ''
  TransactionNo = ''
  StreamName = ''
  
  helper = phelper.PObjectHelper(config)
  try :
    oTransaction = params.uipTransaction.GetRecord(0)

    """
    # Check Source Transaction
    oRefItemCA = helper.GetObjectByNames(
        'CATransactItem',
        {'LTransaction.TransactionNo' : oTransaction.RefTransactionNo}
    )
    oReturnInfo = helper.GetObject('CashAdvanceReturnInfo',
                                        oRefItemCA.LTransaction.TransactionId)
    if not oReturnInfo.isnull :
      raise '', "Transaksi UM yang dipilih sudah memiliki LPJ dengan nomor transaksi : %s " % (
            oReturnInfo.LReturnTransaction.TransactionNo)"""

    if oTransaction.ShowMode != 1:
      # Check Source Transaction
      oRefItemCA = helper.GetObjectByNames(
          'CATransactItem',
          {'LTransaction.TransactionNo' : oTransaction.RefTransactionNo}
      )


      oTran = helper.GetObjectByNames('Transaction',
         {'TransactionNo' : oTransaction.TransactionNo })
      
      RefTransactionId = oRefItemCA.LTransaction.TransactionId
      ReturnTransactionId = oTran.TransactionId
      sSQL = "select * from cashadvancereturninfo \
              where SourceTransactionId=%d \
              and ReturnTransactionId <> %d " % (RefTransactionId, ReturnTransactionId)
      
      resSQL = config.CreateSQL(sSQL).rawresult
      
      if not resSQL.Eof :
        oRetTransaction = helper.GetObject('Transaction', resSQL.ReturnTransactionId)
        raise '', "Transaksi UM yang dipilih sudah memiliki LPJ dengan nomor transaksi : %s " % (
            oRetTransaction.TransactionNo)
      

    
    request = {}
    #request['BatchId'] = oTransaction.GetFieldByName('LBatch.BatchId')
    request['ActualDate'] = oTransaction.ActualDate
    request['EmployeeId'] = oTransaction.EmployeeId #oTransaction.GetFieldByName('LEmployee.Nomor_Karyawan')
    request['EmployeeName'] = oTransaction.EmployeeName
    request['CashAccountNo'] = oTransaction.GetFieldByName('LCashAccount.AccountNo')
    request['Amount'] = oTransaction.Amount
    request['ReferenceNo'] = oTransaction.ReferenceNo
    request['Description'] = oTransaction.Description
    request['Rate'] = oTransaction.Rate
    request['CurrencyCode'] = oTransaction.CurrencyCode
    request['Inputer'] = config.SecurityContext.InitUser
    request['BranchCode'] = config.SecurityContext.GetUserInfo()[4]
    request['RefAmount'] = oTransaction.RefAmount
    request['RefTransactionItemId'] = oTransaction.RefTransactionItemId
    request['RefAmount'] = oTransaction.RefAmount
    request['ReimburseAmount'] = oTransaction.ReimburseAmount or 0.0
    request['TransactionNo'] = oTransaction.TransactionNo
    request['PaidTo'] = oTransaction.PaidTo
    request['RefTransactionNo'] = oTransaction.RefTransactionNo
    
    items = []

    for i in range(params.uipTransactionItem.RecordCount):
      oItem = params.uipTransactionItem.GetRecord(i)
      item = {}
      #item['ProductId'] = oItem.GetFieldByName('LProduct.ProductId')
      item['AccountId'] = oItem.AccountId
      item['AccountName'] = oItem.AccountName
      item['Ashnaf'] = oItem.Ashnaf
      item['Amount'] = oItem.Amount
      #item['Valuta'] = oItem.GetFieldByName('LCurrency.Currency_Code')
      item['Rate']   = oItem.Rate
      item['Ekuivalen'] = oItem.Ekuivalen
      item['Description'] = oItem.Description
      item['FundEntity'] = oItem.FundEntity
      item['DistItemAccount'] = oItem.DistItemCode
      item['BudgetId'] = oItem.BudgetId or 0
      item['ItemType'] = oItem.ItemType or 0
      item['AssetName'] = oItem.AssetName or ''
      item['AssetQty'] = oItem.AssetQty or 0
      item['AssetCatId'] = oItem.AssetCatId or 0
      item['AssetAmount'] = oItem.AssetAmount or 0.0
      item['AssetPaymentType'] = oItem.AssetPaymentType or ''
      item['AssetAccountNo'] = oItem.AssetAccountNo or ''
      item['AssetProductAccountNo'] = oItem.AssetProductAccountNo or ''
      item['AssetProductAccountName'] = oItem.AssetProductAccountName or ''
      item['CPIAAccountNo'] = oItem.CPIAAccountNo or ''
      item['CPIACatId'] = oItem.CPIACatId or ''
      item['CPIACatCode'] = oItem.CPIACatCode or ''
      item['CPIACatName'] = oItem.CPIACatName or ''
      item['CPIAHasContract'] = oItem.CPIAHasContract or 'F'
      item['CPIAContractNo'] = oItem.CPIAContractNo or ''
      item['CPIAContractEndDate'] = oItem.CPIAContractEndDate or 0.0

      item['RecordIdx'] = i

      items.append(item)
    #-- for

    request['Items']= items

    sRequest = simplejson.dumps(request)

    oService = helper.LoadScript('Transaction.GeneralTransaction')
    
    if oTransaction.ReimburseAmount > 0.0 :
      TransactionCode = 'CARB'
    else:
      TransactionCode = 'CAR'

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

