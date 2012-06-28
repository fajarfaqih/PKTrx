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

def DistributionNew(config, srequest ,params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)
  
  oBatchHelper = helper.CreateObject('BatchHelper')
  oBatch = oBatchHelper.GetBatchUser(request['ActualDate'])

  config.BeginTransaction()
  try:
    #oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    
    oHistory = helper.CreatePObject('TransHistoryOfChanges')
    oHistory.ChangeType = 'I'

    oTran = oBatch.NewTransaction('DD001')
    
#     if request[u'PaymentType'] == 'K' : PettyCash 
    if request[u'PaymentType'] == 'C' : 
      FileKwitansi = BranchCashDistribution(helper,oTran,oBatch,request,params)
    elif request[u'PaymentType'] == 'B' :  
      FileKwitansi = BankDistribution(helper,oTran,oBatch,request,params)
    elif request[u'PaymentType'] == 'A' :
      FileKwitansi = AssetDistribution(helper,oTran,oBatch,request,params)
    else :
      raise '','Jenis Pembayaran Tidak Terdaftar'  
      
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
  
def DistributionUpdate(config, srequest ,params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oBatchHelper = helper.CreateObject('BatchHelper')
  oBatch = oBatchHelper.GetBatchUser(request['ActualDate'])

  oTran = helper.GetObjectByNames(
      'Transaction',{'TransactionNo': request[u'TransactionNo'] }
    )
  
  #oTran.DeleteJournal()
  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    # Generate History
    oHistory = helper.CreatePObject('TransHistoryOfChanges')
    oHistory.TransactionNo = oTran.TransactionNo
    oHistory.ChangeType = 'E'

    oTran.CancelTransaction()

    #oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId

#     if request[u'PaymentType'] == 'K' : PettyCash
    if request[u'PaymentType'] == 'C' : 
      FileKwitansi = BranchCashDistribution(helper,oTran,oBatch,request,params)
    elif request[u'PaymentType'] == 'B' :  
      FileKwitansi = BankDistribution(helper,oTran,oBatch,request,params)
    elif request[u'PaymentType'] == 'A' :
      FileKwitansi = AssetDistribution(helper,oTran,oBatch,request,params)
    else :
      raise '','Jenis Pembayaran Tidak Terdaftar'  
    
    # Check for auto approval
    oTran.AutoApprovalUpdate()
    oHistory.NewTransactionNo = oTran.TransactionNo

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def PettyCashDistribution(config, srequest ,params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  status = 0
  msg = '' 
  
  config.BeginTransaction()
  try:
    aInputer    = request[u'Inputer'] 
    aBranchCode = request[u'BranchCode']
    aValuta = request[u'CashCurrency']
    aRate = request[u'Rate']
     
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('DD001')    
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
            
    #aProductBranchCode = request[u'ProductBranchCode']
    #if aProductBranchCode != aBranchCode:
    #  aJournalCode = '15'
    #else:
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
      aAccountNo = item[u'AccountNo']
      oProductAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo':aAccountNo})
      if oProductAccount.isnull:
        raise 'Collection', 'Rekening produk %s tidak ditemukan' % (aAccountNo)
      
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
    
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount']):
      oTran.AutoApproval()
      
    config.Commit()
  except:
    config.Rollback()
    raise
   
  status,msg = oTran.CreateJournal()
  
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
   
def BranchCashDistribution(helper,oTran,oBatch,request,params):
  aInputer    = request[u'Inputer'] 
  aBranchCode = request[u'BranchCode']
  aValuta = request[u'CashCurrency']
  aRate = request[u'Rate'] or 1.0
  aPeriodId = request[u'PeriodId']
  
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
              
  #aProductBranchCode = request[u'ProductBranchCode']
  #if aProductBranchCode != aBranchCode:
  #  aJournalCode = '15'
  #else:
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
    aAccountNo = item[u'AccountNo']
    oProductAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo':aAccountNo})
    if oProductAccount.isnull:
      raise 'Collection', 'Rekening produk %s tidak ditemukan' % (aAccountNo)
    
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
  
  oItemBC = oTran.CreateAccountTransactionItem(oBranchCash)
  oItemBC.SetMutation('C', totalAmount, aRate)
  oItemBC.Description = request[u'Description']
  oItemBC.SetJournalParameter(aJournalCode)
  
  # Generate TransactionNo
  oTran.GenerateTransactionNumber(oBranchCash.CashCode)
  
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()
      
  return FileKwitansi
     
def BankDistribution(helper,oTran,oBatch,request,params):
  aInputer    = request[u'Inputer'] 
  aBranchCode = request[u'BranchCode']
   
  oTran.Inputer     = aInputer
  oTran.BranchCode  = aBranchCode
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.ChannelCode = 'A'
  oTran.PaidTo = request[u'PaidTo']
  oTran.ReceivedFrom = request[u'ReceivedFrom']
  oTran.ActualDate = request[u'ActualDate']
      
  #aProductBranchCode = request[u'ProductBranchCode']
  #if aProductBranchCode != aBranchCode:
  #  aJournalCode = '15'
  #else:
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
    aAccountNo = item[u'AccountNo']
    oProductAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo':aAccountNo})
    if oProductAccount.isnull:
      raise 'Collection', 'Rekening produk %s tidak ditemukan' % (aAccountNo)
    
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

  oItemBA = oTran.CreateAccountTransactionItem(oBankAccount)
  oItemBA.SetMutation('C', totalAmount, aRate)
  oItemBA.Description = item[u'Description']
  oItemBA.SetJournalParameter(aJournalCode)
  
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()
      
  return FileKwitansi
  
def AssetDistribution(helper,oTran,oBatch,request,params):
  aInputer    = request[u'Inputer'] 
  aBranchCode = request[u'BranchCode']           
   
  oTran.Inputer     = aInputer
  oTran.BranchCode  = aBranchCode
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.ChannelCode = 'G'
  oTran.PaidTo = request[u'PaidTo']
  oTran.ReceivedFrom = request[u'ReceivedFrom']
  oTran.ActualDate = request[u'ActualDate']
      
  #aProductBranchCode = request[u'ProductBranchCode']
  #if aProductBranchCode != aBranchCode:
  #  aJournalCode = '15'
  #else:
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
  
  oTran.Rate = aRate
  oTran.CurrencyCode = aValuta
  # Generate TransactionNo
  oTran.GenerateTransactionNumber('000')
  
  totalAmount = 0.0
  items = request[u'Items']
  for item in items:
    aAccountNo = item[u'AccountNo']
    oProductAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo':aAccountNo})
    if oProductAccount.isnull:
      raise 'Collection', 'Rekening produk %s tidak ditemukan' % (aAccountNo)
    
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

  oItemGL = oTran.CreateGLTransactionItem(aAssetCode, aValuta)
  oItemGL.RefAccountName = request[u'AssetName']
  oItemGL.SetMutation('C', totalAmount, aRate)
  oItemGL.Description = item[u'Description']
  oItemGL.SetJournalParameter(aJournalCode)
  
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi
