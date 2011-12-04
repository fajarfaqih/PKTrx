# Collection.py
import simplejson
import com.ihsan.foundation.pobjecthelper as phelper

def GenerateResponse(Status,ErrMessage,TransactionNo,FileKwitansi):
  response = {}
  response['Status'] = Status
  response['TransactionNo'] = TransactionNo
  response['ErrMessage'] = ErrMessage
  response['FileKwitansi'] = FileKwitansi
  
  return simplejson.dumps(response)

def GetBatch(helper,ActualDate):
  oBatchHelper = helper.CreateObject('BatchHelper')
  oBatch = oBatchHelper.GetBatchUser(ActualDate)
  return oBatch

def CashOutNew(config,srequest,params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)
  
  oBatch = GetBatch(helper,request['ActualDate'])
  
  config.BeginTransaction()
  try:
    oTran = oBatch.NewTransaction('CO')
    
    if request[u'PaymentType'] == 'K' : 
      FileKwitansi = PettyCash(helper,oTran,oBatch,request,params)
    elif request[u'PaymentType'] == 'C' : 
      FileKwitansi = BranchCash(helper,oTran,oBatch,request,params)
    elif request[u'PaymentType'] == 'B' :  
      FileKwitansi = Bank(helper,oTran,oBatch,request,params)
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

def CashOutUpdate(config, srequest, params):
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
    oTran.CancelTransaction()
    oTran.BatchId = oBatch.BatchId

    if request[u'PaymentType'] == 'K' : 
      FileKwitansi = PettyCash(helper,oTr,oBatch,request,params)
    elif request[u'PaymentType'] == 'C' :
      FileKwitansi = BranchCash(helper,oTran,oBatch,request,params)
    elif request[u'PaymentType'] == 'B' :  
      FileKwitansi = Bank(helper,oTran,oBatch,request,params)
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

def PettyCash(helper,oTran,oBatch,request,params):
  aInputer    = request[u'Inputer']
  aBranchCode = request[u'BranchCode']
   
  oTran.Inputer     = aInputer
  oTran.BranchCode  = aBranchCode
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.ChannelCode = 'P'
  oTran.PaidTo = request[u'PaidTo'] 
  oTran.CurrencyCode = '000'
  oTran.Rate = 1
  oTran.ReceivedFrom = request[u'ReceivedFrom']    
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
      
  aJournalCode = '10'
  aJournalCodeDebit = '10'
  
  totalAmount = 0.0
  oListPettyCash = {}
  items = request[u'Items']
  for item in items:
    aValuta = item[u'Valuta'] 
    AccountCode  = item[u'AccountCode']
    AccountName = item[u'AccountName']
    aAmount = item[u'Amount']
    aRate = item[u'Rate']
    aDesc = item[u'Description']
    
    oItemGL = oTran.CreateGLTransactionItem(AccountCode, aValuta)
    oItemGL.RefAccountName = AccountName
    oItemGL.GLName = AccountName
    oItemGL.SetMutation('D', aAmount, aRate)
    oItemGL.Description = aDesc
    oItemGL.SetJournalParameter('10')
    
    aBudgetId = item[u'BudgetId'] 
    
    if aBudgetId != 0 :        
      oBudget = helper.GetObject('Budget',aBudgetId)
      oItemGL.CreateBudgetTransaction(oBudget.BudgetId)
    
    # Create Item for PettyCash
    if oListPettyCash.has_key(aValuta):
      oItemPC = oListPettyCash[aValuta]
      oItemPC.AddAmount(item[u'Amount']) 
    else:
      oPettyCash = helper.GetObjectByNames('PettyCash',
        {'UserName': aInputer, 'BranchCode': aBranchCode, 'CurrencyCode': aValuta})
      if oPettyCash.isnull:
        raise 'Cash In', 'Rekening kas kecil %s:%s tidak ditemukan' % (aInputer, aValuta)
      
      oItemPC = oTran.CreateAccountTransactionItem(oPettyCash)
      oItemPC.SetMutation('C', item[u'Amount'], item[u'Rate'])
      oItemPC.Description = item[u'Description']
      oItemPC.SetJournalParameter(aJournalCodeDebit)
      
      oListPettyCash[aValuta] = oItemPC
    #-- if.else
    totalAmount = item[u'Amount']
  #-- for
  oTran.Amount = totalAmount
  
  # Generate TransactionNo
  oTran.GenerateTransactionNumber(oPettyCash.CashCode)
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()
  
  return FileKwitansi

def BranchCash(helper,oTran,oBatch,request,params):
  aInputer    = request[u'Inputer'] 
  aBranchCode = request[u'BranchCode']
  aRate = request[u'RateCash']
  aValuta = request[u'CurrencyCode']
   
  oTran.Inputer     = aInputer
  oTran.BranchCode  = aBranchCode
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.ChannelCode = 'R'
  oTran.PaidTo = request[u'PaidTo']
  oTran.CurrencyCode = aValuta
  oTran.Rate = aRate
  oTran.ReceivedFrom = request[u'ReceivedFrom']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
          
  aJournalCode = '10'
  aJournalCodeDebit = '10'
      
  totalAmount = 0.0
  items = request[u'Items']    
  for item in items:
    AccountCode  = item[u'AccountCode']
    AccountName = item[u'AccountName']
    aAmount = item[u'Amount']
    aDesc = item[u'Description']
    
    oItemGL = oTran.CreateGLTransactionItem(AccountCode, aValuta)
    oItemGL.RefAccountName = AccountName
    oItemGL.GLName = AccountName
    oItemGL.SetMutation('D', aAmount, aRate)
    oItemGL.Description = aDesc
    oItemGL.SetJournalParameter('10')
    
    aBudgetId = item[u'BudgetId'] 
    
    if aBudgetId != 0 :        
      oBudget = helper.GetObject('Budget',aBudgetId)
      oItemGL.CreateBudgetTransaction(oBudget.BudgetId)
    
    totalAmount += item[u'Amount']
  #-- for
  oTran.Amount = totalAmount
  
  oBranchCash = helper.GetObjectByNames('BranchCash',
        {'BranchCode': aBranchCode, 'CurrencyCode': aValuta})
  if oBranchCash.isnull:
        raise 'Cash Out', 'Rekening kas cabang %s:%s tidak ditemukan' % (aBranchCode, aValuta)

  oItemBC = oTran.CreateAccountTransactionItem(oBranchCash)
  oItemBC.SetMutation('C', totalAmount, aRate)
  oItemBC.Description = request[u'Description']
  oItemBC.SetJournalParameter(aJournalCodeDebit)

  # Generate TransactionNo
  oTran.GenerateTransactionNumber(oBranchCash.CashCode)
  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()

  return FileKwitansi
  
  
def Bank(helper,oTran,oBatch,request,params):
  aInputer    = request[u'Inputer'] 
  aBranchCode = request[u'BranchCode']
   
  oTran.Inputer     = aInputer
  oTran.BranchCode  = aBranchCode
  oTran.ReferenceNo = request[u'ReferenceNo']
  oTran.Description = request[u'Description']
  oTran.ChannelCode = 'R'
  oTran.PaidTo = request[u'PaidTo']
  oTran.CurrencyCode = '000'
  oTran.ReceivedFrom = request[u'ReceivedFrom']
  oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
          
  aJournalCode = '10'
  aJournalCodeDebit = '10'
  
  aBankAccountNo = str(request[u'BankAccountNo'])
  
  oBankAccount = helper.GetObject('BankCash', aBankAccountNo)
  if oBankAccount.isnull:
    raise 'Cash In', 'Rekening bank %s tidak ditemukan' % (aBankAccountNo)    
  # end if.else  

  aRate = request[u'Rate']
  aValuta = oBankAccount.CurrencyCode
  oTran.CurrencyCode = aValuta
  oTran.Rate = aRate
      
  # Generate TransactionNo
  oTran.GenerateTransactionNumber(oBankAccount.CashCode)
      
  totalAmount = 0.0
  items = request[u'Items']
  for item in items:
    aValuta = item[u'Valuta'] 
    AccountCode  = item[u'AccountCode']
    AccountName = item[u'AccountName']
    aAmount = item[u'Amount']
    aRate = item[u'Rate']
    aDesc = item[u'Description']
    
    oItemGL = oTran.CreateGLTransactionItem(AccountCode, aValuta)
    oItemGL.RefAccountName = AccountName
    oItemGL.GLName = AccountName
    oItemGL.SetMutation('D', aAmount, aRate)
    oItemGL.Description = aDesc
    oItemGL.SetJournalParameter('10')
    
    aBudgetId = item[u'BudgetId'] 
    
    if aBudgetId != 0 :        
      oBudget = helper.GetObject('Budget',aBudgetId)
      oItemGL.CreateBudgetTransaction(oBudget.BudgetId)

    totalAmount += aAmount
  #-- for
  oTran.Amount = totalAmount

  oItemBA = oTran.CreateAccountTransactionItem(oBankAccount)
  oItemBA.SetMutation('C', totalAmount, aRate)
  oItemBA.Description = item[u'Description']
  oItemBA.SetJournalParameter(aJournalCodeDebit)

  oTran.SaveInbox(params)
  FileKwitansi = oTran.GetKwitansi()

  return FileKwitansi
