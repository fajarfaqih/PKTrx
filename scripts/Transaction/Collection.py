# Collection.py
import simplejson
import com.ihsan.foundation.pobjecthelper as phelper
import sys

def GenerateResponse(Status, ErrMessage, TransactionNo, FileKwitansi):
  response = {}
  response['Status'] = Status
  response['TransactionNo'] = TransactionNo
  response['ErrMessage'] = ErrMessage
  response['FileKwitansi'] = FileKwitansi

  return simplejson.dumps(response)

def SetTransactionData(oTran, request):

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
  

def GetDataDonor(helper, DonorId):
  oDonor = helper.CreateObject('ExtDonor')
  oDonor.GetData(DonorId)

  return oDonor

#------------- COLLECTION -------------------
# dictJournalCode = { FunEntity : JournalCode }
dictJournalCode = {
  1 : 'C10Z', 
  2 : 'C10I', 
  3 : 'C10W', 
  4 : '10', 
  5 : '10'
}

def ExecFunction(PaymentType, helper, oTran, oBatch, request, params):
  if PaymentType == 'K' : 
    FileKwitansi = PettyCashCollection(helper, oTran, oBatch, request, params)
  elif PaymentType == 'C' : 
    FileKwitansi = BranchCashCollection(helper, oTran, oBatch, request, params)
  elif PaymentType == 'B' :  
    FileKwitansi = BankCollection(helper, oTran, oBatch, request, params)
  elif PaymentType == 'A' :
    FileKwitansi = AssetCollection(helper, oTran, oBatch, request, params)
  else :
    raise '', 'Jenis Pembayaran Tidak Terdaftar'  

  return FileKwitansi

