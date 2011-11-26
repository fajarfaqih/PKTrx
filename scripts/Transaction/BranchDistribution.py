# GeneralTransaction.py
import simplejson
import com.ihsan.foundation.pobjecthelper as phelper

status = 0
msg = ''
FileKwitansi = ''

def BranchDistributionNew(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('DT')

    FileKwitansi = BranchDistribution(helper,oTran,oBatch,request,params)
     
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

def BranchDistributionUpdate(config, srequest, params):
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
    oTran.TransactionCode = 'DT'

    FileKwitansi = BranchDistribution(helper,oTran,oBatch,request,params)

    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
  
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
  oDCashAccount = helper.GetObject('BranchCash',
       aDestAccountNo).CastToLowestDescendant()
  if oDCashAccount.isnull:
    raise 'Cash/Bank', 'Kas Tujuan tidak ditemukan'
  
  oItemDCA = oTran.CreateAccountTransactionItem(oDCashAccount)
  oItemDCA.SetMutation('D', request[u'Amount'], 1.0)    
  oItemDCA.Description = request[u'Description']
  oItemDCA.SetJournalParameter('15')
  
  oTran.GenerateTransactionNumber(oSCashAccount.CashCode)
  oTran.SaveInbox(params)

  oTransferInfo = helper.GetObjectByNames('DistributionTransferInfo',{'TransactionId' : oTran.TransactionId}) 
  
  if oTransferInfo.isnull: 
    oTransferInfo = helper.CreatePObject('DistributionTransferInfo')
    oTransferInfo.TransactionId = oTran.TransactionId
    #oTransferInfo.TransactionItemId = oItemCA.TransactionItemId
    oTransferInfo.CashAccountNoDest = aDestAccountNo
    oTransferInfo.CashAccountNoSource = aSourceAccountNo

  oTransferInfo.AccountNo = request[u'AccountNo']
  oTransferInfo.BranchSource = aBranchCode
  oTransferInfo.BranchDestination = aDestBranchCode
    
  return oTran.GetKwitansi()
  
def BranchDistributionReturnNew(config, srequest, params):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    oBatch = helper.GetObject('TransactionBatch', request[u'BatchId'])
    oTran = oBatch.NewTransaction('DTR')

    FileKwitansi = BranchDistributionReturn(helper, oTran, oBatch, request, params)

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
  
def BranchDistributionReturnUpdate(config, srequest, params):
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
    oTran.TransactionCode = 'DTR'

    FileKwitansi = BranchDistributionReturn(helper, oTran, oBatch, request, params)

    # Check for auto approval
    oTran.AutoApprovalUpdate()

    config.Commit()
  except:
    config.Rollback()
    raise

  status,msg = oTran.CreateJournal()      
  return GenerateResponse(status,msg,oTran.TransactionNo,FileKwitansi)
     
def BranchDistributionReturn(helper,oTran,oBatch,request,params):

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
  
def GenerateResponse(Status,ErrMessage,TransactionNo,FileKwitansi):
  response = {}
  response['Status'] = Status
  response['TransactionNo'] = TransactionNo
  response['ErrMessage'] = ErrMessage
  response['FileKwitansi'] = FileKwitansi
  
  return simplejson.dumps(response)
