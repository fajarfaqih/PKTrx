# GeneralTransaction.py
import simplejson
import com.ihsan.foundation.pobjecthelper as phelper
import sys
    
status = 0
msg = ''
FileKwitansi = ''
FundEntityMAP = {'Z': 1, 'I': 2, 'W': 3}

def Main(config, srequest,params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'TotalDebit']):
      oTran.AutoApproval()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)

def GetBatch(helper,ActualDate):

  oBatchHelper = helper.CreateObject('BatchHelper')
  oBatch = oBatchHelper.GetBatchUser(ActualDate)
  return oBatch

def GenerateResponse(Status,ErrMessage,TransactionNo,FileKwitansi):
  response = {}
  response['Status'] = Status
  response['TransactionNo'] = TransactionNo
  response['ErrMessage'] = ErrMessage
  response['FileKwitansi'] = FileKwitansi
  
  return simplejson.dumps(response)

def ExecFunction(TranCode, helper, oTran, oBatch, request, params):
  if TranCode == 'GT' : # Transaksi Umum
    FileKwitansi = GeneralTransaction(helper,oTran,oBatch,request,params)
  elif TranCode == 'TI' : # Transfer Internal
    FileKwitansi = InternalTransfer(helper,oTran,oBatch,request,params)
  elif TranCode == 'TIR' : # Transfer RAK
    FileKwitansi = TransferRAK(helper,oTran,oBatch,request,params)
  elif TranCode == 'PAD' : # Pinjaman Antar Dana
    FileKwitansi = InterFundTransfer(helper,oTran,oBatch,request,params)
  elif TranCode in ['EAR','XAR'] : # Piutang Karyawan
    FileKwitansi = EmployeeAR(helper,oTran,oBatch,request,params)
  elif TranCode in ['PEAR','PXAR'] : # Piutang Karyawan
    FileKwitansi = PayEmployeeAR(helper,oTran,oBatch,request,params)
  elif TranCode == 'CA' : # Penyerahan Uang Muka
    FileKwitansi = CashAdvance(helper,oTran,oBatch,request,params)
  elif TranCode in ['CARB','CAR'] : # LPJ Uang Muka
    FileKwitansi = CashAdvanceReturn(helper,oTran,oBatch,request,params)
  elif TranCode == 'INVS' : # Investasi
    FileKwitansi = Investment(helper,oTran,oBatch,request,params)
  elif TranCode == 'INVSR' : # Pengembalian Investasi
    FileKwitansi = InvestmentReturn(helper,oTran,oBatch,request,params)
  elif TranCode == 'CARR' : # Pengembalian UM RAK
    FileKwitansi = CashAdvanceReturnRAK(helper,oTran,oBatch,request,params)
  elif TranCode == 'CPIA' : # Biaya Dibayar Di muka
    FileKwitansi = CostPaidInAdvance(helper,oTran,oBatch,request,params)
  elif TranCode == 'INVP' : # Pembayaran Invoice
    FileKwitansi = InvoicePayment(helper,oTran,oBatch,request,params)
  elif TranCode == 'DT' : # Transfer Dana RAK
    FileKwitansi = BranchDistribution(helper,oTran,oBatch,request,params)
  elif TranCode == 'DTR' : # LPJ Dana RAK
    FileKwitansi = BranchDistributionReturn(helper,oTran,oBatch,request,params)
  else:
    raise '','Kode Transaksi Tidak Dikenal'

  return FileKwitansi

def CreateTransaction(TranCode, config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  status = 0
  msg = ''
  
  oBatch = GetBatch(helper,request['ActualDate'])
   
  config.BeginTransaction()
  try:
    oHistory = helper.CreatePObject('TransHistoryOfChanges')
    oHistory.ChangeType = 'I'

    #oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction(TranCode)

    FileKwitansi = ExecFunction(TranCode, helper, oTran, oBatch, request, params)

    # Check for auto approval
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount'] * request[u'Rate']):
      oTran.AutoApproval()
    
    oHistory.TransactionNo = oTran.TransactionNo

    config.Commit()
  except:
    config.Rollback()
    raise
  
  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)

def UpdateTransaction(TranCode, config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)
  
  oBatch = GetBatch(helper,request['ActualDate'])

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  TranHelper = helper.LoadScript('Transaction.TransactionHelper')
  TranHelper.DeleteTransactionJournal(oTran)

  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    # Generate History
    oHistory = helper.CreatePObject('TransHistoryOfChanges')
    oHistory.TransactionNo = oTran.TransactionNo
    oHistory.ChangeType = 'E'

    oTran.CancelTransaction()

    oTran.BatchId = oBatch.BatchId
    oTran.TransactionCode = TranCode
    
    FileKwitansi = ExecFunction(TranCode, helper, oTran, oBatch, request, params)
    
    # Check for auto approval
    oTran.AutoApprovalUpdate()

    oHistory.NewTransactionNo = oTran.TransactionNo
    
    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
# end def 


# DEFINE 
dictJournalCodeDonor = {
  1 : 'C10Z',
  2 : 'C10I',
  3 : 'C10W',
  4 : '10',
  5 : '10'
}

def GeneralTransaction( helper, oTran, oBatch, request, params):
  aInputer    = request[u'Inputer']
  aBranchCode = request[u'BranchCode']

  oTran.Inputer     = aInputer
  oTran.BranchCode  = aBranchCode
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Amount = request[u'TotalCredit']
#     oTran.CurrencyCode = request[u'CashCurrency']
  oTran.CurrencyCode = '000'
  oTran.Rate = '1'
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
  
  items = request[u'Items']
  
  for item in items:
    aValuta = item[u'Valuta']
    aAmount = item[u'Amount']
    aRate   = item[u'Rate']
    aDesc   = item[u'Description']

    aItemType = item[u'ItemType']

    if aItemType == 'C':
    # Collection Transaction (Product)
      aProductId  = item[u'ProductId']
      #oProductAccount = helper.GetObjectByNames('ProductAccount',
      #  {'ProductId': aProductId, 'BranchCode': aBranchCode, 'CurrencyCode': aValuta})

      oProductAccount = helper.GetObject('ProductAccount',str(item[u'AccountNo']))
      if oProductAccount.isnull:
        raise 'Collection', 'Rekening produk %d:%s tidak ditemukan' % (aProductId, aValuta)

      oItemPA = oTran.CreateDonorTransactionItem(oProductAccount, item[u'DonorId'])
      if item[u'MutationType'] == 'C':
        oItemPA.SetMutation(aAmount, aRate)
      else:
        oItemPA.SetReverseMutation(aAmount, aRate)
      # end if else  
      oItemPA.Description = aDesc

      FundEntity = item[u'FundEntity']
      PercentageOfAmil = item[u'PercentageOfAmil']
      if PercentageOfAmil <= 0.0 :
        JournalCode ='10'
      else:
        JournalCode = dictJournalCodeDonor[FundEntity]
      # end if

      oItemPA.SetJournalParameter(JournalCode)
      oItemPA.SetCollectionEntity(FundEntity)
      oItemPA.PercentageOfAmil = PercentageOfAmil

      #oSponsor = helper.GetObject('Sponsor', item[u'SponsorId'])
      #if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)
      
      oDonor = helper.CreateObject('ExtDonor')
      oDonor.GetData(item[u'DonorId'])
      if oDonor.IsSponsor() : oDonor.AddTransaction(oItemPA)
      
      oVolunteer = helper.GetObject('Volunteer', str(item[u'VolunteerId']))
      if not oVolunteer.isnull: oVolunteer.AddTransaction(oItemPA)

    elif aItemType == 'D':
    # Distribution Transaction (Product)
      aProductId  = item[u'ProductId']
      #oProductAccount = helper.GetObjectByNames('ProductAccount',
      #  {'ProductId': aProductId, 'BranchCode': aBranchCode, 'CurrencyCode': aValuta}) 
      oProductAccount = helper.GetObject('ProductAccount',str(item[u'AccountNo']))
      if oProductAccount.isnull:
        raise 'Distribution', 'Rekening produk %d:%s tidak ditemukan' % (aProductId, aValuta)
            
      oItemPA = oTran.CreateZakahDistTransactItem(oProductAccount, item[u'Ashnaf'])
      
      oItemPA.SetMutation(item[u'MutationType'], aAmount, aRate)
      oItemPA.Description = aDesc
      oItemPA.SetJournalParameter('10')
      oItemPA.SetDistributionEntity(item[u'FundEntity'])
      #oItemPA.DistributionItemAccount = item[u'DistItemAccount']

      #oSponsor = helper.GetObject('Sponsor', item[u'SponsorId'])
      #if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)
      if item[u'SponsorId'] != 0 :
        oDonor = helper.CreateObject('ExtDonor')
        oDonor.GetData(item[u'SponsorId'])
        if oDonor.IsSponsor() : oDonor.AddTransaction(oItemPA)
      
    elif aItemType == 'B':
    # Cash/Bank Transaction
      oAccount = helper.GetObject('CashAccount', str(item[u'AccountNo'])).CastToLowestDescendant()
      if oAccount.isnull:
        raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % item[u'AccountNo']

      oItemCA = oTran.CreateAccountTransactionItem(oAccount)
      oItemCA.SetMutation(item[u'MutationType'], aAmount, aRate)
      oItemCA.Description = aDesc
      oItemCA.SetJournalParameter('10')

    else: # aItemType == 'G':
    # Ledger Transaction
      oItemGL = oTran.CreateGLTransactionItem(item[u'AccountCode'], aValuta)
      oItemGL.RefAccountName = item[u'AccountName']
      oItemGL.SetMutation(item[u'MutationType'], aAmount, aRate)
      oItemGL.Description = aDesc
      oItemGL.SetJournalParameter('10')

    #-- if.else
  #-- for
  oTran.GenerateTransactionNumber('000')
  oTran.SaveInbox(params)
  
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi

### -------  INTERNAL TRANSFER -----------------------------------      
def InternalTransfer(helper,oTran,oBatch,request,params):
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']
  #oTran.TransactionNo = request[u'TransactionNo']
  oTran.Amount = request[u'Amount']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
  oTran.CurrencyCode = request[u'TranCurrencyCode']
  oTran.Rate = request[u'Rate']

  # Set Journal Code
  JournalCode = 'TI'
    
  # Source Transaction
  oSrcAccount = helper.GetObject('CashAccount',
    str(request[u'SourceAccountNo'])).CastToLowestDescendant()
  if oSrcAccount.isnull :
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'AccountNo']

  oItemSA = oTran.CreateAccountTransactionItem(oSrcAccount)
  oItemSA.SetMutation('C', request[u'Amount'], request[u'Rate'])
  oItemSA.Description = request[u'Description']
  oItemSA.SetJournalParameter(JournalCode)

  # Destination Transaction
  oDstAccount = helper.GetObject('CashAccount',
    str(request[u'DestAccountNo'])).CastToLowestDescendant()
  if oDstAccount.isnull :
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'AccountNo']

  oItemDA = oTran.CreateAccountTransactionItem(oDstAccount)
  oItemDA.SetMutation('D', request[u'Amount'], request[u'Rate'])
  oItemDA.Description = request[u'Description']
  oItemDA.SetJournalParameter(JournalCode)

  oTran.Amount = request[u'SourceAmount']
  oTran.CurrencyCode = request[u'SourceCurrencyCode']
  oTran.Rate = request[u'SourceRate']
  
  oTran.GenerateTransactionNumber('000')
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi
  
### -------  END INTERNAL TRANSFER -----------------------------------

### -------  TRANSFER RAK -----------------------------------      
def TransferRAK(helper, oTran, oBatch, request, params):
  oTran.ReferenceNo = request[u'ReferenceNo']

  CurrencyCode = request[u'TranCurrencyCode']
  aAmount = request[u'Amount']
  aRate = request[u'Rate']

  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']
  #oTran.TransactionNo = request[u'TransactionNo']
  oTran.Amount = request[u'Amount']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
  oTran.CurrencyCode = CurrencyCode
  oTran.Rate = request[u'Rate']
  
  
  # Set Journal Code
  JournalCode = '15' 
    
  # Source Cash Account Transaction
  oSrcAccount = helper.GetObject('CashAccount',
    str(request[u'SourceAccountNo'])).CastToLowestDescendant()
  if oSrcAccount.isnull :
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'AccountNo']

  oItemSA = oTran.CreateAccountTransactionItem(oSrcAccount)
  oItemSA.SetMutation('C', aAmount, aRate)
  oItemSA.Description = request[u'Description']
  oItemSA.SetJournalParameter(JournalCode)

  # Destination Cash Account Transaction
  oDstAccount = helper.GetObject('CashAccount',
    str(request[u'DestAccountNo'])).CastToLowestDescendant()
  if oDstAccount.isnull :
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'AccountNo']

  oItemDA = oTran.CreateAccountTransactionItem(oDstAccount)
  oItemDA.SetMutation('D', aAmount, aRate)
  oItemDA.Description = request[u'Description']
  oItemDA.SetJournalParameter(JournalCode)

  FundEntity = int(request[u'FundEntity'])
  if FundEntity == 4 : # Sumber Dana Amil
    # Source
    oItemFA = oTran.CreateGLTransactionItem('5520904', '000')
    oItemFA.RefAccountName = 'Pengiriman Transfer Dana'
    oItemFA.SetMutation('D', aAmount, aRate)
    oItemFA.Description = request[u'Description']
    oItemFA.SetJournalParameter(JournalCode)

    # Desctination
    oItemFA = oTran.CreateGLTransactionItem('4510902', '000')
    oItemFA.BranchCode = request[u'DestBranchCode']
    oItemFA.RefAccountName = 'Penerimaan Transfer Dana'
    oItemFA.SetMutation('C', aAmount, aRate)
    oItemFA.Description = request[u'Description']
    oItemFA.SetJournalParameter(JournalCode)


  else : # Sumber Dana Non Amil
    
    TransferAccountCode = {
      '4110101' : '4110104',
      '4210101' : '4210105',
      '4210102' : '4210106',
      '4210103' : '4210107',
      '4220101' : '4220104',
      '4310101' : '4310104',
      '4410101' : '4410104',
      '5110101' : '5110103',
      '5210101' : '5210105',
      '5210102' : '5210106',
      '5210103' : '5210107',
      '5210201' : '5210203',
      '5310101' : '5310103',
      '5410101' : '5410103',
    }

    # Source Account
    ProductAccountNo = str(request[u'ProductAccountNo'])
    oSrcAccount = helper.GetObject('ProductAccount',
                                    ProductAccountNo).CastToLowestDescendant()

    if oSrcAccount.isnull:
      raise 'ProductAccount', 'Rekening Produk cabang asal (%s) tidak ditemukan' % request[u'AccountNo']
    
    oItemSA = oTran.CreateAccountTransactionItem(oSrcAccount)
    oItemSA.SetMutation('D', request[u'Amount'], request[u'Rate'])
    oItemSA.Description = request[u'Description']
    
    oItemSA.SetDistributionEntity(request[u'FundEntity'])
    oItemSA.AccountCode = TransferAccountCode[oItemSA.AccountCode]
    oItemSA.SetJournalParameter(JournalCode)

    # Destination Account
    oDstAccount = helper.GetObjectByNames('ProductAccount', 
                          { 'ProductId' : int(request[u'ProductId']),
                            'BranchCode' : str(request[u'DestBranchCode']),
                            'CurrencyCode' : CurrencyCode
                          }).CastToLowestDescendant()

    if oDstAccount.isnull:
      raise 'ProductAccount', 'Rekening Produk cabang tujuan (%s) tidak ditemukan' % request[u'AccountNo']

    oItemDA = oTran.CreateAccountTransactionItem(oDstAccount)
    oItemDA.SetMutation('C', request[u'Amount'], request[u'Rate'])
    oItemDA.Description = request[u'Description']

    oItemDA.SetCollectionEntity(request[u'FundEntity'])
    oItemDA.AccountCode = TransferAccountCode[oItemDA.AccountCode]
    oItemDA.SetJournalParameter(JournalCode)
    
  oTran.Amount = request[u'SourceAmount']
  oTran.CurrencyCode = request[u'SourceCurrencyCode']
  oTran.Rate = request[u'SourceRate']
  
  oTran.GenerateTransactionNumber('000')
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi
  
### -------  END TRANSFER RAK -----------------------------------



### -------  INTERFUND TRANSFER -----------------------------------  
def InterFundTransfer(helper,oTran,oBatch,request,params):
  JournalCode = {1 : 'PADZ', 2 : 'PADI', 3 : 'PADW', 4 : 'PADA' , 5 : 'PADN'}
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']
  #oTran.TransactionNo = request[u'TransactionNo']
  oTran.Amount = request[u'Amount']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
  
  # Source Transaction
  oSrcAccount = helper.GetObject('ProductAccount',
    str(request[u'SourceAccountNo'])).CastToLowestDescendant()
  if oSrcAccount.isnull:
    raise 'ProductAccount', 'Rekening %s tidak ditemukan' % request[u'AccountNo']
  
  oTran.CurrencyCode = oSrcAccount.CurrencyCode 
  
  oItemSA = oTran.CreateAccountTransactionItem(oSrcAccount)
  oItemSA.SetMutation('D', request[u'Amount'], request[u'Rate'])
  oItemSA.Description = request[u'Description']
  
  #oItemSA.AccountCode = oSrcAccount.GetDistributionInterface(request[u'FundEntitySource'])  
  oItemSA.SetDistributionEntity(request[u'FundEntitySource'])
  oItemSA.SetJournalParameter(JournalCode[request[u'FundEntitySource']])

  # Destination Transaction
  oDstAccount = helper.GetObject('ProductAccount',
    str(request[u'DestAccountNo'])).CastToLowestDescendant()
  if oDstAccount.isnull:
    raise 'ProductAccount', 'Rekening %s tidak ditemukan' % request[u'AccountNo']

  oItemDA = oTran.CreateAccountTransactionItem(oDstAccount)
  oItemDA.SetMutation('C', request[u'Amount'], request[u'Rate'])
  oItemDA.Description = request[u'Description']

  oItemDA.AccountCode = oDstAccount.GetCollectionInterface(request[u'FundEntityDestination'])
  oItemDA.SetCollectionEntity(request[u'FundEntityDestination'])
  oItemDA.SetJournalParameter(JournalCode[request[u'FundEntityDestination']])
  
  oTran.GenerateTransactionNumber('000')
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi
    

### ------- END INTERFUND TRANSFER -----------------------------------
  

### ------- EMPLOYEE ACCOUNT RECEIVABLE -----------------------------------  
def EmployeeAR(helper,oTran,oBatch,request,params):
    FundEntityMap = { 1 : 'AK-Z', 2 : 'AK-I', 3 : 'AK-W', 4 : 'AK-A1'}
  
    BranchCode = str(request[u'BranchCode'])  
    oTran.ReferenceNo = request[u'ReferenceNo']
    oTran.Description = request[u'Description']
    oTran.Inputer     = request[u'Inputer']
    oTran.BranchCode  = BranchCode
    #oTran.TransactionNo = request[u'TransactionNo']
    oTran.Amount = request[u'Amount']
    oTran.CurrencyCode = '000'
    oTran.ReceivedFrom = request[u'Casher']
    oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
        
    # EmployeeAR Account
    employeeId = request[u'EmployeeId']
    if request[u'DebtorType'] == 'E' :
      oAccount = helper.GetObjectByNames('EmployeeAccountReceivable',
        {
          'EmployeeIdNumber': employeeId,
          'CurrencyCode': '000',
          'BranchCode' : BranchCode
        }
      )
    
      if oAccount.isnull:
        # Create EmployeeAR Account
        oAccount = helper.CreatePObject('EmployeeAccountReceivable', employeeId)
        oAccount.BranchCode = BranchCode
        oAccount.CurrencyCode = '000'
        oAccount.AccountName  = request[u'EmployeeName']
      #end if  
    else:
      oAccount = helper.GetObjectByNames('ExternalAccountReceivable',
        {
          'DebtorId': employeeId,
          'CurrencyCode': '000'
        }
      )
    
      if oAccount.isnull:
        # Create EmployeeAR Account
        oAccount = helper.CreatePObject('ExternalAccountReceivable', employeeId)
        oAccount.BranchCode = BranchCode
        oAccount.CurrencyCode = '000'
        oAccount.AccountName  = request[u'EmployeeName']
      #end if  
    #end if else
    
    oTran.PaidTo = request[u'EmployeeName']
    
    oItemAR = oTran.CreateAccountTransactionItem(oAccount)
    oItemAR.SetMutation('D', request[u'Amount'], 1.0)
    oItemAR.Description = request[u'Description']
    oItemAR.SetFundEntity(request[u'FundEntity'])
    oItemAR.SetJournalParameter(FundEntityMap[request[u'FundEntity']])
    
    
    # Cash Account Transaction
    oCashAccount = helper.GetObject('CashAccount',
      str(request[u'CashAccountNo'])).CastToLowestDescendant()
      
    if oCashAccount.isnull: 
      raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'CashAccountNo']

    oItemCA = oTran.CreateAccountTransactionItem(oCashAccount)
    oItemCA.SetMutation('C', request[u'Amount'], 1.0)
    oItemCA.Description = request[u'Description']
    oItemCA.SetJournalParameter('10')

    oTran.GenerateTransactionNumber(oCashAccount.CashCode,request[u'IsChangeTransactionNo'])
    oTran.SaveInbox(params)
    return oTran.GetKwitansi()

def PayEmployeeAR(helper,oTran,oBatch,request,params):
  FundEntityMap = {1 : 'PAK-Z', 2 : 'PAK-I', 3 : 'PAK-W', 4 : 'PAK-A1'}

  BranchCode = str(request[u'BranchCode'])

  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = BranchCode
  #oTran.TransactionNo = request[u'TransactionNo']
  oTran.Amount = request[u'Amount']
  oTran.CurrencyCode = '000'
  oTran.PaidTo = request[u'Casher']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
  
  # Get Branch
  oBranch = helper.GetObject('Branch', BranchCode)

  # EmployeeAR Account
  employeeId = request[u'EmployeeId']
  if request[u'DebtorType'] == 'E' :    
    oAccount = helper.GetObjectByNames('EmployeeAccountReceivable',
      {
        'EmployeeIdNumber': employeeId,
        'CurrencyCode': '000',
        'BranchCode' : request[u'BranchCode']
      }
    )
     
    if oAccount.isnull:
      raise 'PayEAR', 'Karyawan belum memiliki rekening piutang di cabang %s ( %s ) ' % (BranchCode , oBranch.BranchName)
  else:
    
    oAccount = helper.GetObjectByNames('ExternalAccountReceivable',
        {
          'DebtorId': employeeId,
          'CurrencyCode': '000'
        }
      )
    
    if oAccount.isnull:    
      raise 'PayEAR', 'Eksternal Debitur belum memiliki rekening piutang'
    # end if
      
  # end if else    
  oTran.ReceivedFrom = oAccount.AccountName[:30]
  
  oItemAR = oTran.CreateAccountTransactionItem(oAccount)
  oItemAR.SetMutation('C', request[u'Amount'], 1.0)
  oItemAR.Description = request[u'Description']
  oItemAR.SetFundEntity(request[u'FundEntity'])
  oItemAR.SetJournalParameter(FundEntityMap[request[u'FundEntity']])

  # Cash
  oCashAccount = helper.GetObject('CashAccount',
    str(request[u'CashAccountNo'])).CastToLowestDescendant()
  if oCashAccount.isnull:
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'CashAccountNo']

  oItemCA = oTran.CreateAccountTransactionItem(oCashAccount)
  oItemCA.SetMutation('D', request[u'Amount'], 1.0)
  oItemCA.Description = request[u'Description']
  oItemCA.SetJournalParameter('10')
  

  oTran.GenerateTransactionNumber(oCashAccount.CashCode,request[u'IsChangeTransactionNo'])
  oTran.SaveInbox(params)
  
  return oTran.GetKwitansi()    

### ------- END EMPLOYEE ACCOUNT RECEIVABLE -----------------------------------

### ------- CASH ADVANCE  -----------------------------------
def CashAdvance(helper,oTran,oBatch,request,params):
  JournalCode = {1 : 'AK-Z', 2 : 'AK-I', 3 : 'AK-W', 4 : 'AK-A2', 5 : 'AK-N'}
  
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']  
  oTran.Amount = request[u'Amount']
  oTran.Rate = request[u'Rate']
  oTran.CurrencyCode = request[u'CurrencyCode']
  oTran.ReceivedFrom = request[u'ReceivedFrom']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')

  
  aCurrencyCode = request[u'CurrencyCode']
  aRate = request[u'Rate']
  # EmployeeAR Account
  employeeId = request[u'EmployeeId']

  oAccount = helper.GetObjectByNames('EmployeeCashAdvance',
    {
      'EmployeeIdNumber': employeeId,
      'CurrencyCode': aCurrencyCode #'000'
    }
  )
  
  if oAccount.isnull:
    #raise '','Karyawan Belum Memiliki Rekening Uang Muka' 
    # Create EmployeeCashAdvance Account
    oAccount = helper.CreatePObject('EmployeeCashAdvance', [employeeId,aCurrencyCode])
    oAccount.BranchCode = request[u'BranchCode']
    #oAccount.CurrencyCode = aCurrencyCode #'000'
    oAccount.AccountName  = request[u'EmployeeName']

  oItemCAD = oTran.CreateCATransactItem(oAccount)
  oItemCAD.SetMutation('D', request[u'Amount'], aRate)
  oItemCAD.Description = request[u'Description']
  #oItemCAD.ProductAccountNo = request[u'ProductAccountNo']
  oItemCAD.SetFundEntity(request[u'FundEntity'])
  oItemCAD.SetJournalParameter(JournalCode[request[u'FundEntity']])
  
  DistributionTransferId = request[u'DistributionTransferId'] or 0
  if DistributionTransferId != 0 :
    oDistTransferInfo = helper.GetObject('DistributionTransferInfo', DistributionTransferId)
    if oDistTransferInfo.isnull :
      raise '', 'Data RAK tidak ditemukan'
    
    oDistTransferInfo.UpdateBalance( '-', request[u'Amount'])
    
    if oDistTransferInfo.Balance < 0.0 :
      raise '', 'Saldo RAK tidak mencukupi untuk melakukan transaksi'

    oItemCAD.DistributionTransferId = DistributionTransferId

  # Create BudgetTransaction
  aBudgetId = request[u'BudgetId'] 

  if aBudgetId != 0 :
    oBudget = helper.GetObject('Budget',aBudgetId)
    oItemCAD.CreateBudgetTransaction(oBudget.BudgetId)
  # endif 

  # Destination Transaction
  oCashAccount = helper.GetObject('CashAccount',
    str(request[u'CashAccountNo'])).CastToLowestDescendant()
  if oCashAccount.isnull:
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'CashAccountNo']

  oItemCA = oTran.CreateAccountTransactionItem(oCashAccount)
  oItemCA.SetMutation('C', request[u'Amount'], aRate)  
  oItemCA.Description = request[u'Description']
  oItemCA.SetJournalParameter('10')
  
  oTran.PaidTo = oAccount.AccountName
  #oTran.Rece

  oTran.GenerateTransactionNumber(oCashAccount.CashCode)
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()

  return oTran.GetKwitansi()

### ------- End CASH ADVANCE  -------------------------------------------

### ------- Begin CASH ADVANCE RETURN -----------------------------------
def CreateFixAssetTransactionItem(helper, oTran, params, request, item, isCreateRAK = 0):
  aAmount = item[u'Amount']
  aRate = request[u'Rate']
  aCurrencyCode = request[u'CurrencyCode']
  aCashAdvance =  item[u'Amount'] * aRate
  aFundEntity = item[u'FundEntity']
  aDescription = item[u'Description']

  
  # 1. Create Data FixedAsset
  AccountNoFA = str(item[u'AssetAccountNo'])
  if AccountNoFA == '' :
    oFAAccount = helper.CreatePObject('FixedAsset')
  else:
    oFAAccount = helper.GetObject('FixedAsset',AccountNoFA)
  # end if
    
  oFAAccount.BranchCode = request[u'BranchCode']
  oFAAccount.CurrencyCode = '000'
  oFAAccount.AccountName  = item[u'AssetName']
  oFAAccount.Qty = item[u'AssetQty']
  oFAAccount.SetAssetCategory(item[u'AssetCatId'])
  oFAAccount.SetInitialValue(item[u'AssetAmount'] * aRate)
  oFAAccount.SetInitialProcessDate()
  oFAAccount.UangMuka = aCashAdvance

  if oFAAccount.LAssetCategory.AssetType == 'T' :
    oFAAccount.AccountNoProduct = item[u'AssetProductAccountNo']
  
  # 2. Buat transaksi pembelian asset
  # Set Journal Code berdasarkan PaymentType
  if item[u'AssetPaymentType'] == 'T' :
    JournalCode = 'DA01B'
  else :
    if aCashAdvance > 0.0 :
      JournalCode = 'DA01A'
    else:
      JournalCode = 'DA01C'
    # endif
  # endif
             
  # Buat Transaksi pembelian

  oItemFA = oTran.CreateAssetTransactionItem(oFAAccount)
  oItemFA.SetMutation('D', aAmount, aRate)
  oItemFA.Description = aDescription
  oItemFA.SetJournalParameter(JournalCode)
  oItemFA.AccountCode = oFAAccount.GetAssetAccount()
  oItemFA.SetFundEntity(aFundEntity or 4)
  
  if oFAAccount.LAssetCategory.AssetType == 'T' :
    oProduct = oFAAccount.LProductAccount
    
    oItemFA = oTran.CreateAccountTransactionItem(oProduct)
    oItemFA.SetMutation('D',aAmount,aRate)
    oItemFA.Description = aDescription
    oItemFA.SetJournalParameter('DA02A')
    oItemFA.SetDistributionEntity(aFundEntity)

    AccountCode = oFAAccount.GetAssetKelolaanPlusAccount(aFundEntity)
    oItemFA.AddGLInterface('ASET_KELOLA', AccountCode,'Penambahaan Aset Kelolaan')

  else:
    AccountCode = oFAAccount.GetAmilCostForAssetAccount()
    oItemFA = oTran.CreateGLTransactionItem(AccountCode, '000')
    oItemFA.RefAccountName = 'Beban Aset Kelolaan Amil Atas Aktiva Tetap'
    oItemFA.SetMutation('D',aAmount,aRate)
    oItemFA.Description = aDescription
    oItemFA.SetJournalParameter('DA02B')
  
  # simpan nomor akun pada dataset
  recItem = params.uipTransactionItem.GetRecord(item[u'RecordIdx'])
  recItem.AssetAccountNo = oFAAccount.AccountNo  
  
  # Buat RAK jika status RAK true
  if isCreateRAK:
    AccountRAK = helper.GetObject('ParameterGlobal', 'GLIRAKOTO').Get()
    oItemGL = oTran.CreateGLTransactionItem(AccountRAK, '000')
    oItemGL.RefAccountName = 'RAK Otomatis'
    oItemGL.SetMutation('C', aAmount, aRate)
    oItemGL.Description = 'Akun RAK Otomatis'
    oItemGL.SetJournalParameter('10')
  # end if
  
def CreateCPIATransactionItem(helper, oTran, params, request, item, isCreateRAK = 0 ):
  aAmount = item[u'Amount']
  aRate = request[u'Rate']
  aCurrencyCode = request[u'CurrencyCode']
  aCashAdvance =  item[u'Amount'] * aRate
  aFundEntity = item[u'FundEntity']
  aDescription = item[u'Description']

  # 1. Create CostPaidInAdvance
  CPIAAccountNo = str(item[u'CPIAAccountNo'])
  if CPIAAccountNo == '' :
    oCPIAAccount = helper.CreatePObject('CostPaidInAdvance')
  else :
    oCPIAAccount = helper.GetObject('CostPaidInAdvance',CPIAAccountNo)

  oCPIAAccount.BranchCode = request[u'BranchCode']
  if item[u'CPIAHasContract'] == 'T':
    oCPIAAccount.SetContract(item[u'CPIAContractNo'], item[u'CPIAContractEndDate'])
  else:
    oCPIAAccount.SetNoContract()
  #-- if.else
  oCPIAAccount.SetInitialValue(aAmount)
  oCPIAAccount.Description = item[u'Description']
  oCPIAAccount.CostAccountNo = item[u'AccountId']
  oCPIAAccount.CPIACatId = item[u'CPIACatId']

  oItem = oTran.CreateAccountTransactionItem(oCPIAAccount)
  oItem.SetMutation('D', aAmount, aRate)
  oItem.Description = aDescription
  oItem.SetJournalParameter('BDD01')

  # simpan nomor akun pada dataset
  recItem = params.uipTransactionItem.GetRecord(item[u'RecordIdx'])
  recItem.CPIAAccountNo = oCPIAAccount.AccountNo

  # Buat RAK jika status RAK true
  if isCreateRAK:
    AccountRAK = helper.GetObject('ParameterGlobal', 'GLIRAKOTO').Get()
    oItemGL = oTran.CreateGLTransactionItem(AccountRAK, '000')
    oItemGL.RefAccountName = 'RAK Otomatis'
    oItemGL.SetMutation('C', aAmount, aRate)
    oItemGL.Description = 'Akun RAK Otomatis'
    oItemGL.SetJournalParameter('10')
  # end if

def CashAdvanceReturn(helper,oTran,oBatch,request,params):
  FundEntityMap = {1 : 'PAK-Z', 2 : 'PAK-I', 3 : 'PAK-W', 4 : 'PAK-A2', 5 : 'PAK-N'}
  
  # Set Transaction Data  
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']
  #oTran.TransactionNo = request[u'TransactionNo']
  oTran.Amount = request[u'RefAmount'] + request[u'ReimburseAmount']
  oTran.CurrencyCode = request[u'CurrencyCode']
  oTran.ReceivedFrom = request[u'EmployeeName']
  oTran.PaidTo = request[u'PaidTo']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
  oTran.Rate = request[u'Rate']
  oTran.ChannelAccountNo = str(request[u'CashAccountNo'])
  
  # Set Support Variable 
  aRate = request[u'Rate']
  aCurrencyCode = request[u'CurrencyCode']
  
  # Get Source Transaction Item Id Using TransactionNo
  oRefItemCA = helper.GetObjectByNames(
        'CATransactItem',
        {'LTransaction.TransactionNo' : request[u'RefTransactionNo']}
  ) 
  
  # EmployeeAR Account
  employeeId = request[u'EmployeeId']
  
  oAccount = helper.GetObjectByNames('EmployeeCashAdvance',
    {
      'EmployeeIdNumber': employeeId,
      'CurrencyCode': aCurrencyCode
    }
  )
  if oAccount.isnull:
    raise '','Karyawan Belum Memiliki Rekening Uang Muka'
  
  oItemCAR = oTran.CreateCAReturnTransactItem(oAccount)    
  oItemCAR.SetMutation('C', request[u'RefAmount'], aRate)
  oItemCAR.Description = request[u'Description']  
  oItemCAR.SetFundEntity(oRefItemCA.FundEntity)

  oItemCAR.SetJournalParameter(FundEntityMap[oRefItemCA.FundEntity or 4] )
  
  oItemCAR.SetReturnInfo(oRefItemCA)
  
  # CashAccount Transaction
  aJournalCode = 10
  oCashAccount = helper.GetObject('CashAccount',
    str(request[u'CashAccountNo'])).CastToLowestDescendant()
  if oCashAccount.isnull :
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'CashAccountNo']

  if request[u'Amount'] > 0.0 or request[u'ReimburseAmount'] > 0.0 :
    oItemCA = oTran.CreateAccountTransactionItem(oCashAccount)

    if request[u'Amount'] > 0.0 :
      oItemCA.SetMutation('D', request[u'Amount'], aRate)
    elif request[u'ReimburseAmount'] > 0.0:
      oItemCA.SetMutation('C', request[u'ReimburseAmount'], aRate)
    # end if

    oItemCA.Description = oCashAccount.AccountName #request[u'Description']
    oItemCA.SetJournalParameter('10')
    
    oBudgetTrans = helper.GetObject('BudgetTransaction',request[u'RefTransactionItemId'])
    if not oBudgetTrans.isnull : 
      aBudgetId = oBudgetTrans.BudgetId
      if aBudgetId != 0 :
        oBudget = helper.GetObject('Budget',aBudgetId)
        oItemCA.CreateBudgetTransactionReturn(oBudget.BudgetId)

  aBranchCode = request[u'BranchCode']
  aValuta = oCashAccount.CurrencyCode    
  totalAmount = 0.0
  items = request[u'Items']
  

  for item in items:
    if item[u'ItemType'] == 'D':        
      # Create Item for ProductAccount
      aAccountNo  = item[u'AccountId']
      #oProductAccount = helper.GetObjectByNames('ProductAccount',
      #  {'ProductId': aProductId, 'BranchCode': aBranchCode, 'CurrencyCode': aValuta})
      
      oProductAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo' :aAccountNo})
      if oProductAccount.isnull:
        raise 'Collection', 'Rekening produk %s tidak ditemukan' % (aAccountNo)
      
      oItemPA = oTran.CreateZakahDistTransactItem(oProductAccount, item[u'Ashnaf'])  
      oItemPA.SetMutation('D', item[u'Amount'], aRate)
      oItemPA.Description = item[u'Description']
      oItemPA.SetJournalParameter(aJournalCode)
      oItemPA.SetDistributionEntity(item[u'FundEntity'])
      oItemPA.DistributionItemAccount = item[u'DistItemAccount']
      oItemBudget = oItemPA
      
    elif item[u'ItemType'] == 'G':      
      oItemGL = oTran.CreateGLTransactionItem(item[u'AccountId'], aValuta)
      oItemGL.RefAccountName = item[u'AccountName']
      oItemGL.SetMutation('D', item[u'Amount'], aRate)
      oItemGL.Description = item[u'Description']
      oItemGL.SetJournalParameter('10')
      oItemBudget = oItemGL
                
    elif item[u'ItemType'] == 'A':
      CreateFixAssetTransactionItem( helper, oTran, params, request, item, isCreateRAK=0)

    elif item[u'ItemType'] == 'B':
      CreateCPIATransactionItem( helper, oTran, params, request, item, isCreateRAK=0)

    else:
      raise '','Kode Item Tidak Dikenal'
          
    totalAmount += item[u'Amount']
    #-- if.else
  #-- for
  
  oTran.GenerateTransactionNumber(oCashAccount.CashCode) 
    
  oTran.SaveInbox(params)
  
  return oTran.GetKwitansi()

### ------- End CASH ADVANCE RETURN -----------------------------------

### ------- INVESTMENT -----------------------------------
def Investment(helper,oTran,oBatch,request,params):
  FundEntityMap = {1 : 'AK-Z', 2 : 'AK-I', 3 : 'AK-W', 4 : 'AK-A3'}
  
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']
  oTran.Amount = request[u'Amount']
  oTran.CurrencyCode = '000'
  oTran.ReceivedFrom = request[u'ReceivedFrom']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')

  # Create Investment Account
  InvesteeId = request[u'InvesteeId']
  BranchCode = request[u'BranchCode']

  AccountNo = str(request[u'InvestmentAccountNo'])
  if AccountNo == '' :
    if request[u'InvesteeCategory'] == 1 : # ==> Non Employee
      oAccount = helper.CreatePObject('InvestmentNonEmployee', InvesteeId)
    else : # InvesteeCategory == 2  ==> Employee
      oAccount = helper.CreatePObject('InvestmentEmployee', InvesteeId)
    # end if
  else :
    oAccount = helper.GetObject('Investment',AccountNo).CastToLowestDescendant()
  # end if
  
  if request[u'InvesteeCategory'] == 1 : # ==> Non Employee
    oInvestee = helper.GetObject('Investee',InvesteeId)
    InvesteeName = oInvestee.InvesteeName
  else : # InvesteeCategory == 2  ==> Employee
    oEmployee = helper.GetObject('VEmployee',InvesteeId)
    InvesteeName = oEmployee.EmployeeName
  # end if

  oTran.PaidTo = InvesteeName

  oAccount.BranchCode = request[u'BranchCode']
  oAccount.CurrencyCode = '000'
  oAccount.AccountName  = request[u'Description']
  oAccount.FundEntity = request[u'FundEntity']
  oAccount.InvestmentAmount = request[u'Amount']
  oAccount.SetLifeTime(request[u'LifeTime'])
  oAccount.InvestmentCatId = request[u'InvestmentCatId']
  oAccount.StartDate = request[u'StartDate']
  oAccount.InvestmentNisbah = request[u'Nisbah'] 
 
  #oItemInv = oTran.CreateAccountTransactionItem(oAccount)
  #oItemInv.SetMutation('D', request[u'Amount'], 1.0)
  oItemInv = oTran.CreateInvestmentTransactItem(oAccount)
  oItemInv.SetMutation('D', request[u'Amount'], 0.0, 1.0)
  oItemInv.Description = request[u'Description']
  oItemInv.SetFundEntity(request[u'FundEntity'])
  oItemInv.SetJournalParameter(FundEntityMap[request[u'FundEntity']])
            
  
  # Create BudgetTransaction
  aBudgetId = request[u'BudgetId'] 

  if aBudgetId != 0 :
    oBudget = helper.GetObject('Budget',aBudgetId)
    oItemInv.CreateBudgetTransaction(oBudget.BudgetId)
  # endif 

  # Destination Transaction
  oCashAccount = helper.GetObject('CashAccount',
    str(request[u'CashAccountNo'])).CastToLowestDescendant()
  if oCashAccount.isnull:
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'CashAccountNo']

  oItemCA = oTran.CreateAccountTransactionItem(oCashAccount)
  oItemCA.SetMutation('C', request[u'Amount'], 1.0)    
  oItemCA.Description = request[u'Description']
  oItemCA.SetJournalParameter('10')
  
  oTran.GenerateTransactionNumber(oCashAccount.CashCode)
  oTran.SaveInbox(params)
  
  return oTran.GetKwitansi()

### ------- End INVESTMENT  -----------------------------------


### ------- Begin INVESTMENT RETURN  -----------------------------------  
def InvestmentReturn(helper,oTran,oBatch,request,params):
  FundEntityMap = {1 : 'PI-Z', 2 : 'PI-I', 3 : 'PI-W', 4 : 'PI-A'}
  
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']
  oTran.Amount = request[u'Amount'] + request[u'Share']
  oTran.CurrencyCode = '000'
  oTran.PaidTo = request[u'PaidTo']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
  
  # Investment Account
  oInvestment = helper.GetObject('Investment', str(request[u'InvestmentAccountNo'])).CastToLowestDescendant()
  if oInvestment.isnull:
    raise '','Data Investasi tidak ditemukan' 
  
  if oInvestment.IsA('InvestmentEmployee') :
    oTran.ReceivedFrom = oInvestment.LEmployee.EmployeeName[:100]
  else : # oInvestment.IsA('InvestmentNonEmployee') :
    oTran.ReceivedFrom = oInvestment.LInvestee.InvesteeName[:100]
  # end if

  oItemInvR = oTran.CreateInvestmentTransactItem(oInvestment)
  oItemInvR.SetMutation('C', request[u'Amount'], request[u'Share'], 1.0)
  oItemInvR.Description = request[u'Description']
  oItemInvR.SetFundEntity(oInvestment.FundEntity)
  oItemInvR.SetJournalParameter(FundEntityMap[oInvestment.FundEntity])
  
  
  #oItemShare = oTran.CreateAccountTransactionItem(oInvestment,IsUpdateBalance='F')
  #oItemShare.SetMutation('C', request[u'Share'], 1.0)
  #oItemShare.Description = 'Bagi Hasil'
  #oItemShare.SetFundEntity(oInvestment.FundEntity)  
  # Set Account Bagi Hasil Investasi Pengelola
  #oItemShare.SetAccountInterface('4510603')
  #oItemShare.SetJournalParameter('10')

  # Create BudgetTransaction
#   aBudgetId = request[u'BudgetId'] 
# 
#   if aBudgetId != 0 :
#     oBudget = helper.GetObject('Budget',aBudgetId)
#     oItemInv.CreateBudgetTransaction(oBudget.BudgetId)
  # endif 

  # Destination Transaction
  oCashAccount = helper.GetObject('CashAccount',
    str(request[u'CashAccountNo'])).CastToLowestDescendant()
  if oCashAccount.isnull:
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'CashAccountNo']

  oItemCA = oTran.CreateAccountTransactionItem(oCashAccount)
  oItemCA.SetMutation('D', request[u'Amount'] + request[u'Share'], 1.0)    
  oItemCA.Description = request[u'Description']
  oItemCA.SetJournalParameter('10')
  
  oTran.GenerateTransactionNumber(oCashAccount.CashCode)
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()

  return oTran.GetKwitansi()

### ------- End INVESTMENT RETURN -----------------------------------

### ------- Begin CashAdvance RETURN  -----------------------------------
def CashAdvanceReturnRAK(helper,oTran,oBatch,request,params):
  FundEntityMap = {1 : 'PAK-Z', 2 : 'PAK-I', 3 : 'PAK-W', 4 : 'PAK-A'}
  
  #--- Set Transaction Data
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']
  #oTran.TransactionNo = request[u'TransactionNo']
  oTran.Amount = request[u'RefAmount']
  oTran.CurrencyCode = '000'
  oTran.ReceivedFrom = request[u'EmployeeName']
  oTran.PaidTo = request[u'PaidTo']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
  
  
  #--- EmployeeAR Account
  employeeId = request[u'EmployeeId']
  
  oAccount = helper.GetObjectByNames('EmployeeCashAdvance',
    {
      'EmployeeIdNumber': employeeId,
      'CurrencyCode': '000'
    }
  )
  if oAccount.isnull:
    raise '','Karyawan Belum Memiliki Rekening Uang Muka'    
  
  # Get Source Transaction Item Id Using TransactionNo
  oRefItemCA = helper.GetObject('CATransactItem',request[u'RefTransactionItemId'])
  oDTransferInfo = oRefItemCA.LDistributionTransfer
  
  if request[u'Amount'] > 0.0 :
    oDTransferInfo.UpdateBalance( '+', request[u'Amount'])

  # Create Employee AR Transaction Item
  oItemCAR = oTran.CreateCAReturnTransactItem(oAccount)
  oItemCAR.SetMutation('C', request[u'RefAmount'], 1.0)
  oItemCAR.Description = request[u'Description']
  oItemCAR.SetFundEntity(oRefItemCA.FundEntity)
  #oItemCAR.SetJournalParameter('10')
  oItemCAR.SetJournalParameter(FundEntityMap[oRefItemCA.FundEntity or 4] )
  
  # Set Return Transaction Item
  oRefItemCA.ReturnTransactionItemId = oItemCAR.TransactionItemId

  #--- Destination (Cash) Transaction
  oCashAccount = helper.GetObject('CashAccount',
    str(request[u'CashAccountNo'])).CastToLowestDescendant()
  if oCashAccount.isnull:
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'CashAccountNo']
  
  if request[u'Amount'] > 0.0 :
    # Create Cash Transaction Item
    oItemCA = oTran.CreateAccountTransactionItem(oCashAccount)
    oItemCA.SetMutation('D', request[u'Amount'], 1.0)
    oItemCA.Description = oCashAccount.AccountName #request[u'Description']
    oItemCA.SetJournalParameter('16')
    
    #oItemRAK = oTran.Create

  aBranchCode = request[u'BranchCode']
  aValuta = oCashAccount.CurrencyCode    

  oTran.GenerateTransactionNumber(oCashAccount.CashCode)
  
  oTran.SaveInbox(params)
  
  return oTran.GetKwitansi()
    
def CostPaidInAdvance(helper,oTran,oBatch,request,params):
  # Creating Account
  oAccount = helper.CreatePObject('CostPaidInAdvance')    
  oAccount.BranchCode = request[u'BranchCode']
  if request[u'HasContract'] == 'T':
    oAccount.SetContract(request[u'ContractNo'], request[u'ContractEndDate'])
  else:
    oAccount.SetNoContract()
  #-- if.else
  oAccount.SetInitialValue(request[u'Amount'])
  oAccount.Description = request[u'Description']
  oAccount.CostAccountNo = request[u'CostAccountNo']
  oAccount.CPIACatId = request[u'CPIACatId']

  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']
  oTran.Amount = request[u'Amount']
  oTran.CurrencyCode = '000'
  oTran.ReceivedFrom = request[u'ReceivedFrom']
  oTran.PaidTo = request[u'PaidTo']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')

  oItem = oTran.CreateAccountTransactionItem(oAccount)
  oItem.SetMutation('D', request[u'Amount'], 1.0)
  oItem.Description = request[u'Description']
  oItem.SetJournalParameter('BDD01')

  aBudgetId = request[u'BudgetId'] 
  
  if aBudgetId != 0 :
    oBudget = helper.GetObject('Budget',aBudgetId)
    oItem.CreateBudgetTransaction(oBudget.BudgetId)
  # endif 
  
  # Destination Transaction
  oCashAccount = helper.GetObject('CashAccount',
    str(request[u'CashAccountNo'])).CastToLowestDescendant()
  if oCashAccount.isnull:
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'CashAccountNo']

  oItemCA = oTran.CreateAccountTransactionItem(oCashAccount)
  oItemCA.SetMutation('C', request[u'Amount'], 1.0)    
  oItemCA.Description = request[u'Description']
  oItemCA.SetJournalParameter('10')
  
  oTran.GenerateTransactionNumber(oCashAccount.CashCode)
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi


def InvoicePayment(helper,oTran,oBatch,request,params):
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']
  #oTran.TransactionNo = request[u'TransactionNo']
  oTran.Amount = request[u'RefAmount']
  oTran.CurrencyCode = request[u'CurrencyCode']
  oTran.ReceivedFrom = request[u'EmployeeName']
  oTran.PaidTo = request[u'PaidTo']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')

  aRate = request[u'Rate']
  
  # Get Object Invoice 
  oInvoice = helper.GetObject('InvoiceProduct', request[u'InvoiceId'])
  
  oSponsor = helper.GetObject('Sponsor', oInvoice.SponsorId)

  # Set Transaksi donor id
  oTran.DonorId = oInvoice.SponsorId
  
  # Product Account
  oProductAccount = helper.GetObjectByNames('ProductAccount',
    {'AccountNo': oInvoice.ProductAccountNo}
  ).CastToLowestDescendant()
  if oProductAccount.isnull:
    raise '','Data Produk tidak ditemukan'    
  
  oItemPA = oTran.CreateDonorTransactionItem(oProductAccount, oInvoice.SponsorId)
  oItemPA.SetMutation(request[u'RefAmount'], aRate)
  oItemPA.Description = request[u'Description']
  oItemPA.SetJournalParameter('10')
  oItemPA.SetCollectionEntity(FundEntityMAP['I'])
  oItemPA.PercentageOfAmil = request[u'PercentageOfAmil']
  
  # Update PaymentTransaction Invoice
  oInvoice.InvoicePaymentStatus = 'T'
  oInvoice.PaymentTransactionId = oTran.TransactionId
  oInvoice.PaymentTransactionItemId = oItemPA.TransactionItemId

  # Destination Transaction
  oCashAccount = helper.GetObject('CashAccount',
    str(request[u'CashAccountNo'])).CastToLowestDescendant()
  if oCashAccount.isnull:
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'CashAccountNo']
  
  oItemCA = oTran.CreateAccountTransactionItem(oCashAccount)
  oItemCA.SetMutation('D', request[u'RefAmount'], aRate)
  oItemCA.Description = oCashAccount.AccountName #request[u'Description']
  oItemCA.SetJournalParameter('10')

  aBranchCode = request[u'BranchCode']
  aValuta = oCashAccount.CurrencyCode    

  oTran.GenerateTransactionNumber(oCashAccount.CashCode)
  
  oTran.SaveInbox(params)
  
  FileKwitansi = oTran.GetKwitansi()
    
  return FileKwitansi

def BranchDistribution(helper,oTran,oBatch,request,params):
  aBranchCode = request[u'BranchCode']
  
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = aBranchCode
  oTran.Amount = request[u'Amount']
  oTran.CurrencyCode = '000'
  oTran.PaidTo = request[u'PaidTo']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')    

  # Source Cash Account
  aSourceAccountNo = str(request[u'SourceAccountNo'])
  oSCashAccount = helper.GetObject('CashAccount',
       aSourceAccountNo).CastToLowestDescendant()
  
  if oSCashAccount.isnull:
    raise 'Cash/Bank', 'Kas Asal tidak ditemukan'
  
  oItemCA = oTran.CreateAccountTransactionItem(oSCashAccount)
  oItemCA.SetMutation('C', request[u'Amount'], 1.0)    
  oItemCA.Description = request[u'Description']
  oItemCA.SetJournalParameter('15')
  
  # Create BudgetTransaction
  aBudgetId = request[u'BudgetId'] 
  
  if aBudgetId != 0 :
    oBudget = helper.GetObject('Budget',aBudgetId)
    oItemCA.CreateBudgetTransaction(oBudget.BudgetId)
  # endif 

  # Destination Cash Account    
  aDestBranchCode = request[u'DestBranchCode']
  aDestAccountNo = str(request[u'DestAccountNo'])
  oDCashAccount = helper.GetObject('CashAccount',
       aDestAccountNo).CastToLowestDescendant()
  if oDCashAccount.isnull:
    raise 'Cash/Bank', 'Kas Tujuan tidak ditemukan'
  
  oItemDCA = oTran.CreateAccountTransactionItem(oDCashAccount)
  oItemDCA.SetMutation('D', request[u'Amount'], 1.0)    
  oItemDCA.Description = request[u'Description']
  oItemDCA.SetJournalParameter('15')
  
  oTran.GenerateTransactionNumber(oSCashAccount.CashCode)
  oTran.SaveInbox(params)
  
  
  oTransferInfo = helper.GetObjectByNames( 
     'DistributionTransferInfo',
     { 'TransactionId' : oTran.TransactionId }
  ) 
  
  if oTransferInfo.isnull: 
    oTransferInfo = helper.CreatePObject('DistributionTransferInfo')
    oTransferInfo.TransactionId = oTran.TransactionId
    #oTransferInfo.TransactionItemId = oItemCA.TransactionItemId
  
  oTransferInfo.CashAccountNoDest = aDestAccountNo
  oTransferInfo.CashAccountNoSource = aSourceAccountNo    
  oTransferInfo.SetBalance(request[u'Amount'])
  oTransferInfo.AccountNo = request[u'AccountNo']
  oTransferInfo.BranchSource = aBranchCode
  oTransferInfo.BranchDestination = aDestBranchCode
    
  return oTran.GetKwitansi()

def BranchDistributionReturn(helper,oTran,oBatch,request,params):
  aRate = request[u'Rate']

  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']
  #oTran.TransactionNo = request[u'TransactionNo']
  oTran.Amount = request[u'RefAmount']
  oTran.CurrencyCode = '000'
  oTran.ReceivedFrom = request[u'EmployeeName']
  oTran.PaidTo = request[u'PaidTo']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
  
  # Destination Transaction
  aJournalCode = 15
  oCashAccount = helper.GetObject('CashAccount',
    str(request[u'CashAccountNo'])).CastToLowestDescendant()
  if oCashAccount.isnull:
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'CashAccountNo']

  if request[u'Amount'] > 0.0 :
    oItemCA = oTran.CreateAccountTransactionItem(oCashAccount)
    oItemCA.SetMutation('D', request[u'Amount'], 1.0)
    
    oItemCA.Description = oCashAccount.AccountName #request[u'Description']
    oItemCA.SetJournalParameter('15')
    
    #oBudgetTrans = helper.GetObject('BudgetTransaction',request[u'RefTransactionItemId'])
    
    #aBudgetId = oBudgetTrans.BudgetId
    #if aBudgetId != 0 :
    ##  oBudget = helper.GetObject('Budget',aBudgetId)
    #  oItemCA.CreateBudgetTransactionReturn(oBudget.BudgetId)
      
    # Source BranchCash Account
    #raise '',request[u'BranchCodeDestination']
    oCashAccountDest = helper.GetObject('CashAccount',str(request[u'DestAccountNo'])).CastToLowestDescendant()
    if oCashAccountDest.isnull:
      raise 'Cash/Bank', 'Rekening %s cabang penerima tidak ditemukan' % request[u'DestAccountNo']
    
    oItemDCA = oTran.CreateAccountTransactionItem(oCashAccountDest)
    oItemDCA.SetMutation('D', request[u'Amount'], 1.0)    
    oItemDCA.Description = request[u'Description']
    oItemDCA.SetJournalParameter('15')

  aBranchCode = request[u'BranchCode']
  aValuta = oCashAccount.CurrencyCode
  totalAmount = 0.0
  items = request[u'Items']
  
  for item in items:
    FundEntity = item[u'FundEntity']
    Amount = item[u'Amount']
    if item[u'ItemType'] == 'D':        
      # Create Item for ProductAccount
      aAccountNo  = item[u'AccountId']
      #oProductAccount = helper.GetObjectByNames('ProductAccount',
      #  {'ProductId': aProductId, 'BranchCode': aBranchCode, 'CurrencyCode': aValuta})
      
      oProductAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo' :aAccountNo})
      if oProductAccount.isnull:
        raise 'Collection', 'Rekening produk %s tidak ditemukan' % (aAccountNo)
      
      oItemPA = oTran.CreateZakahDistTransactItem(oProductAccount, item[u'Ashnaf'])  
      oItemPA.SetMutation('D', item[u'Amount'], item[u'Rate'])
      oItemPA.Description = item[u'Description']
      oItemPA.SetJournalParameter(aJournalCode)
      oItemPA.SetDistributionEntity(item[u'FundEntity'])
      oItemPA.DistributionItemAccount = item[u'DistItemAccount']
      oItemBudget = oItemPA
      
    elif item[u'ItemType'] == 'G':      
      oItemGL = oTran.CreateGLTransactionItem(item[u'AccountId'], aValuta)
      oItemGL.RefAccountName = item[u'AccountName']
      oItemGL.SetMutation('D', item[u'Amount'], item[u'Rate'])
      oItemGL.Description = item[u'Description']
      oItemGL.SetJournalParameter(aJournalCode)
      oItemBudget = oItemGL
                
    elif item[u'ItemType'] == 'A':
      CreateFixAssetTransactionItem( helper, oTran, params, request, item, isCreateRAK = 1)
      
    elif item[u'ItemType'] == 'B':
      CreateCPIATransactionItem( helper, oTran, params, request, item, isCreateRAK = 1)
      
    else:
      raise '','Kode Item Tidak Dikenal'
    

    # Create BudgetTransaction
#       aBudgetId = item[u'BudgetId'] 
#  
#       if aBudgetId != 0 :
#         oBudget = helper.GetObject('Budget',aBudgetId)
#         oItemBudget.CreateBudgetTransaction(oBudget.BudgetId)
    # endif 
    
    totalAmount += item[u'Amount']
    #-- if.else
  #-- for

  # Set DistributionInfo
  #oRefTransItem = helper.GetObject('TransactionItem',request[u'RefTransactionItemId'])
  oDistInfo = helper.GetObjectByNames('DistributionTransferInfo',{'TransactionId' : request[u'RefTransactionId']})
  oDistInfo.ReportStatus = 'T'
  oDistInfo.ReportTransactionId = oTran.TransactionId
  
  oTran.GenerateTransactionNumber(oCashAccount.CashCode)
  
  oTran.SaveInbox(params)
  
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi