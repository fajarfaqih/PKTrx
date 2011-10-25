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
    aInputer    = request[u'Inputer']
    aBranchCode = request[u'BranchCode']

    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('TM')
    oTran.Inputer     = aInputer
    oTran.BranchCode  = aBranchCode
    oTran.ReferenceNo = request[u'ReferenceNo']
    oTran.Description = request[u'Description']
    oTran.Amount = request[u'TotalCredit']
#     oTran.CurrencyCode = request[u'CashCurrency']

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
        oProductAccount = helper.GetObjectByNames('ProductAccount',
          {'ProductId': aProductId, 'BranchCode': aBranchCode, 'CurrencyCode': aValuta})
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

        oSponsor = helper.GetObject('Sponsor', item[u'SponsorId'])
        if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)
        oVolunteer = helper.GetObject('Volunteer', str(item[u'VolunteerId']))
        if not oVolunteer.isnull: oVolunteer.AddTransaction(oItemPA)

      elif aItemType == 'D':
      # Distribution Transaction (Product)
        aProductId  = item[u'ProductId']
        oProductAccount = helper.GetObjectByNames('ProductAccount',
          {'ProductId': aProductId, 'BranchCode': aBranchCode, 'CurrencyCode': aValuta})
        if oProductAccount.isnull:
          raise 'Collection', 'Rekening produk %d:%s tidak ditemukan' % (aProductId, aValuta)

        oItemPA = oTran.CreateZakahDistTransactItem(oProductAccount, item[u'Ashnaf'])
        oItemPA.SetMutation(item[u'MutationType'], aAmount, aRate)
        oItemPA.Description = aDesc
        oItemPA.SetJournalParameter('10')
        oItemPA.SetDistributionEntity(item[u'FundEntity'])
        oItemPA.DistributionItemAccount = item[u'DistItemAccount']

        oSponsor = helper.GetObject('Sponsor', item[u'SponsorId'])
        if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)
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
    
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'TotalDebit']):
      oTran.AutoApproval()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)

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
    oTran = oBatch.NewTransaction('EAR')

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
    oTran.TransactionCode = 'EAR'
    
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
      
    oTran.PaidTo = request[u'EmployeeName']
    
    oItemAR = oTran.CreateAccountTransactionItem(oAccount)
    oItemAR.SetMutation('D', request[u'Amount'], 1.0)
    oItemAR.Description = request[u'Description']
    oItemAR.SetJournalParameter('10')
    
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
    oTran = oBatch.NewTransaction('PEAR')

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
    oTran.TransactionCode = 'PEAR'

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
  oAccount = helper.GetObjectByNames('EmployeeAccountReceivable',
    {
      'EmployeeIdNumber': employeeId,
      'CurrencyCode': '000'
    }
  )
   
  if oAccount.isnull:
    raise 'PayEAR', 'Karyawan belum memiliki rekening piutang'
  
  oTran.ReceivedFrom = oAccount.AccountName[:30]
  
  oItemAR = oTran.CreateAccountTransactionItem(oAccount)
  oItemAR.SetMutation('C', request[u'Amount'], 1.0)
  oItemAR.Description = request[u'Description']
  oItemAR.SetJournalParameter('10')

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
  
def CashAdvance(config, srequest, params):
  
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
  oItemCAD.SetJournalParameter('10')
  
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

    FileKwitansi = CashAdvanceReturn(config, srequest, params)
    
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
  
def CashAdvanceReturn(config, srequest, params):
  
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
                  
      else:
        raise '','Kode Item Tidak Dikenal'
            
      totalAmount += item[u'Amount']
      #-- if.else
    #-- for
    oTran.GenerateTransactionNumber(oCashAccount.CashCode)
    
    oTran.SaveInbox(params)
    
    return oTran.GetKwitansi()

### ------- End CASH ADVANCE RETURN -----------------------------------


def CashAdvanceReturnRAK(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('CARR')

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
    
    FileKwitansi = oTran.GetKwitansi()
    
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
  
def GenerateResponse(Status,ErrMessage,TransactionNo,FileKwitansi):
  response = {}
  response['Status'] = Status
  response['TransactionNo'] = TransactionNo
  response['ErrMessage'] = ErrMessage
  response['FileKwitansi'] = FileKwitansi
  
  return simplejson.dumps(response)

def CostPaidInAdvance(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  status = 0
  msg = ''
   
  config.BeginTransaction()
  try:
    # Createing Account
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
    
    # Creating Transaction
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('CPA')

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

def InvoicePayment(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('INVP')
    
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
    aRate = 1.0
    
    # Get Object Invoice 
    oInvoice = helper.GetObject('InvoiceProduct', request[u'InvoiceId'])
    oInvoice.InvoicePaymentStatus = 'T'

    oSponsor = helper.GetObject('Sponsor', oInvoice.SponsorId)
    
    # Product Account
    oProductAccount = helper.GetObjectByNames('ProductAccount',
      {'AccountNo': oInvoice.ProductAccountNo}
    ).CastToLowestDescendant()
    if oProductAccount.isnull:
      raise '','Data Produk tidak ditemukan'    
    
    oItemPA = oTran.CreateDonorTransactionItem(oProductAccount, oInvoice.SponsorId)
    oItemPA.SetMutation(request[u'Amount'], aRate)
    oItemPA.Description = request[u'Description']
    oItemPA.SetJournalParameter('INV02')
    oItemPA.SetCollectionEntity(FundEntityMAP['I'])
    
    #oItemPA.PercentageOfAmil = item['PercentageOfAmil']

    # Destination Transaction
    oCashAccount = helper.GetObject('CashAccount',
      str(request[u'CashAccountNo'])).CastToLowestDescendant()
    if oCashAccount.isnull:
      raise 'Cash/Bank', 'Rekening %s tidak ditemukan' % request[u'CashAccountNo']
    
    oItemCA = oTran.CreateAccountTransactionItem(oCashAccount)
    oItemCA.SetMutation('D', request[u'Amount'], 1.0)
    oItemCA.Description = oCashAccount.AccountName #request[u'Description']
    oItemCA.SetJournalParameter('10')

    aBranchCode = request[u'BranchCode']
    aValuta = oCashAccount.CurrencyCode    

    oTran.GenerateTransactionNumber(oCashAccount.CashCode)
    
    oTran.SaveInbox(params)
    
    FileKwitansi = oTran.GetKwitansi()
    
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