def CollectionNew(config, srequest , params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oBatchHelper = helper.CreateObject('BatchHelper')
  oBatch = oBatchHelper.GetBatchUser(request['ActualDate'])

  config.BeginTransaction()
  try:
    oHistory = helper.CreatePObject('TransHistoryOfChanges')
    oHistory.ChangeType = 'I'

    #oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('SD001')
    
    PaymentType = request[u'PaymentType']
    FileKwitansi = ExecFunction(PaymentType, helper, oTran, oBatch, request, params)
      
    # Check for auto approval
    corporate = helper.CreateObject('Corporate')
    if corporate.CheckLimitOtorisasi(request[u'Amount'] * request[u'Rate']):
      oTran.AutoApproval()
    
    oHistory.TransactionNo = oTran.TransactionNo

    config.Commit()
  except:
    config.Rollback()
    raise
  
  status, msg = oTran.CreateJournal()
  return GenerateResponse(status, msg, oTran.TransactionNo, FileKwitansi)

def CollectionUpdate(config, srequest , params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  oBatchHelper = helper.CreateObject('BatchHelper')
  oBatch = oBatchHelper.GetBatchUser(request['ActualDate'])

  oTran = helper.GetObjectByNames(
      'Transaction', {'TransactionNo': request[u'TransactionNo'] }
    )
  
  #oTran.DeleteJournal()
  status = 0
  msg = ''
  
  config.BeginTransaction()
  try:
    oHistory = helper.CreatePObject('TransHistoryOfChanges')
    oHistory.TransactionNo = oTran.TransactionNo
    oHistory.ChangeType = 'E'

    oTran.CancelTransaction()
    #oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
    
    PaymentType = request[u'PaymentType']
    FileKwitansi = ExecFunction(PaymentType, helper, oTran, oBatch, request, params)

    # Check for auto approval
    oTran.AutoApprovalUpdate()
    oHistory.NewTransactionNo = oTran.TransactionNo

    config.Commit()
  except:
    config.Rollback()
    raise

  status, msg = oTran.CreateJournal()
  return GenerateResponse(status, msg, oTran.TransactionNo, FileKwitansi)
  
def BranchCashCollection(helper, oTran, oBatch, request, params):
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
  
  # Get Sponsor & volunteer
  oSponsor = helper.GetObject('Sponsor', request[u'SponsorId'])
  oVolunteer = helper.GetObject('Volunteer', str(request[u'VolunteerId']))
  oDonor = GetDataDonor(helper, request[u'DonorId'])
  
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
        
  # oListBranchCash = {}
  totalAmount = 0.0
  items = request[u'Items']
  for item in items:

    # Create Item for ProductAccount
    aAccountNo = item[u'AccountNo']
    oProductAccount = helper.GetObjectByNames('ProductAccount', {'AccountNo':aAccountNo})
    #oProductAccount = helper.GetObject('ProductAccount', aAccountNo)
    if oProductAccount.isnull:
      raise 'Collection', 'Rekening produk %s tidak ditemukan' % (aAccountNo)

    oItemPA = oTran.CreateDonorTransactionItem(oProductAccount, request[u'DonorId'])
    oItemPA.SetMutation(item[u'Amount'], aRate)
    oItemPA.Description = item[u'Description']

    FundEntity = item[u'FundEntity']
    PercentageOfAmil = item[u'PercentageOfAmil']
    if PercentageOfAmil <= 0.0 :
      JournalCode ='10'
    else:
      JournalCode = dictJournalCode[FundEntity]
    # end if
    oItemPA.SetJournalParameter(JournalCode)

    oItemPA.SetCollectionEntity(FundEntity)
    oItemPA.PercentageOfAmil = PercentageOfAmil

    if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)
    if not oVolunteer.isnull: oVolunteer.AddTransaction(oItemPA)
    if oDonor.IsSponsor() : oDonor.AddTransaction(oItemPA)

    totalAmount += item[u'Amount']
  #-- for
  oTran.Amount = totalAmount
  
  oItemBC = oTran.CreateAccountTransactionItem(oBranchCash)
  oItemBC.SetMutation('D', totalAmount, aRate)
  oItemBC.Description = request[u'Description']
  oItemBC.SetJournalParameter('10')
  
  # Generate TransactionNo
  oTran.GenerateTransactionNumber(oBranchCash.CashCode)
  
  oTran.SaveInbox(params)
  
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi

def BankCollection(helper, oTran, oBatch, request, params):

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
  
  # Get Sponsor & volunteer
  oSponsor = helper.GetObject('Sponsor', request[u'SponsorId'])
  oVolunteer = helper.GetObject('Volunteer', str(request[u'VolunteerId']))
  oDonor = GetDataDonor(helper, request[u'DonorId'])
  
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
    #oProductAccount = helper.GetObject('ProductAccount', aAccountNo)
    oProductAccount = helper.GetObjectByNames('ProductAccount', {'AccountNo':aAccountNo})
    if oProductAccount.isnull:
      raise 'Collection', 'Rekening produk %s tidak ditemukan' % (aAccountNo)

    oItemPA = oTran.CreateDonorTransactionItem(oProductAccount, request[u'DonorId'])
    oItemPA.SetMutation(item[u'Amount'], aRate)
    oItemPA.Description = item[u'Description']

    FundEntity = item[u'FundEntity']
    PercentageOfAmil = item[u'PercentageOfAmil']
    if PercentageOfAmil <= 0.0 :
      JournalCode ='10'
    else:
      JournalCode = dictJournalCode[FundEntity]
    # end if
    oItemPA.SetJournalParameter(JournalCode)

    oItemPA.SetCollectionEntity(FundEntity)
    oItemPA.PercentageOfAmil = PercentageOfAmil

    if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)
    if not oVolunteer.isnull: oVolunteer.AddTransaction(oItemPA)
    if oDonor.IsSponsor() : oDonor.AddTransaction(oItemPA)

    totalAmount += item[u'Amount']
  #-- for
  oTran.Amount = totalAmount
  
  oItemBA = oTran.CreateAccountTransactionItem(oBankAccount)
  oItemBA.SetMutation('D', totalAmount, aRate)
  oItemBA.Description = request[u'Description']
  oItemBA.SetJournalParameter('10')
  
  oTran.SaveInbox(params)
  
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi 

def AssetCollection(helper, oTran, oBatch, request, params):  
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
  
  # Get Sponsor & volunteer
  oSponsor = helper.GetObject('Sponsor', request[u'SponsorId'])
  oVolunteer = helper.GetObject('Volunteer', str(request[u'VolunteerId']))
  oDonor = GetDataDonor(helper, request[u'DonorId'])

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
    oProductAccount = helper.GetObjectByNames('ProductAccount', {'AccountNo':aAccountNo})
    #oProductAccount = helper.GetObject('ProductAccount', aAccountNo)
    if oProductAccount.isnull:
      raise 'Collection', 'Rekening produk %s tidak ditemukan' % (aAccountNo)

    oItemPA = oTran.CreateDonorTransactionItem(oProductAccount, request[u'DonorId'])
    oItemPA.SetMutation(item[u'Amount'], aRate)
    oItemPA.Description = item[u'Description']
    
    FundEntity = item[u'FundEntity']
    PercentageOfAmil = item[u'PercentageOfAmil']
    if PercentageOfAmil <= 0.0 :
      JournalCode ='10'
    else:
      JournalCode = dictJournalCode[FundEntity]
    # end if
    oItemPA.SetJournalParameter(JournalCode)

    oItemPA.SetCollectionEntity(FundEntity)
    oItemPA.PercentageOfAmil = PercentageOfAmil

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
  oItemGL.SetJournalParameter('10')

  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()

  return FileKwitansi

def PettyCashCollection(helper, oTran, oBatch, request, params):
  aInputer = request[u'Inputer']
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
  oTran.ChannelCode = 'P'

  # Get Sponsor & volunteer
  oSponsor = helper.GetObject('Sponsor', request[u'SponsorId'])
  oVolunteer = helper.GetObject('Volunteer', str(request[u'VolunteerId']))
  oDonor = GetDataDonor(helper, request[u'DonorId'])

  # Set Information
  oTran.SponsorId = request[u'SponsorId']
  oTran.VolunteerId = request[u'VolunteerId']
  oTran.DonorId = request[u'DonorId']
  oTran.ActualDate = request[u'ActualDate']
  oTran.PaidTo = request[u'PaidTo']
  
  PettyCashAccountNo = str(request[u'PettyCashAccountNo'])
  oPettyCash = helper.GetObject('PettyCash', PettyCashAccountNo)
  if oPettyCash.isnull:
    raise 'Collection', 'Rekening kas kecil dengan kode %s tidak ditemukan' % ( PettyCashAccountNo)
  
  totalAmount = 0.0
  items = request[u'Items']
  for item in items:
    # Create Item for ProductAccount      
    aAccountNo = item[u'AccountNo']
    aProductId = item[u'ProductId']
    oProductAccount = helper.GetObjectByNames('ProductAccount', {'AccountNo':aAccountNo})
    if oProductAccount.isnull:
      raise 'Collection', 'Rekening produk %s tidak ditemukan' % (aAccountNo)

    oItemPA = oTran.CreateDonorTransactionItem(oProductAccount, request[u'DonorId'])
    oItemPA.SetMutation(item[u'Amount'], aRate)
    oItemPA.Description = item[u'Description']
    
    FundEntity = item[u'FundEntity']
    PercentageOfAmil = item[u'PercentageOfAmil']
    if PercentageOfAmil <= 0.0 :
      JournalCode ='10'
    else:
      JournalCode = dictJournalCode[FundEntity]
    # end if
    oItemPA.SetJournalParameter(JournalCode)

    oItemPA.SetCollectionEntity(FundEntity)
    oItemPA.PercentageOfAmil = PercentageOfAmil

    if not oSponsor.isnull  : oSponsor.AddTransaction(oItemPA)        
    if not oVolunteer.isnull: oVolunteer.AddTransaction(oItemPA)      
    if oDonor.IsSponsor() : oDonor.AddTransaction(oItemPA)
    
    totalAmount += item[u'Amount']
      
  #-- for
  oTran.Amount = totalAmount
  
  oItemPC = oTran.CreateAccountTransactionItem(oPettyCash)
  oItemPC.SetMutation('D', totalAmount, aRate)
  oItemPC.Description = request[u'Description']
  oItemPC.SetJournalParameter('10')
  
  oTran.GenerateTransactionNumber(oPettyCash.CashCode)
  oTran.SaveInbox(params)

  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi