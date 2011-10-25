# Distribution.py
import simplejson
import com.ihsan.foundation.pobjecthelper as phelper

def GenerateResponse(Status,ErrMessage,TransactionNo,FileKwitansi):
  response = {}
  response['Status'] = Status
  response['TransactionNo'] = TransactionNo
  response['ErrMessage'] = ErrMessage
  response['FileKwitansi'] = FileKwitansi
  
  return simplejson.dumps(response)

def PettyCashDistribution(config, srequest ,params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  #status,msg = oTran.DeleteJournal()

  status = 0
  msg = '' 
  
  config.BeginTransaction()
  try:
    aInputer    = request[u'Inputer'] 
    aBranchCode = request[u'BranchCode']
    aValuta = request[u'CashCurrency']
    aRate = request[u'Rate']
    
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
         
    oTran.Inputer     = aInputer
    oTran.BranchCode  = aBranchCode
    oTran.ReferenceNo = request[u'ReferenceNo']
    oTran.Description = request[u'Description']
    oTran.ChannelCode = 'P'
    oTran.PaidTo = request[u'PaidTo'] 
    oTran.CurrencyCode = aValuta
    oTran.ReceivedFrom = request[u'ReceivedFrom']
    oTran.ActualDate = request[u'ActualDate']
    oTran.Rate = aRate
            
    aProductBranchCode = request[u'ProductBranchCode']
    if aProductBranchCode != aBranchCode:
      aJournalCode = '15'
    else:
      aJournalCode = '10'
    #-- if.else

        
    # Get Sponsor
    oSponsor = helper.GetObject('Sponsor', request[u'SponsorId'])
    oVolunteer = helper.GetObject('Volunteer', str(request[u'VolunteerId']))
    oDonor = helper.CreateObject('ExtDonor')
    oDonor.GetData(request[u'DonorId'])
    
    # Set Information 
    oTran.SponsorId = request[u'SponsorId']
    oTran.VolunteerId = request[u'VolunteerId']
    
    oPettyCash = helper.GetObjectByNames('PettyCash',
      {'UserName': aInputer, 'BranchCode': aBranchCode, 'CurrencyCode': aValuta})
    if oPettyCash.isnull:
      raise 'Collection', 'Rekening kas kecil %s:%s tidak ditemukan' % (aInputer, aValuta)
          
    totalAmount = 0.0
    items = request[u'Items']
    for item in items:
      
      # Create Item for ProductAccount
#       aProductId  = item[u'ProductId']
#       oProductAccount = helper.GetObjectByNames('ProductAccount',
#         {'ProductId': aProductId, 'BranchCode': aProductBranchCode, 'CurrencyCode': aValuta})
      aAccountNo = item[u'AccountNo']
      oProductAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo':aAccountNo})  
      if oProductAccount.isnull:
        raise 'Collection', 'Rekening produk %d:%s tidak ditemukan' % (aProductId, aValuta)
      
      oItemPA = oTran.CreateZakahDistTransactItem(oProductAccount, item[u'Ashnaf'])  
      oItemPA.SetMutation('D', item[u'Amount'], aRate)
      oItemPA.Description = item[u'Description']
      oItemPA.SetJournalParameter(aJournalCode)
      oItemPA.SetDistributionEntity(item[u'FundEntity'])
      oItemPA.DistributionItemAccount = item[u'DistItemAccount']
      
      if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)
      if not oVolunteer.isnull: oVolunteer.AddTransaction(oItemPA)
      if oDonor.IsSponsor() : oDonor.AddTransaction(oItemPA)
        
      # Create BudgetTransaction
      aBudgetId = item[u'BudgetId'] 
 
      if aBudgetId != 0 :
        oBudget = helper.GetObject('Budget',aBudgetId)
        oItemPA.CreateBudgetTransaction(oBudget.BudgetId)
      # endif 
      
      totalAmount += item[u'Amount']
    #-- for
    oTran.Amount = totalAmount
    
    oItemPC = oTran.CreateAccountTransactionItem(oPettyCash)
    oItemPC.SetMutation('C', totalAmount, aRate)
    oItemPC.Description = request[u'Description']
    oItemPC.SetJournalParameter(aJournalCode)
    
    # Generate TransactionNo
    oTran.GenerateTransactionNumber(oPettyCash.CashCode)
    oTran.SaveInbox(params)
    FileKwitansi = oTran.GetKwitansi()
    
    oTran.AutoApprovalUpdate()
      
    config.Commit()
  except:
    config.Rollback()
    raise
   
  status,msg = oTran.CreateJournal()
  
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
   
def BranchCashDistribution(config, srequest ,params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  status = 0
  msg = '' 
  
  config.BeginTransaction()
  try:
    aInputer    = request[u'Inputer'] 
    aBranchCode = request[u'BranchCode']
    aValuta = request[u'CashCurrency']
    aRate = request[u'Rate']
    
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
        
    oTran.Inputer     = aInputer
    oTran.BranchCode  = aBranchCode
    oTran.ReferenceNo = request[u'ReferenceNo']
    oTran.Description = request[u'Description']
    oTran.ChannelCode = 'R'
    oTran.PaidTo = request[u'PaidTo']
    oTran.ReceivedFrom = request[u'ReceivedFrom']
    oTran.ActualDate = request[u'ActualDate']
    oTran.Rate = aRate
    oTran.CurrencyCode = aValuta
            
    aProductBranchCode = request[u'ProductBranchCode']
    if aProductBranchCode != aBranchCode:
      aJournalCode = '15'
    else:
      aJournalCode = '10'
    #-- if.else
    
    # Get Sponsor
    oSponsor = helper.GetObject('Sponsor', request[u'SponsorId'])
    oVolunteer = helper.GetObject('Volunteer', str(request[u'VolunteerId']))
    oDonor = helper.CreateObject('ExtDonor')
    oDonor.GetData(request[u'DonorId'])
    
    # Set Information 
    oTran.SponsorId = request[u'SponsorId']
    oTran.VolunteerId = request[u'VolunteerId']

    oBranchCash = helper.GetObjectByNames('BranchCash',
      {'BranchCode': aBranchCode, 'CurrencyCode': aValuta})
    if oBranchCash.isnull:
      raise 'Collection', 'Rekening kas cabang %s:%s tidak ditemukan' % (aBranchCode, aValuta)
      
    totalAmount = 0.0
    items = request[u'Items']
     
    for item in items:
      # Create Item for ProductAccount
#       aProductId  = item[u'ProductId']
#       oProductAccount = helper.GetObjectByNames('ProductAccount',
#         {'ProductId': aProductId, 'BranchCode': aProductBranchCode, 'CurrencyCode': aValuta})
      aAccountNo = item[u'AccountNo']
      oProductAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo':aAccountNo})
      if oProductAccount.isnull:
        raise 'Collection', 'Rekening produk %d:%s tidak ditemukan' % (aProductId, aValuta)
      
      oItemPA = oTran.CreateZakahDistTransactItem(oProductAccount, item[u'Ashnaf'])  
      oItemPA.SetMutation('D', item[u'Amount'], aRate)
      oItemPA.Description = item[u'Description']
      oItemPA.SetJournalParameter(aJournalCode)
      oItemPA.SetDistributionEntity(item[u'FundEntity'])
      oItemPA.DistributionItemAccount = item[u'DistItemAccount']
      
      if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)      
      if not oVolunteer.isnull: oVolunteer.AddTransaction(oItemPA)
      if oDonor.IsSponsor() : oDonor.AddTransaction(oItemPA)
      
      # Create BudgetTransaction
      #aOwnerId  = item[u'OwnerId']
      #aPeriodId = request[u'PeriodId']
      #aItemCode = item[u'DistItemAccount']
      aBudgetId = item[u'BudgetId'] 
 
      if aBudgetId != 0 :
        oBudget = helper.GetObject('Budget',aBudgetId)
        oItemPA.CreateBudgetTransaction(oBudget.BudgetId)
      # endif 
      totalAmount += item[u'Amount']     
    #-- for
    oTran.Amount = totalAmount
    
    oItemBC = oTran.CreateAccountTransactionItem(oBranchCash)
    oItemBC.SetMutation('C', totalAmount, aRate)
    oItemBC.Description = request[u'Description']
    oItemBC.SetJournalParameter(aJournalCode)
    
    # Generate TransactionNo
    oTran.GenerateTransactionNumber(oBranchCash.CashCode)
    
    oTran.SaveInbox(params)
    FileKwitansi = oTran.GetKwitansi()
        
    oTran.AutoApprovalUpdate()
      
    config.Commit()
  except:
    config.Rollback()
    raise
   
  status,msg = oTran.CreateJournal()
  
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def BankDistribution(config, srequest ,params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  status = 0
  msg = '' 
  
  config.BeginTransaction()
  try:
    aInputer    = request[u'Inputer'] 
    aBranchCode = request[u'BranchCode']
     
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
        
    oTran.Inputer     = aInputer
    oTran.BranchCode  = aBranchCode
    oTran.ReferenceNo = request[u'ReferenceNo']
    oTran.Description = request[u'Description']
    oTran.ChannelCode = 'A'
    oTran.PaidTo = request[u'PaidTo']
    oTran.ReceivedFrom = request[u'ReceivedFrom']
    oTran.ActualDate = request[u'ActualDate']
    
        
    aProductBranchCode = request[u'ProductBranchCode']
    if aProductBranchCode != aBranchCode:
      aJournalCode = '15'
    else:
      aJournalCode = '10'
    #-- if.else
    
    
    # Get Sponsor
    oSponsor = helper.GetObject('Sponsor', request[u'SponsorId'])
    oVolunteer = helper.GetObject('Volunteer', str(request[u'VolunteerId']))
    oDonor = helper.CreateObject('ExtDonor')
    oDonor.GetData(request[u'DonorId'])
    
    # Set Information 
    oTran.SponsorId = request[u'SponsorId']
    oTran.VolunteerId = request[u'VolunteerId']

    aBankAccountNo = str(request[u'BankAccountNo'])
    aRate = request[u'Rate']
    oTran.Rate = aRate
    
    oBankAccount = helper.GetObject('BankCash', aBankAccountNo)
    if oBankAccount.isnull:
      raise 'Collection', 'Rekening bank %s tidak ditemukan' % (aBankAccountNo)
    
    # Generate TransactionNo
    oTran.GenerateTransactionNumber(oBankAccount.CashCode)
    
    aValuta = oBankAccount.CurrencyCode
    oTran.CurrencyCode = aValuta
    
    totalAmount = 0.0
    items = request[u'Items']
    for item in items:
      # Create Item for ProductAccount
#       aProductId  = item[u'ProductId']
#       oProductAccount = helper.GetObjectByNames('ProductAccount',
#         {'ProductId': aProductId, 'BranchCode': aProductBranchCode, 'CurrencyCode': aValuta})
      aAccountNo = item[u'AccountNo']
      oProductAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo':aAccountNo})
      if oProductAccount.isnull:
        raise 'Collection', 'Rekening produk %d:%s tidak ditemukan' % (aProductId, aValuta)
      
      oItemPA = oTran.CreateZakahDistTransactItem(oProductAccount, item[u'Ashnaf'])  
      oItemPA.SetMutation('D', item[u'Amount'], aRate)
      oItemPA.Description = item[u'Description']
      oItemPA.SetJournalParameter(aJournalCode)
      oItemPA.SetDistributionEntity(item[u'FundEntity'])
      oItemPA.DistributionItemAccount = item[u'DistItemAccount']
      
      if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)
      if not oVolunteer.isnull: oVolunteer.AddTransaction(oItemPA)
      if oDonor.IsSponsor() : oDonor.AddTransaction(oItemPA)

      # Create BudgetTransaction
      #aOwnerId  = item[u'OwnerId']
      #aPeriodId = request[u'PeriodId']
      #aItemCode = item[u'DistItemAccount']
      aBudgetId = item[u'BudgetId'] 
 
      if aBudgetId != 0 :
        oBudget = helper.GetObject('Budget',aBudgetId)
        oItemPA.CreateBudgetTransaction(oBudget.BudgetId)
      # endif 
      
      totalAmount += item[u'Amount']
      #-- if.else
    #-- for
    oTran.Amount = totalAmount
    
    oItemBA = oTran.CreateAccountTransactionItem(oBankAccount)
    oItemBA.SetMutation('C', totalAmount, aRate)
    oItemBA.Description = item[u'Description']
    oItemBA.SetJournalParameter(aJournalCode)
    
    oTran.SaveInbox(params)
    FileKwitansi = oTran.GetKwitansi()
        
    oTran.AutoApprovalUpdate()
      
    config.Commit()
  except:
    config.Rollback()
    raise
   
  status,msg = oTran.CreateJournal()  
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def AssetDistribution(config, srequest ,params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  status = 0
  msg = '' 
  
  config.BeginTransaction()
  try:
    aInputer    = request[u'Inputer'] 
    aBranchCode = request[u'BranchCode']           
    
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
         
    oTran.Inputer     = aInputer
    oTran.BranchCode  = aBranchCode
    oTran.ReferenceNo = request[u'ReferenceNo']
    oTran.Description = request[u'Description']
    oTran.ChannelCode = 'G'
    oTran.PaidTo = request[u'PaidTo']
    oTran.ReceivedFrom = request[u'ReceivedFrom']
    oTran.ActualDate = request[u'ActualDate']
        
    aProductBranchCode = request[u'ProductBranchCode']
    if aProductBranchCode != aBranchCode:
      aJournalCode = '15'
    else:
      aJournalCode = '10'
    #-- if.else
    
    
    # Get Sponsor
    oSponsor = helper.GetObject('Sponsor', request[u'SponsorId'])
    oVolunteer = helper.GetObject('Volunteer', str(request[u'VolunteerId']))
    oDonor = helper.CreateObject('ExtDonor')
    oDonor.GetData(request[u'DonorId'])
    
    # Set Information 
    oTran.SponsorId = request[u'SponsorId']
    oTran.VolunteerId = request[u'VolunteerId']

    aAssetCode = request[u'AssetCode']
    aValuta    = request[u'AssetCurrency']
    aRate      = request[u'Rate']
    oTran.CurrencyCode = aValuta
    oTran.Rate = aRate
    
    # Generate TransactionNo
    oTran.GenerateTransactionNumber('000')
    
    totalAmount = 0.0
    items = request[u'Items']
    for item in items:
      # Create Item for ProductAccount
#       aProductId  = item[u'ProductId']
#       oProductAccount = helper.GetObjectByNames('ProductAccount',
#         {'ProductId': aProductId, 'BranchCode': aProductBranchCode, 'CurrencyCode': aValuta})
      aAccountNo = item[u'AccountNo']
      oProductAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo':aAccountNo})
      if oProductAccount.isnull:
        raise 'Collection', 'Rekening produk %d:%s tidak ditemukan' % (aProductId, aValuta)
      
      oItemPA = oTran.CreateZakahDistTransactItem(oProductAccount, item[u'Ashnaf'])  
      oItemPA.SetMutation('D', item[u'Amount'], aRate)
      oItemPA.Description = item[u'Description']
      oItemPA.SetJournalParameter(aJournalCode)
      oItemPA.SetDistributionEntity(item[u'FundEntity'])
      oItemPA.DistributionItemAccount = item[u'DistItemAccount']
      
      if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)
      if not oVolunteer.isnull: oVolunteer.AddTransaction(oItemPA)
      if oDonor.IsSponsor() : oDonor.AddTransaction(oItemPA)
      
      # Create BudgetTransaction
      #aOwnerId  = item[u'OwnerId']
      #aPeriodId = request[u'PeriodId']
      #aItemCode = item[u'DistItemAccount']
      aBudgetId = item[u'BudgetId'] 
 
      if aBudgetId != 0 :
        oBudget = helper.GetObject('Budget',aBudgetId)
        oItemPA.CreateBudgetTransaction(oBudget.BudgetId)
      # endif 
      
      totalAmount += item[u'Amount']
      #-- if.else
    #-- for
    oTran.Amount = totalAmount
    
    oItemGL = oTran.CreateGLTransactionItem(aAssetCode, aValuta)
    oItemGL.RefAccountName = request[u'AssetName']
    oItemGL.SetMutation('C', totalAmount, aRate)
    oItemGL.Description = item[u'Description']
    oItemGL.SetJournalParameter(aJournalCode)
    
    oTran.SaveInbox(params)
    FileKwitansi = oTran.GetKwitansi()
        
    oTran.AutoApprovalUpdate()
      
    config.Commit()
  except:
    config.Rollback()
    raise
   
  status,msg = oTran.CreateJournal()  
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
