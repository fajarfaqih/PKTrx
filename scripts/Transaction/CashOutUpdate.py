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

def PettyCashIn(config, srequest ,params):
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
    aInputer    = request[u'Inputer']
    aBranchCode = request[u'BranchCode']
     
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
        
    oTran.Inputer     = aInputer
    oTran.BranchCode  = aBranchCode
    oTran.ReferenceNo = request[u'ReferenceNo']
    oTran.Description = request[u'Description']
    oTran.ChannelCode = 'P'
    oTran.PaidTo = request[u'PaidTo'] 
    oTran.CurrencyCode = '000'
    oTran.ReceivedFrom = request[u'ReceivedFrom']
    oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate') 
    
    #aProductBranchCode = request[u'ProductBranchCode']
    #if aProductBranchCode != aBranchCode:
    #  aJournalCode = 'C15'
    #  aJournalCodeDebit = '15'      
    #else:
    #  aJournalCode = 'C10'
    #  aJournalCodeDebit = '10'      
    #-- if.else
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
    
    oTran.AutoApprovalUpdate()
      
    config.Commit()
  except:
    config.Rollback()
    raise
   
  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)

def BranchCashIn(config, srequest ,params):
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
    aInputer    = request[u'Inputer'] 
    aBranchCode = request[u'BranchCode']
     
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
            
    oTran.Inputer     = aInputer
    oTran.BranchCode  = aBranchCode
    oTran.ReferenceNo = request[u'ReferenceNo']
    oTran.Description = request[u'Description']
    oTran.ChannelCode = 'R'
    oTran.PaidTo = request[u'PaidTo']
    oTran.CurrencyCode = '000'
    oTran.ReceivedFrom = request[u'ReceivedFrom']
    oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
            
#     if aProductBranchCode != aBranchCode:
#       aJournalCode = 'C15'
#       aJournalCodeDebit = '15'      
#     else:
#       aJournalCode = 'C10'
#       aJournalCodeDebit = '10'
#     #-- if.else
    aJournalCode = '10'
    aJournalCodeDebit = '10'
        
    totalAmount = 0.0
    oListBranchCash = {}
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
      
      # Create Item for BranchCash
      if oListBranchCash.has_key(aValuta):
        oItemBC = oListBranchCash[aValuta]
        oItemBC.AddAmount(item[u'Amount'])
         
      else:        
        oBranchCash = helper.GetObjectByNames('BranchCash',
          {'BranchCode': aBranchCode, 'CurrencyCode': aValuta})
        if oBranchCash.isnull:
          raise 'Cash In', 'Rekening kas cabang %s:%s tidak ditemukan' % (aBranchCode, aValuta)
        
        oItemBC = oTran.CreateAccountTransactionItem(oBranchCash)
        oItemBC.SetMutation('C', item[u'Amount'], item[u'Rate'])
        oItemBC.Description = item[u'Description']
        oItemBC.SetJournalParameter(aJournalCodeDebit)
        
        oListBranchCash[aValuta] = oItemBC        
      #-- if.else
      totalAmount += item[u'Amount']  
    #-- for
    oTran.Amount = totalAmount
    
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
  
def BankIn(config, srequest ,params):
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
    aInputer    = request[u'Inputer'] 
    aBranchCode = request[u'BranchCode']
     
    oTran.CancelTransaction()
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran.BatchId = oBatch.BatchId
        
    oTran.Inputer     = aInputer
    oTran.BranchCode  = aBranchCode
    oTran.ReferenceNo = request[u'ReferenceNo']
    oTran.Description = request[u'Description']
    oTran.ChannelCode = 'R'
    oTran.PaidTo = request[u'PaidTo']
    oTran.CurrencyCode = '000'
    oTran.ReceivedFrom = request[u'ReceivedFrom']
    oTran.ActualDate = oBatch.GetAsTDateTime('BatchDate')
            
#     aProductBranchCode = request[u'ProductBranchCode']
#     if aProductBranchCode != aBranchCode:
#       aJournalCode = 'C15'
#       aJournalCodeDebit = '15'            
#     else:
#       aJournalCode = 'C10'
#       aJournalCodeDebit = '10'      
#     #-- if.else
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
      #-- if.else
      totalAmount += aAmount      
    #-- for
    oTran.Amount = totalAmount
    
    oItemBA = oTran.CreateAccountTransactionItem(oBankAccount)
    oItemBA.SetMutation('C', totalAmount, aRate)
    oItemBA.Description = item[u'Description']
    oItemBA.SetJournalParameter(aJournalCodeDebit)

    oTran.SaveInbox(params)
    FileKwitansi = oTran.GetKwitansi()
    
    oTran.AutoApprovalUpdate()
      
    config.Commit()
  except:
    config.Rollback()
    raise
  
  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
