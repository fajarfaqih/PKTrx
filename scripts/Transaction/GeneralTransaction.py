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

def GeneralTransactionNew(config,srequest ,params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('GT')
    
    FileKwitansi = GeneralTransaction(helper,oTran,oBatch,request,params)
    
    # Check for auto approval
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount'] * request[u'Rate']):
      oTran.AutoApproval()
      
    config.Commit()
  except:
    config.Rollback()
    raise
  
  status,msg = oTran.CreateJournal()
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def GeneralTransactionUpdate(config,srequest ,params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)
  
  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  TranHelper = helper.LoadScript('Transaction.TransactionHelper')
  TranHelper.DeleteTransactionJournal(oTran)

  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
    
    FileKwitansi = GeneralTransaction(helper,oTran,oBatch,request,params)
    
    # Check for auto approval
    oTran.AutoApprovalUpdate()
    
    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)  

def GeneralTransaction(helper,oTran,oBatch,request,params):
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
      oItemPA.SetJournalParameter('C10')
      oItemPA.SetCollectionEntity(item[u'FundEntity'])
      oItemPA.PercentageOfAmil = 0.0

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
def InternalTransferNew(config,srequest ,params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('TI')
    
    FileKwitansi = InternalTransfer(helper,oTran,oBatch,request,params)
    
    # Check for auto approval
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount'] * request[u'Rate']):
      oTran.AutoApproval()
      
    config.Commit()
  except:
    config.Rollback()
    raise
  
  status,msg = oTran.CreateJournal()
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def InternalTransferUpdate(config,srequest ,params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)
  
  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  #oTran.DeleteJournal()

  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
    
    FileKwitansi = InternalTransfer(helper,oTran,oBatch,request,params)
    
    # Check for auto approval
    oTran.AutoApprovalUpdate()
    
    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)  

      
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

  # Source Transaction
  oSrcAccount = helper.GetObject('CashAccount',
    str(request[u'SourceAccountNo'])).CastToLowestDescendant()
  if oSrcAccount.isnull:
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'AccountNo']

  oItemSA = oTran.CreateAccountTransactionItem(oSrcAccount)
  oItemSA.SetMutation('C', request[u'Amount'], request[u'Rate'])
  oItemSA.Description = request[u'Description']
  oItemSA.SetJournalParameter('TI')

  # Destination Transaction
  oDstAccount = helper.GetObject('CashAccount',
    str(request[u'DestAccountNo'])).CastToLowestDescendant()
  if oDstAccount.isnull:
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'AccountNo']

  oItemDA = oTran.CreateAccountTransactionItem(oDstAccount)
  oItemDA.SetMutation('D', request[u'Amount'], request[u'Rate'])
  oItemDA.Description = request[u'Description']
  oItemDA.SetJournalParameter('TI')

  oTran.Amount = request[u'SourceAmount']
  oTran.CurrencyCode = request[u'SourceCurrencyCode']
  oTran.Rate = request[u'SourceRate']
  
  oTran.GenerateTransactionNumber('000')
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi
  
### -------  END INTERNAL TRANSFER -----------------------------------

### -------  INTERFUND TRANSFER -----------------------------------  
def InterFundTransferNew(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)
  
  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('PAD')

    FileKwitansi = InterFundTransfer(helper,oTran,oBatch,request,params)
    
    # Check for auto approval
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount'] * request[u'Rate']):
      oTran.AutoApproval()
    
    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
      
def InterFundTransferUpdate(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  #oTran.DeleteJournal()
  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
    
    FileKwitansi = InterFundTransfer(helper,oTran,oBatch,request,params)
    
    # Check for auto approval
    oTran.AutoApprovalUpdate()
    
    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
      
def InterFundTransfer(helper,oTran,oBatch,request,params):
  FundEntityMap = {1 : 'PADZ', 2 : 'PADI', 3 : 'PADW', 4 : 'PADA' , 5 : 'PADN'}
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
  #raise '',oSrcAccount.GetDistributionInterface(request[u'FundEntitySource'])
  #oItemSA.AccountCode = oSrcAccount.GetDistributionInterface(request[u'FundEntitySource'])  
  oItemSA.SetDistributionEntity(request[u'FundEntitySource'])
  oItemSA.SetJournalParameter(FundEntityMap[request[u'FundEntitySource']])

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
  oItemDA.SetJournalParameter(FundEntityMap[request[u'FundEntityDestination']])
  
  oTran.GenerateTransactionNumber('000')
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi
    

### ------- END INTERFUND TRANSFER -----------------------------------
  

### ------- EMPLOYEE ACCOUNT RECEIVABLE -----------------------------------
def EmployeeARNew(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    if request[u'DebtorType'] == 'E' :
      oTran = oBatch.NewTransaction('EAR')
    else :
      oTran = oBatch.NewTransaction('XAR')  

    FileKwitansi = EmployeeAR(helper,oTran,oBatch,request,params)
     
    # Check for auto approval
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount']):
      oTran.AutoApproval()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
    
def EmployeeARUpdate(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  #oTran.DeleteJournal()

  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
    if request[u'DebtorType'] == 'E' :
      oTran.TransactionCode = 'EAR'
    else :
      oTran.TransactionCode = 'XAR'    
    
    
    FileKwitansi = EmployeeAR(helper,oTran,oBatch,request,params)
  
    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def EmployeeAR(helper,oTran,oBatch,request,params):
    FundEntityMap = {1 : 'AK-Z', 2 : 'AK-I', 3 : 'AK-W', 4 : 'AK-A'}
    
    oTran.ReferenceNo = request[u'ReferenceNo']
    oTran.Description = request[u'Description']
    oTran.Inputer     = request[u'Inputer']
    oTran.BranchCode  = request[u'BranchCode']
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
          'CurrencyCode': '000'
        }
      )
    
      if oAccount.isnull:
        # Create EmployeeAR Account
        oAccount = helper.CreatePObject('EmployeeAccountReceivable', employeeId)
        oAccount.BranchCode = request[u'BranchCode']
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
        oAccount.BranchCode = request[u'BranchCode']
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
    
    # Destination Transaction
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

def PayEmployeeARNew(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    if request[u'DebtorType'] == 'E' :
      oTran = oBatch.NewTransaction('PEAR')
    else :
      oTran = oBatch.NewTransaction('PXAR')
    

    FileKwitansi = PayEmployeeAR(helper,oTran,oBatch,request,params)
     
    # Check for auto approval
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount']):
      oTran.AutoApproval()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
    
def PayEmployeeARUpdate(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  #oTran.DeleteJournal()

  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
    if request[u'DebtorType'] == 'E' :
      oTran.TransactionCode = 'PEAR'
    else :
      oTran.TransactionCode = 'PXAR'
    

    FileKwitansi = PayEmployeeAR(helper,oTran,oBatch,request,params)

    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)

def PayEmployeeAR(helper,oTran,oBatch,request,params):
  FundEntityMap = {1 : 'PAK-Z', 2 : 'PAK-I', 3 : 'PAK-W', 4 : 'PAK-A'}

  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']
  #oTran.TransactionNo = request[u'TransactionNo']
  oTran.Amount = request[u'Amount']
  oTran.CurrencyCode = '000'
  oTran.PaidTo = request[u'Casher']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
  
  # EmployeeAR Account
  employeeId = request[u'EmployeeId']
  if request[u'DebtorType'] == 'E' :    
    oAccount = helper.GetObjectByNames('EmployeeAccountReceivable',
      {
        'EmployeeIdNumber': employeeId,
        'CurrencyCode': '000'
      }
    )
     
    if oAccount.isnull:
      raise 'PayEAR', 'Karyawan belum memiliki rekening piutang'
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
def CashAdvanceNew(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('CA')

    FileKwitansi = CashAdvance(helper,oTran,oBatch,request,params)
     
    # Check for auto approval
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount']):
      oTran.AutoApproval()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)

def CashAdvanceUpdate(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  #oTran.DeleteJournal()

  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
    oTran.TransactionCode = 'CA'

    FileKwitansi = CashAdvance(helper,oTran,oBatch,request,params)

    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def CashAdvance(helper,oTran,oBatch,request,params):
  FundEntityMap = {1 : 'AK-Z', 2 : 'AK-I', 3 : 'AK-W', 4 : 'AK-A'}
  
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']
  oTran.Amount = request[u'Amount']
  oTran.CurrencyCode = '000'
  oTran.ReceivedFrom = request[u'ReceivedFrom']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')

  # EmployeeAR Account
  employeeId = request[u'EmployeeId']
  
  oAccount = helper.GetObjectByNames('EmployeeCashAdvance',
    {
      'EmployeeIdNumber': employeeId,
      'CurrencyCode': '000'
    }
  )
  
  if oAccount.isnull:
    #raise '','Karyawan Belum Memiliki Rekening Uang Muka' 
    # Create EmployeeCashAdvance Account
    oAccount = helper.CreatePObject('EmployeeCashAdvance', employeeId)
    oAccount.BranchCode = request[u'BranchCode']
    oAccount.CurrencyCode = '000'
    oAccount.AccountName  = request[u'EmployeeName']

  oItemCAD = oTran.CreateCATransactItem(oAccount)
  oItemCAD.SetMutation('D', request[u'Amount'], 1.0)
  oItemCAD.Description = request[u'Description']
  #oItemCA.Description = 'Uang Muka'
  oItemCAD.SetFundEntity(request[u'FundEntity'])
  oItemCAD.SetJournalParameter(FundEntityMap[request[u'FundEntity']])
  
  if request[u'DistributionTransferId'] != 0 :
    oItemCAD.DistributionTransferId = request[u'DistributionTransferId']

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
  oItemCA.SetMutation('C', request[u'Amount'], 1.0)    
  oItemCA.Description = request[u'Description']
  oItemCA.SetJournalParameter('10')
  
  oTran.PaidTo = oAccount.AccountName
  #oTran.Rece

  oTran.GenerateTransactionNumber(oCashAccount.CashCode)
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()

  return oTran.GetKwitansi()

### ------- End CASH ADVANCE  -----------------------------------

### ------- Begin CASH ADVANCE RETURN -----------------------------------
def CashAdvanceReturnNew(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('CAR')

    FileKwitansi = CashAdvanceReturn(helper,oTran,oBatch,request,params)
    
    # Check for auto approval
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount']):
      oTran.AutoApproval()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
   
def CashAdvanceReturnUpdate(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  #oTran.DeleteJournal()

  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
    oTran.TransactionCode = 'CAR'

    FileKwitansi = CashAdvanceReturn(helper,oTran,oBatch,request,params)

    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def CashAdvanceReturn(helper,oTran,oBatch,request,params):
  FundEntityMap = {1 : 'PAK-Z', 2 : 'PAK-I', 3 : 'PAK-W', 4 : 'PAK-A'}
    
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
      'CurrencyCode': '000'
    }
  )
  if oAccount.isnull:
    raise '','Karyawan Belum Memiliki Rekening Uang Muka'
  
  oItemCAR = oTran.CreateCAReturnTransactItem(oAccount)    
  oItemCAR.SetMutation('C', request[u'RefAmount'], 1.0)    
  oItemCAR.Description = request[u'Description']  
  oItemCAR.SetFundEntity(oRefItemCA.FundEntity)
  oItemCAR.SetJournalParameter(FundEntityMap[oRefItemCA.FundEntity or 4] )
  
  oItemCAR.SetReturnInfo(oRefItemCA)
  
  # Destination Transaction
  aJournalCode = 10
  oCashAccount = helper.GetObject('CashAccount',
    str(request[u'CashAccountNo'])).CastToLowestDescendant()
  if oCashAccount.isnull:
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'CashAccountNo']

  if request[u'Amount'] > 0.0 :
    oItemCA = oTran.CreateAccountTransactionItem(oCashAccount)
    oItemCA.SetMutation('D', request[u'Amount'], 1.0)
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
      oItemGL.SetJournalParameter('10')
      oItemBudget = oItemGL
                
    elif item[u'ItemType'] == 'A':
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
      oFAAccount.SetInitialValue(item[u'AssetAmount'])
      oFAAccount.SetInitialProcessDate()
      oFAAccount.UangMuka = item[u'Amount']

      if oFAAccount.LAssetCategory.AssetType == 'T' :
        oFAAccount.AccountNoProduct = item[u'AccountId']
      
      # 2. Buat transaksi pembelian asset
      # Set Journal Code berdasarkan PaymentType
      if item[u'AssetPaymentType'] == 'T' :
        JournalCode = 'DA01B'
      else :
        if CashAdvance > 0.0 :
          JournalCode = 'DA01A'
        else:
          JournalCode = 'DA01C'
        # endif
      # endif
                 
      # Buat Transaksi pembelian
      oItemFA = oTran.CreateAccountTransactionItem(oFAAccount)
      oItemFA.SetMutation('D', item[u'Amount'], 1.0)
      oItemFA.Description = item[u'Description']
      oItemFA.SetJournalParameter(JournalCode)
      oItemFA.AccountCode = oFAAccount.GetAssetAccount()  
      
      # simpan nomor akun pada dataset
      recItem = params.uipTransactionItem.GetRecord(item[u'RecordIdx'])
      recItem.AssetAccountNo = oFAAccount.AccountNo      

    elif item[u'ItemType'] == 'B':
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
      oCPIAAccount.SetInitialValue(item[u'Amount'])
      oCPIAAccount.Description = item[u'Description']
      oCPIAAccount.CostAccountNo = item[u'AccountId']
      oCPIAAccount.CPIACatId = item[u'CPIACatId']

      oItem = oTran.CreateAccountTransactionItem(oCPIAAccount)
      oItem.SetMutation('D', item[u'Amount'], 1.0)
      oItem.Description = item[u'Description']
      oItem.SetJournalParameter('BDD01')

      # simpan nomor akun pada dataset
      recItem = params.uipTransactionItem.GetRecord(item[u'RecordIdx'])
      recItem.CPIAAccountNo = oCPIAAccount.AccountNo

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
def InvestmentNew(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('INVS')

    FileKwitansi = Investment(helper,oTran,oBatch,request,params)
     
    # Check for auto approval
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount']):
      oTran.AutoApproval()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)

def InvestmentUpdate(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  #oTran.DeleteJournal()

  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
    oTran.TransactionCode = 'INVS'

    FileKwitansi = Investment(helper,oTran,oBatch,request,params)

    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def Investment(helper,oTran,oBatch,request,params):
  FundEntityMap = {1 : 'AK-Z', 2 : 'AK-I', 3 : 'AK-W', 4 : 'AK-A'}
  
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
  
  oAccount.BranchCode = request[u'BranchCode']
  oAccount.CurrencyCode = '000'
  oAccount.AccountName  = request[u'Description'] #request[u'ManagerName']
  oAccount.FundEntity = request[u'FundEntity']
  oAccount.InvestmentAmount = request[u'Amount']
  oAccount.SetLifeTime(request[u'LifeTime'])
  oAccount.InvestmentCatId = request[u'InvestmentCatId']
  oAccount.StartDate = request[u'StartDate']
  oAccount.InvestmentNisbah = request[u'Nisbah'] 
   
  oItemInv = oTran.CreateAccountTransactionItem(oAccount)
  oItemInv.SetMutation('D', request[u'Amount'], 1.0)
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
def InvestmentReturnNew(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('INVSR')

    FileKwitansi = InvestmentReturn(helper,oTran,oBatch,request,params)
     
    # Check for auto approval
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount']):
      oTran.AutoApproval()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)

def InvestmentReturnUpdate(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  #oTran.DeleteJournal()

  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
    oTran.TransactionCode = 'INVSR'

    FileKwitansi = InvestmentReturn(helper,oTran,oBatch,request,params)

    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def InvestmentReturn(helper,oTran,oBatch,request,params):
  FundEntityMap = {1 : 'PAK-Z', 2 : 'PAK-I', 3 : 'PAK-W', 4 : 'PAK-A'}
  
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']
  oTran.Amount = request[u'Amount'] + request[u'Share'] 
  oTran.CurrencyCode = '000'
  oTran.PaidTo = request[u'PaidTo']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')

  # Investment Account 
  oAccount = helper.GetObject('Investment', str(request[u'InvestmentAccountNo']))  
  if oAccount.isnull:
    raise '','Data Investasi tidak ditemukan' 

  oItemInvR = oTran.CreateAccountTransactionItem(oAccount)
  oItemInvR.SetMutation('C', request[u'Amount'], 1.0)
  oItemInvR.Description = request[u'Description']
  oItemInvR.SetFundEntity(oAccount.FundEntity)
  oItemInvR.SetJournalParameter(FundEntityMap[oAccount.FundEntity])
  
  oItemShare = oTran.CreateAccountTransactionItem(oAccount,IsUpdateBalance='F')
  oItemShare.SetMutation('C', request[u'Share'], 1.0)
  oItemShare.Description = 'Bagi Hasil'
  oItemShare.SetFundEntity(oAccount.FundEntity)  
  # Set Account Bagi Hasil Investasi Pengelola
  oItemShare.SetAccountInterface('4510603')
  oItemShare.SetJournalParameter('10')

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
  oItemCA.SetMutation('D', request[u'Amount']+request[u'Share'], 1.0)    
  oItemCA.Description = request[u'Description']
  oItemCA.SetJournalParameter('10')
  
  oTran.GenerateTransactionNumber(oCashAccount.CashCode)
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()

  return oTran.GetKwitansi()

### ------- End INVESTMENT RETURN -----------------------------------

### ------- Begin CashAdvance RETURN  -----------------------------------
def CashAdvanceReturnRAKNew(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('CARR')

    FileKwitansi = CashAdvanceReturnRAK(helper,oTran,oBatch,request,params)
     
    # Check for auto approval
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount']):
      oTran.AutoApproval()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)

def CashAdvanceReturnRAKUpdate(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  #oTran.DeleteJournal()

  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
    oTran.TransactionCode = 'CARR'

    FileKwitansi = CashAdvanceReturnRAK(helper,oTran,oBatch,request,params)

    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)

def CashAdvanceReturnRAK(helper,oTran,oBatch,request,params):
  
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
  
  # EmployeeAR Account
  employeeId = request[u'EmployeeId']
  
  oAccount = helper.GetObjectByNames('EmployeeCashAdvance',
    {
      'EmployeeIdNumber': employeeId,
      'CurrencyCode': '000'
    }
  )
  if oAccount.isnull:
    raise '','Karyawan Belum Memiliki Rekening Uang Muka'    
  
  oItemCAR = oTran.CreateCAReturnTransactItem(oAccount)
  oItemCAR.SetMutation('C', request[u'RefAmount'], 1.0)
  oItemCAR.Description = request[u'Description']
  oItemCAR.SetJournalParameter('10')

  oRefItemCA = helper.GetObject('CATransactItem',request[u'RefTransactionItemId'])
  oRefItemCA.ReturnTransactionItemId = oItemCAR.TransactionItemId

  # Destination Transaction
  aJournalCode = 10
  oCashAccount = helper.GetObject('CashAccount',
    str(request[u'CashAccountNo'])).CastToLowestDescendant()
  if oCashAccount.isnull:
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'CashAccountNo']

  if request[u'Amount'] > 0.0 :
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
    
def GenerateResponse(Status,ErrMessage,TransactionNo,FileKwitansi):
  response = {}
  response['Status'] = Status
  response['TransactionNo'] = TransactionNo
  response['ErrMessage'] = ErrMessage
  response['FileKwitansi'] = FileKwitansi
  
  return simplejson.dumps(response)

def CostPaidInAdvanceNew(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('CPIA')

    FileKwitansi = CostPaidInAdvance(helper,oTran,oBatch,request,params)
     
    # Check for auto approval
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount']):
      oTran.AutoApproval()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def CostPaidInAdvanceUpdate(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  TranHelper = helper.LoadScript('Transaction.TransactionHelper')
  TranHelper.DeleteTransactionJournal(oTran)

  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId

    FileKwitansi = CostPaidInAdvance(helper,oTran,oBatch,request,params)

    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
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
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')

  oItem = oTran.CreateAccountTransactionItem(oAccount)
  oItem.SetMutation('D', request[u'Amount'], 1.0)
  oItem.Description = request[u'Description']
  oItem.SetJournalParameter('BDD01')
  
  # Destination Transaction
  oCashAccount = helper.GetObject('CashAccount',
    str(request[u'CashAccountNo'])).CastToLowestDescendant()
  if oCashAccount.isnull:
    raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'CashAccountNo']

  oItemCA = oTran.CreateAccountTransactionItem(oCashAccount)
  oItemCA.SetMutation('C', request[u'Amount'], 1.0)    
  oItemCA.Description = request[u'Description']
  oItemCA.SetJournalParameter('10')
  oTran.PaidTo = oAccount.AccountName
  #oTran.Rece
  
  oTran.GenerateTransactionNumber(oCashAccount.CashCode)
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi

def InvoicePaymentNew(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('INVP')

    FileKwitansi = InvoicePayment(helper,oTran,oBatch,request,params)
     
    # Check for auto approval
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount']):
      oTran.AutoApproval()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def InvoicePaymentUpdate(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  TranHelper = helper.LoadScript('Transaction.TransactionHelper')
  TranHelper.DeleteTransactionJournal(oTran)

  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId

    FileKwitansi = InvoicePayment(helper,oTran,oBatch,request,params)

    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)

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
  
  # Product Account
  oProductAccount = helper.GetObjectByNames('ProductAccount',
    {'AccountNo': oInvoice.ProductAccountNo}
  ).CastToLowestDescendant()
  if oProductAccount.isnull:
    raise '','Data Produk tidak ditemukan'    
  
  oItemPA = oTran.CreateDonorTransactionItem(oProductAccount, oInvoice.SponsorId)
  oItemPA.SetMutation(request[u'RefAmount'], aRate)
  oItemPA.Description = request[u'Description']
  oItemPA.SetJournalParameter('INV02')
  oItemPA.SetCollectionEntity(FundEntityMAP['I'])
  
  #oItemPA.PercentageOfAmil = item['PercentageOfAmil']
  
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
