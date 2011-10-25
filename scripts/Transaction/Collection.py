# Collection.py
import simplejson
import com.ihsan.foundation.pobjecthelper as phelper
import sys

def GenerateResponse(Status,ErrMessage,TransactionNo,FileKwitansi):
  response = {}
  response['Status'] = Status
  response['TransactionNo'] = TransactionNo
  response['ErrMessage'] = ErrMessage
  response['FileKwitansi'] = FileKwitansi

  return simplejson.dumps(response)

def SetTransactionData(oTran,request):

  oTran.Inputer     = request[u'Inputer']
  oTran.BranchCode  = request[u'BranchCode']
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.ActualDate = request[u'ActualDate']
  
  oTran.DonorId = request[u'DonorId']
  oTran.DonorNo = request[u'DonorNo']
  oTran.DonorName = request[u'DonorName']
  
  oTran.SponsorId = request[u'SponsorId']
  oTran.VolunteerId = request[u'VolunteerId']
  

#------------- COLLECTION -------------------
def CollectionNew(config, srequest ,params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)
  
  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('SD001')
    
#     if request[u'PaymentType'] == 'K' : PettyCash 
    if request[u'PaymentType'] == 'C' : 
      FileKwitansi = BranchCashCollection(helper,oTran,oBatch,request,params)
    elif request[u'PaymentType'] == 'B' :  
      FileKwitansi = BankCollection(helper,oTran,oBatch,request,params)
    elif request[u'PaymentType'] == 'A' :
      FileKwitansi = AssetCollection(helper,oTran,oBatch,request,params)
    else :
      raise '','Jenis Pembayaran Tidak Terdaftar'  
      
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

def CollectionUpdate(config, srequest ,params):
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

#     if request[u'PaymentType'] == 'K' : PettyCash
    if request[u'PaymentType'] == 'C' : 
      FileKwitansi = BranchCashCollection(helper,oTran,oBatch,request,params)
    elif request[u'PaymentType'] == 'B' :  
      FileKwitansi = BankCollection(helper,oTran,oBatch,request,params)
    elif request[u'PaymentType'] == 'A' :
      FileKwitansi = AssetCollection(helper,oTran,oBatch,request,params)
    else :
      raise '','Jenis Pembayaran Tidak Terdaftar'  
    
    # Check for auto approval
    oTran.AutoApprovalUpdate()
    
    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
def BranchCashCollection(helper,oTran,oBatch,request,params):
  aInputer    = request[u'Inputer']
  aBranchCode = request[u'BranchCode']
  aValuta = request[u'CashCurrency']
  aRate = request[u'Rate']
  
  oTran.Inputer     = aInputer
  oTran.BranchCode  = aBranchCode
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']  
  oTran.DonorNo = request[u'DonorNo']
  oTran.DonorName = request[u'DonorName']
  oTran.CurrencyCode = aValuta
  oTran.Rate = aRate
  oTran.MarketerId = request[u'MarketerId']
  oTran.ChannelCode = 'R'
    
  aProductBranchCode = request[u'ProductBranchCode']
  if aProductBranchCode != aBranchCode:
    aJournalCode = 'C15'
    aJournalCodeDebit = '15'
  else:
    aJournalCode = 'C10'
    aJournalCodeDebit = '10'
  #-- if.else
  
  # Get Sponsor & volunteer
  oSponsor = helper.GetObject('Sponsor', request[u'SponsorId'])
  oVolunteer = helper.GetObject('Volunteer', str(request[u'VolunteerId']))
  
  oDonor = helper.CreateObject('ExtDonor')
  oDonor.GetData(request[u'DonorId'])

  # Set Information
  oTran.SponsorId = request[u'SponsorId']
  oTran.VolunteerId = request[u'VolunteerId']
  oTran.DonorId = request[u'DonorId']
  oTran.ActualDate = request[u'ActualDate']
  oTran.PaidTo = request[u'PaidTo']
  
  oBranchCash = helper.GetObjectByNames('BranchCash',
        {'BranchCode': aBranchCode, 'CurrencyCode': aValuta})
  if oBranchCash.isnull:
    raise 'Collection', 'Rekening kas cabang %s:%s tidak ditemukan' % (aBranchCode, aValuta)
        
#     oListBranchCash = {}
  totalAmount = 0.0
  items = request[u'Items']
  for item in items:

    # Create Item for ProductAccount
    aAccountNo = item[u'AccountNo']
    oProductAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo':aAccountNo})
    #oProductAccount = helper.GetObject('ProductAccount',aAccountNo)      
    if oProductAccount.isnull:
      raise 'Collection', 'Rekening produk %s tidak ditemukan' % (aAccountNo)
      

    oItemPA = oTran.CreateDonorTransactionItem(oProductAccount, request[u'DonorId'])

    oItemPA.SetMutation(item[u'Amount'], aRate)
    oItemPA.Description = item[u'Description']

    oItemPA.SetJournalParameter('C10')
    oItemPA.SetCollectionEntity(item[u'FundEntity'])
    oItemPA.PercentageOfAmil = item['PercentageOfAmil']

    if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)
    if not oVolunteer.isnull: oVolunteer.AddTransaction(oItemPA)
    if oDonor.IsSponsor() : oDonor.AddTransaction(oItemPA)

    totalAmount += item[u'Amount']
  #-- for
  oTran.Amount = totalAmount
  
  oItemBC = oTran.CreateAccountTransactionItem(oBranchCash)
  oItemBC.SetMutation('D', totalAmount, aRate)
  oItemBC.Description = request[u'Description']
  oItemBC.SetJournalParameter(aJournalCodeDebit)
  
  # Generate TransactionNo
  oTran.GenerateTransactionNumber(oBranchCash.CashCode)
  oTran.SaveInbox(params)
  
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi

def BankCollection(helper,oTran,oBatch,request,params):

  aInputer    = request[u'Inputer']
  aBranchCode = request[u'BranchCode']
  
  oTran.Inputer     = aInputer
  oTran.BranchCode  = aBranchCode
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.DonorNo = request[u'DonorNo']
  oTran.DonorName = request[u'DonorName']
  oTran.MarketerId = request[u'MarketerId'] 
  oTran.ChannelCode = 'A'
  
  aProductBranchCode = request[u'ProductBranchCode']
  if aProductBranchCode != aBranchCode:
    aJournalCode = 'C15'
    aJournalCodeDebit = '15'
  else:
    aJournalCode = 'C10'
    aJournalCodeDebit = '10'

  #-- if.else

  # Get Sponsor & volunteer
  oSponsor = helper.GetObject('Sponsor', request[u'SponsorId'])
  oVolunteer = helper.GetObject('Volunteer', str(request[u'VolunteerId']))
  oDonor = helper.CreateObject('ExtDonor')
  oDonor.GetData(request[u'DonorId'])
  
  # Set Information
  oTran.SponsorId = request[u'SponsorId']
  oTran.VolunteerId = request[u'VolunteerId']
  oTran.DonorId = request[u'DonorId']
  oTran.ActualDate = request[u'ActualDate']
  oTran.PaidTo = request[u'PaidTo']

  aBankAccountNo = str(request[u'BankAccountNo'])
  aRate = request[u'Rate']

  oBankAccount = helper.GetObject('BankCash', aBankAccountNo)
  
  if oBankAccount.isnull:
    raise 'Collection', 'Rekening bank %s tidak ditemukan' % (aBankAccountNo)
  # end if.else

  # Generate TransactionNo
  oTran.GenerateTransactionNumber(oBankAccount.CashCode)

  aValuta = oBankAccount.CurrencyCode
  oTran.CurrencyCode = aValuta
  oTran.Rate = aRate

  totalAmount = 0.0
  items = request[u'Items']
  for item in items:
    # Create Item for ProductAccount
    aAccountNo = item[u'AccountNo']
    #oProductAccount = helper.GetObject('ProductAccount',aAccountNo)
    oProductAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo':aAccountNo})
    if oProductAccount.isnull:
      raise 'Collection', 'Rekening produk %s tidak ditemukan' % (aAccountNo)

    oItemPA = oTran.CreateDonorTransactionItem(oProductAccount, request[u'DonorId'])
    oItemPA.SetMutation(item[u'Amount'], aRate)
    oItemPA.Description = item[u'Description']
    oItemPA.SetJournalParameter('C10')
    oItemPA.SetCollectionEntity(item[u'FundEntity'])
    oItemPA.PercentageOfAmil = item['PercentageOfAmil']

    if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)
    if not oVolunteer.isnull: oVolunteer.AddTransaction(oItemPA)
    if oDonor.IsSponsor() : oDonor.AddTransaction(oItemPA)

    totalAmount += item[u'Amount']
  #-- for
  oTran.Amount = totalAmount
  
  oItemBA = oTran.CreateAccountTransactionItem(oBankAccount)
  oItemBA.SetMutation('D', totalAmount, aRate)
  oItemBA.Description = request[u'Description']
  oItemBA.SetJournalParameter(aJournalCodeDebit)
  
  oTran.SaveInbox(params)
  
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi 

def AssetCollection(helper,oTran,oBatch,request,params):  
  aInputer    = request[u'Inputer']
  aBranchCode = request[u'BranchCode']

  oTran.Inputer     = aInputer
  oTran.BranchCode  = aBranchCode
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.DonorNo = request[u'DonorNo']
  oTran.DonorName = request[u'DonorName']
  oTran.CurrencyCode = request[u'AssetCurrency']
  oTran.MarketerId = request[u'MarketerId']
  oTran.ChannelCode = 'G'
  
  aProductBranchCode = request[u'ProductBranchCode']
  if aProductBranchCode != aBranchCode:
    aJournalCode = 'C15'
    aJournalCodeDebit = '11'
  else:
    aJournalCode = 'C10'
    aJournalCodeDebit = '10'
  #-- if.else


  # Get Sponsor & volunteer
  oSponsor = helper.GetObject('Sponsor', request[u'SponsorId'])
  oVolunteer = helper.GetObject('Volunteer', str(request[u'VolunteerId']))
  oDonor = helper.CreateObject('ExtDonor')
  oDonor.GetData(request[u'DonorId'])

  # Set Information
  oTran.SponsorId = request[u'SponsorId']
  oTran.VolunteerId = request[u'VolunteerId']
  oTran.DonorId = request[u'DonorId']
  oTran.ActualDate = request[u'ActualDate']
  oTran.PaidTo = request[u'PaidTo']

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
    aAccountNo = item[u'AccountNo']
    oProductAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo':aAccountNo})
    #oProductAccount = helper.GetObject('ProductAccount',aAccountNo)
    if oProductAccount.isnull:
      raise 'Collection', 'Rekening produk %s tidak ditemukan' % (aAccountNo)

    oItemPA = oTran.CreateDonorTransactionItem(oProductAccount, request[u'DonorId'])
    oItemPA.SetMutation(item[u'Amount'], aRate)
    oItemPA.Description = item[u'Description']
    oItemPA.SetJournalParameter('C10')
    oItemPA.SetCollectionEntity(item[u'FundEntity'])
    oItemPA.PercentageOfAmil = item['PercentageOfAmil']

    if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)
    if not oVolunteer.isnull: oVolunteer.AddTransaction(oItemPA)
    if oDonor.IsSponsor() : oDonor.AddTransaction(oItemPA)

    totalAmount += item[u'Amount']
  #-- for
  oTran.Amount = totalAmount
  
  oItemGL = oTran.CreateGLTransactionItem(aAssetCode, aValuta)
  oItemGL.RefAccountName = request[u'AssetName']
  oItemGL.SetMutation('D', totalAmount, aRate)
  oItemGL.Description = item[u'Description']
  oItemGL.SetJournalParameter(aJournalCodeDebit)

  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()

  return FileKwitansi

def PettyCashCollection(config, srequest ,params):
  aInputer = request[u'Inputer']
  aBranchCode = request[u'BranchCode']
  aValuta = request[u'CashCurrency']
  aRate = request[u'Rate']
  
  aProductBranchCode = request[u'ProductBranchCode']
  if aProductBranchCode != aBranchCode :
    aJournalCode = 'C15'
    aJournalCodeDebit = '15'
  else:
    aJournalCode = 'C10'
    aJournalCodeDebit = '10'
  #-- if.else
  
  oTran.Inputer     = aInputer
  oTran.BranchCode  = aBranchCode
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.DonorNo = request[u'DonorNo']
  oTran.DonorName = request[u'DonorName']
  oTran.ChannelCode = 'P'
  oTran.CurrencyCode = aValuta
  oTran.Rate = aRate 

  # Get Sponsor & volunteer
  oSponsor = helper.GetObject('Sponsor', request[u'SponsorId'])
  oVolunteer = helper.GetObject('Volunteer', str(request[u'VolunteerId']))
  oDonor = helper.CreateObject('ExtDonor')
  oDonor.GetData(request[u'DonorId'])

  # Set Information
  oTran.SponsorId = request[u'SponsorId']
  oTran.VolunteerId = request[u'VolunteerId']
  oTran.DonorId = request[u'DonorId']
  oTran.ActualDate = request[u'ActualDate']
  oTran.PaidTo = request[u'PaidTo']

  oPettyCash = helper.GetObjectByNames('PettyCash',
    {'UserName': aInputer, 'BranchCode': aBranchCode, 'CurrencyCode': aValuta})
  if oPettyCash.isnull:
    raise 'Collection', 'Rekening kas kecil %s:%s tidak ditemukan' % (aInputer, aValuta)
  
  totalAmount = 0.0
  items = request[u'Items']
  for item in items:
    # Create Item for ProductAccount      
    aAccountNo = item[u'AccountNo']
    aProductId = item[u'ProductId']
    oProductAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo':aAccountNo})
    if oProductAccount.isnull:
      raise 'Collection', 'Rekening produk %s tidak ditemukan' % (aAccountNo)

    oItemPA = oTran.CreateDonorTransactionItem(oProductAccount, request[u'DonorId'])
    oItemPA.SetMutation(item[u'Amount'], aRate)
    oItemPA.Description = item[u'Description']
    oItemPA.SetJournalParameter('C10')
    oItemPA.SetCollectionEntity(item[u'FundEntity'])
    oItemPA.PercentageOfAmil = item['PercentageOfAmil']

    if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)        
    if not oVolunteer.isnull: oVolunteer.AddTransaction(oItemPA)      
    if oDonor.IsSponsor() : oDonor.AddTransaction(oItemPA)
    
    totalAmount += item[u'Amount']
      
  #-- for
  oTran.Amount = totalAmount
  
  oItemPC = oTran.CreateAccountTransactionItem(oPettyCash)
  oItemPC.SetMutation('D', totalAmount, aRate)
  oItemPC.Description = request[u'Description']
  oItemPC.SetJournalParameter(aJournalCodeDebit)
  
  oTran.GenerateTransactionNumber(oPettyCash.CashCode)
  oTran.SaveInbox(params)

  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi
