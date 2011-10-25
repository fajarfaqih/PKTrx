# GeneralTransaction.py
import simplejson
import com.ihsan.foundation.pobjecthelper as phelper

status = 0
msg = ''
FileKwitansi = ''

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
    #oTran.TransactionNo = request[u'TransactionNo']

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
    
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def InternalTransfer(config, srequest ,params):
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

    oTran.GenerateTransactionNumber('000')
    oTran.SaveInbox(params)
    FileKwitansi = oTran.GetKwitansi()
        
    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def InterFundTransfer(config, srequest, params):
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
    oItemSA.AccountCode = oSrcAccount.GetCollectionInterface(request[u'FundEntitySource'])
    oItemSA.SetCollectionEntity(request[u'FundEntitySource'])


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

    # Set Journal Parameter
    PJ = oSrcAccount.LProduct.FundCategory + oDstAccount.LProduct.FundCategory
    #PJ = 'ZI'
    oItemSA.SetJournalParameter('PAD' + PJ)
    oItemDA.SetJournalParameter('PAD' + PJ)

    oTran.GenerateTransactionNumber('000')
    oTran.SaveInbox(params)
    FileKwitansi = oTran.GetKwitansi()
    
    # Check for auto approval
    oTran.AutoApprovalUpdate()
    
    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def EmployeeAR(config, srequest, params):
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

    oTran.GenerateTransactionNumber(oCashAccount.CashCode)
    oTran.SaveInbox(params)
    FileKwitansi = oTran.GetKwitansi()
    
    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
    
def PayEmployeeAR(config, srequest,params):
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

    oTran.GenerateTransactionNumber(oCashAccount.CashCode)
    oTran.SaveInbox(params)
    FileKwitansi = oTran.GetKwitansi()
         
    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def CashAdvance(config, srequest, params):
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

    oTran.ReferenceNo = request[u'ReferenceNo']
    oTran.Description = request[u'Description']
    oTran.Inputer     = request[u'Inputer']
    oTran.BranchCode  = request[u'BranchCode']
    #oTran.TransactionNo = request[u'TransactionNo']
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
      
    oTran.GenerateTransactionNumber(oCashAccount.CashCode)
    oTran.SaveInbox(params)
    FileKwitansi = oTran.GetKwitansi()
        
    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def CashAdvanceReturn(config, srequest, params):
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
#       # Create EmployeeCashAdvance Account
#       oAccount = helper.CreatePObject('EmployeeCashAdvance', employeeId)
#       oAccount.BranchCode = request[u'BranchCode']
#       oAccount.CurrencyCode = '000'
#       oAccount.AccountName  = request[u'EmployeeName']
    
    
    oItemCAR = oTran.CreateCAReturnTransactItem(oAccount)
    oItemCAR.SetMutation('C', request[u'RefAmount'], 1.0)
    oItemCAR.Description = request[u'Description']
    oItemCAR.SetJournalParameter('10')
    #oItemCAR.CATransactionId = 

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
      

      # Create BudgetTransaction
      #aOwnerId  = item[u'OwnerId']
      #aPeriodId = request[u'PeriodId']
      #aItemCode = item[u'DistItemAccount']
#       aBudgetId = item[u'BudgetId'] 
#  
#       if aBudgetId != 0 :
#         oBudget = helper.GetObject('Budget',aBudgetId)
#         oItemBudget.CreateBudgetTransaction(oBudget.BudgetId)
#       # endif 
#       
#       totalAmount += item[u'Amount']
      #-- if.else
    #-- for

    oTran.GenerateTransactionNumber(oCashAccount.CashCode)
    
    oTran.SaveInbox(params)
    
    FileKwitansi = oTran.GetKwitansi()
    
    # Check for auto approval
    oTran.AutoApprovalUpdate()

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
