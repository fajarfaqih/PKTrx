# GeneralTransaction.py
import simplejson
import com.ihsan.foundation.pobjecthelper as phelper
import sys

status = 0
msg = ''
FileKwitansi = ''

def GetBatch(helper):
  config = helper.Config
  
  BranchCode = config.SecurityContext.GetUserInfo()[4]
  BatchNo = 'SYS-BALANCE-%s' % BranchCode
  
  oBatch = helper.GetObjectByNames(
       'TransactionBatch', 
         {'BatchNo' : BatchNo,
          'BranchCode' : BranchCode,
         })
  if oBatch.isnull:
    oBatch = helper.CreatePObject('TransactionBatch')
    oBatch.BatchNo = BatchNo
    oBatch.BranchCode = BranchCode 
    oBatch.BatchDate = config.ModLibUtils.EncodeDate(2010,12,31)
    oBatch.Inputer = config.SecurityContext.InitUser
    oBatch.Description = 'Saldo Awal'
    oBatch.IsPosted = 'T'     
    oBatch.BatchTag = 'SYS'
  # end if
    
  return oBatch

def GetTransaction(helper,oBatch,AccountCode,Description):   
  config = helper.Config     
  BranchCode = config.SecurityContext.GetUserInfo()[4]
  TransactionNo = '%s-%s' % (AccountCode,BranchCode)
  
  oTran = helper.GetObjectByNames(
       'Transaction', 
        {'BatchId' : oBatch.BatchId,
         'TransactionCode' : 'TB',
         'TransactionNo' : TransactionNo,
         'BranchCode' : BranchCode,
        }
       )
  if oTran.isnull:
    oTran = oBatch.NewTransaction('TB')
    oTran.Inputer     = config.SecurityContext.InitUser
    oTran.BranchCode  = BranchCode
    oTran.ReferenceNo = AccountCode
    oTran.Description = Description
    oTran.TransactionDate  = config.ModLibUtils.EncodeDate(2010,12,31)
    oTran.ActualDate  = config.ModLibUtils.EncodeDate(2010,12,31)
    oTran.IsPosted = 'T'
    oTran.TransactionNo = TransactionNo 
  # end if  
  
  return oTran  
    
      
def CashAccount(config,params):
  app = config.AppObject  
  app.ConCreate('TB')
  helper = phelper.PObjectHelper(config)
  
  status = 0
  err_message = ''
  config.BeginTransaction()
  try:
    app.ConWriteln('Get Batch','TB')
    oBatch = GetBatch(helper)
    app.ConWriteln('Get Transaction','TB')
    oTran = GetTransaction(helper,oBatch,'BB-CB','Saldo Awal Kas')
    
    BalanceData = params.BalanceData
    TotalAmount = 0.0
    TotalData = BalanceData.RecordCount
    for i in range(TotalData):
      recBalance = BalanceData.GetRecord(i)
      app.ConWriteln('Proses data ke-%s , %s' %(str(i+1),recBalance.AccountName),'TB')     
      
      AccountNo = recBalance.AccountNo
      oAccount = helper.GetObjectByNames('CashAccount',{'AccountNo':AccountNo})
      if oAccount.isnull:
        raise 'PERINGATAN','Rekening produk %s tidak dapat ditemukan' % (AccountNo)
        
      oItem = helper.GetObjectByNames('AccountTransactionItem',
          {'TransactionId' : oTran.TransactionId,
           'AccountNo' : recBalance.AccountNo
          }
        )
      if oItem.isnull :
        oItem = oTran.CreateAccountTransactionItem(oAccount)
      else:
        oItem.CancelTransaction()      
      BeginningBalance = recBalance.Balance or 0.0
      
      oItem.SetMutation('D', BeginningBalance, 1.0)
      oItem.Description = 'Saldo Awal'
      oItem.SetJournalParameter('10')
            
      TotalAmount += BeginningBalance
    # end for
    
    oTran.Amount = TotalAmount
    
    app.ConWriteln('Proses approval data ','TB')
    oTran.AuthStatus = 'F'
    oTran.AutoApproval()
      
    config.Commit() 
  except:
    config.Rollback()
    status = 1
    err_message = str(sys.exc_info()[1])
  
  return status,err_message  
  
def Program(config,params):
  app = config.AppObject  
  app.ConCreate('TB')
  helper = phelper.PObjectHelper(config)
  
  status = 0
  err_message = ''
  config.BeginTransaction()
  try:
    app.ConWriteln('Get Batch','TB')
    oBatch = GetBatch(helper)
    app.ConWriteln('Get Transaction','TB')
    oTran = GetTransaction(helper,oBatch,'BB-PROG','Saldo Awal Program')
    
    BalanceData = params.BalanceData
    TotalAmount = 0.0
    TotalData = BalanceData.RecordCount
    for i in range(TotalData):
      recBalance = BalanceData.GetRecord(i)
      app.ConWriteln('Proses data ke-%s , %s' %(str(i+1),recBalance.AccountName),'TB')     
      
      AccountNo = recBalance.AccountNo
      oAccount = helper.GetObjectByNames('ProductAccount',{'AccountNo':AccountNo})
      if oAccount.isnull:
        raise 'PERINGATAN','Rekening produk %s tidak dapat ditemukan' % (AccountNo)
        
      oItem = helper.GetObjectByNames('AccountTransactionItem',
          {'TransactionId' : oTran.TransactionId,
           'AccountNo' : recBalance.AccountNo
          }
        )
      if oItem.isnull :
        oItem = oTran.CreateAccountTransactionItem(oAccount)
      else:
        oItem.CancelTransaction()      
      BeginningBalance = recBalance.Balance or 0.0
      
      oItem.SetMutation('C', BeginningBalance, 1.0)
      oItem.Description = 'Saldo Awal'
      oItem.SetJournalParameter('10')
            
      TotalAmount += BeginningBalance
    # end for
    
    oTran.Amount = TotalAmount
    
    app.ConWriteln('Proses approval data ','TB')
    oTran.AuthStatus = 'F'
    oTran.AutoApproval()
      
    config.Commit() 
  except:
    config.Rollback()
    status = 1
    err_message = str(sys.exc_info()[1])
  
  return status,err_message  

def Project(config,params):
  app = config.AppObject  
  app.ConCreate('TB')
  helper = phelper.PObjectHelper(config)
  
  status = 0
  err_message = ''
  config.BeginTransaction()
  try:
    app.ConWriteln('Get Batch','TB')
    oBatch = GetBatch(helper)
    app.ConWriteln('Get Transaction','TB')
    oTran = GetTransaction(helper,oBatch,'BB-PROJ','Saldo Awal Project' )
    
    BalanceData = params.BalanceData
    TotalAmount = 0.0
    TotalData = BalanceData.RecordCount
    for i in range(TotalData):
      recBalance = BalanceData.GetRecord(i)
      app.ConWriteln('Proses data ke-%s , %s' %(str(i+1),recBalance.AccountName),'TB')     
      
      AccountNo = recBalance.AccountNo
      oAccount = helper.GetObjectByNames('ProjectAccount',{'AccountNo':AccountNo})
      if oAccount.isnull:
        raise 'PERINGATAN','Rekening produk %s tidak dapat ditemukan' % (AccountNo)
        
      oDonor = helper.CreateObject('ExtDonor')
      oDonor.GetData(recBalance.SponsorId)
        
      oItem = helper.GetObjectByNames('DonorTransactionItem',
          {'TransactionId' : oTran.TransactionId,
           'AccountNo' : recBalance.AccountNo
          }
        )
      if oItem.isnull :
        oItem = oTran.CreateDonorTransactionItem(oAccount,recBalance.SponsorId)
      else:
        oItem.CancelTransaction()      
      BeginningBalance = recBalance.Balance or 0.0
      oItem.SetMutation(BeginningBalance, 1.0)
      oItem.Description = 'Saldo Awal Project %s' % recBalance.AccountName[:50]
      oItem.SetJournalParameter('10')      
      oDonor.AddTransaction(oItem)
            
      TotalAmount += BeginningBalance
    # end for
    
    oTran.Amount = TotalAmount
    
    app.ConWriteln('Proses approval data ','TB')
    oTran.AuthStatus = 'F'
    oTran.AutoApproval()
      
    config.Commit() 
  except:
    config.Rollback()
    status = 1
    err_message = str(sys.exc_info()[1])
  
  return status,err_message  
  
def EmployeeAR(config,params):
  app = config.AppObject  
  app.ConCreate('TB')
  helper = phelper.PObjectHelper(config)
  
  status = 0
  err_message = ''
  config.BeginTransaction()
  try:
    app.ConWriteln('Get Batch','TB')
    oBatch = GetBatch(helper)
    app.ConWriteln('Get Transaction','TB')
    oTran = GetTransaction(helper,oBatch,'BB-EMP','Saldo Awal Piutang')
    
    aBranchCode = config.SecurityContext.GetUserInfo()[4]
    
    
    BalanceData = params.BalanceData
    TotalAmount = 0.0
    TotalData = BalanceData.RecordCount
    for i in range(TotalData):
      recBalance = BalanceData.GetRecord(i)
      app.ConWriteln('Proses data ke-%s , %s' %(str(i+1),recBalance.AccountName),'TB')     
      
      EmployeeId = recBalance.AccountNo
      oAccount = helper.GetObjectByNames('EmployeeAccountReceivable',{'EmployeeIdNumber':EmployeeId})
      if oAccount.isnull:
        oAccount = helper.CreatePObject('EmployeeAccountReceivable', EmployeeId)
        oAccount.BranchCode = aBranchCode
        oAccount.CurrencyCode = '000'
        oAccount.AccountName  = recBalance.AccountName
        
      oItem = helper.GetObjectByNames('AccountTransactionItem',
          {'TransactionId' : oTran.TransactionId,
           'AccountNo' : oAccount.AccountNo
          }
        )
      if oItem.isnull :
        oItem = oTran.CreateAccountTransactionItem(oAccount)
      else:
        oItem.CancelTransaction()
      BeginningBalance = recBalance.Balance or 0.0
      
      oItem.SetMutation('D', BeginningBalance, 1.0)
      oItem.Description = 'Saldo Awal'
      oItem.SetJournalParameter('10')
            
      TotalAmount += BeginningBalance
    # end for
    
    oTran.Amount = TotalAmount
    
    app.ConWriteln('Proses approval data ','TB')
    oTran.AuthStatus = 'F'
    #-----------
    aSQLText = " select transactionitemid from transactionitem \
                     where transactionid=%d " % oTran.TransactionId        

    oRes = config.CreateSQL(aSQLText).RawResult
    
    while not oRes.Eof:
      oItem = helper.GetObject(
           'TransactionItem',oRes.transactionitemid
      ).CastToLowestDescendant()
      app.ConWriteln('Proses item account %s' % oItem.AccountNo,'TB')
      oItem.SetApproval()

      #oItems.Next()
      oRes.Next()
    #-- while
    #----------
    oTran.AutoApproval()
      
    config.Commit() 
  except:
    config.Rollback()
    status = 1
    err_message = str(sys.exc_info()[1])
  
  return status,err_message

def ExternalAR(config,params):
  app = config.AppObject  
  app.ConCreate('TB')
  helper = phelper.PObjectHelper(config)
  
  status = 0
  err_message = ''
  config.BeginTransaction()
  try:
    app.ConWriteln('Get Batch','TB')
    oBatch = GetBatch(helper)
    app.ConWriteln('Get Transaction','TB')
    oTran = GetTransaction(helper,oBatch,'BB-EXT','Saldo Awal Piutang Eksternal')
    
    aBranchCode = config.SecurityContext.GetUserInfo()[4]
        
    BalanceData = params.BalanceData
    TotalAmount = 0.0
    TotalData = BalanceData.RecordCount
    for i in range(TotalData):
      recBalance = BalanceData.GetRecord(i)
      app.ConWriteln('Proses data ke-%s , %s' %(str(i+1),recBalance.AccountName),'TB')     
      
      DebtorId = recBalance.AccountNo
      oAccount = helper.GetObjectByNames('ExternalAccountReceivable',{'DebtorId':DebtorId})
      if oAccount.isnull:
        oAccount = helper.CreatePObject('ExternalAccountReceivable', DebtorId)
        oAccount.BranchCode = aBranchCode
        oAccount.CurrencyCode = '000'
        oAccount.AccountName  = recBalance.AccountName
        
      oItem = helper.GetObjectByNames('AccountTransactionItem',
          {'TransactionId' : oTran.TransactionId,
           'AccountNo' : oAccount.AccountNo
          }
        )
      if oItem.isnull :
        oItem = oTran.CreateAccountTransactionItem(oAccount)
      else:
        oItem.CancelTransaction()
      BeginningBalance = recBalance.Balance or 0.0
      
      oItem.SetMutation('D', BeginningBalance, 1.0)
      oItem.Description = 'Saldo Awal'
      oItem.SetJournalParameter('10')
            
      TotalAmount += BeginningBalance
    # end for
    
    oTran.Amount = TotalAmount
    
    app.ConWriteln('Proses approval data ','TB')
    oTran.AuthStatus = 'F'
    #-----------
    aSQLText = " select transactionitemid from transactionitem \
                     where transactionid=%d " % oTran.TransactionId        

    oRes = config.CreateSQL(aSQLText).RawResult
    
    while not oRes.Eof:
      oItem = helper.GetObject(
           'TransactionItem',oRes.transactionitemid
      ).CastToLowestDescendant()
      app.ConWriteln('Proses item account %s' % oItem.AccountNo,'TB')
      oItem.SetApproval()

      #oItems.Next()
      oRes.Next()
    #-- while
    #----------
    oTran.AutoApproval()
      
    config.Commit() 
  except:
    config.Rollback()
    status = 1
    err_message = str(sys.exc_info()[1])
  
  return status,err_message

def EmployeeInvestment(config,params):
  app = config.AppObject  
  app.ConCreate('TB')
  helper = phelper.PObjectHelper(config)
  
  status = 0
  err_message = ''
  config.BeginTransaction()
  try:
    app.ConWriteln('Get Batch','TB')
    oBatch = GetBatch(helper)
    app.ConWriteln('Get Transaction','TB')
    oTran = GetTransaction(helper,oBatch,'BB-EMPINVS','Saldo Awal Investasi Karyawan')
    
    aBranchCode = config.SecurityContext.GetUserInfo()[4]
        
    BalanceData = params.BalanceData
    TotalAmount = 0.0
    TotalData = BalanceData.RecordCount
    for i in range(TotalData):
      recBalance = BalanceData.GetRecord(i)
      app.ConWriteln('Proses data ke-%s , %s' %(str(i+1),recBalance.AccountName),'TB')     
      
      EmployeeId = recBalance.AccountNo
      oAccount = helper.GetObjectByNames('InvestmentEmployee',{'EmployeeId':EmployeeId})
      if oAccount.isnull:
        oAccount = helper.CreatePObject('InvestmentEmployee', EmployeeId)
        oAccount.BranchCode = aBranchCode
        oAccount.CurrencyCode = '000'
      # end if  
      oAccount.AccountName  = recBalance.AccountName
      oAccount.FundEntity = 4
      oAccount.InvestmentAmount = recBalance.InvestAmount
      oAccount.SetLifeTime(recBalance.LifeTime)
      oAccount.InvestmentCatId = 3
      oAccount.StartDate = recBalance.StartDate
      oAccount.InvestmentNisbah = recBalance.Nisbah        
        
      oItem = helper.GetObjectByNames('AccountTransactionItem',
          {'TransactionId' : oTran.TransactionId,
           'AccountNo' : oAccount.AccountNo
          }
        )
      if oItem.isnull :
        oItem = oTran.CreateAccountTransactionItem(oAccount)
      else:
        oItem.CancelTransaction()
      BeginningBalance = recBalance.Balance or 0.0
      
      oItem.SetMutation('D', BeginningBalance, 1.0)
      oItem.Description = 'Saldo Awal'
      oItem.SetJournalParameter('10')
            
      TotalAmount += BeginningBalance
    # end for
    
    oTran.Amount = TotalAmount
    
    app.ConWriteln('Proses approval data ','TB')
    oTran.AuthStatus = 'F'
    #-----------
    aSQLText = " select transactionitemid from transactionitem \
                     where transactionid=%d " % oTran.TransactionId        

    oRes = config.CreateSQL(aSQLText).RawResult
    
    while not oRes.Eof:
      oItem = helper.GetObject(
           'TransactionItem',oRes.transactionitemid
      ).CastToLowestDescendant()
      app.ConWriteln('Proses item account %s' % oItem.AccountNo,'TB')
      oItem.SetApproval()

      #oItems.Next()
      oRes.Next()
    #-- while
    #----------
    oTran.AutoApproval()
      
    config.Commit() 
  except:
    config.Rollback()
    status = 1
    err_message = str(sys.exc_info()[1])
  
  return status,err_message


def ExternalInvestment(config,params):
  app = config.AppObject  
  app.ConCreate('TB')
  helper = phelper.PObjectHelper(config)
  
  status = 0
  err_message = ''
  config.BeginTransaction()
  try:
    app.ConWriteln('Get Batch','TB')
    oBatch = GetBatch(helper)
    app.ConWriteln('Get Transaction','TB')
    oTran = GetTransaction(helper,oBatch,'BB-EXTINVS','Saldo Awal Investasi Non Karyawan')
    
    aBranchCode = config.SecurityContext.GetUserInfo()[4]
        
    BalanceData = params.BalanceData
    TotalAmount = 0.0
    TotalData = BalanceData.RecordCount
    for i in range(TotalData):
      recBalance = BalanceData.GetRecord(i)
      app.ConWriteln('Proses data ke-%s , %s' %(str(i+1),recBalance.AccountName),'TB')     
      
      InvesteeId = recBalance.AccountNo
      oAccount = helper.GetObjectByNames('InvestmentNonEmployee',{'InvesteeId':InvesteeId})
      if oAccount.isnull:
        oAccount = helper.CreatePObject('InvestmentNonEmployee', InvesteeId)
        oAccount.BranchCode = aBranchCode
        oAccount.CurrencyCode = '000'
      # end if
        
      oAccount.AccountName  = recBalance.AccountName
      oAccount.FundEntity = 4
      oAccount.InvestmentAmount = recBalance.InvestAmount
      oAccount.SetLifeTime(recBalance.LifeTime)
      oAccount.InvestmentCatId = 1
      oAccount.StartDate = recBalance.StartDate
      oAccount.InvestmentNisbah = recBalance.Nisbah
        
      oItem = helper.GetObjectByNames('AccountTransactionItem',
          {'TransactionId' : oTran.TransactionId,
           'AccountNo' : oAccount.AccountNo
          }
        )
      if oItem.isnull :
        oItem = oTran.CreateAccountTransactionItem(oAccount)
      else:
        oItem.CancelTransaction()
      BeginningBalance = recBalance.Balance or 0.0
      
      oItem.SetMutation('D', BeginningBalance, 1.0)
      oItem.Description = 'Saldo Awal'
      oItem.SetJournalParameter('10')
            
      TotalAmount += BeginningBalance
    # end for
    
    oTran.Amount = TotalAmount
    
    app.ConWriteln('Proses approval data ','TB')
    oTran.AuthStatus = 'F'
    #-----------
    aSQLText = " select transactionitemid from transactionitem \
                     where transactionid=%d " % oTran.TransactionId        

    oRes = config.CreateSQL(aSQLText).RawResult
    
    while not oRes.Eof:
      oItem = helper.GetObject(
           'TransactionItem',oRes.transactionitemid
      ).CastToLowestDescendant()
      app.ConWriteln('Proses item account %s' % oItem.AccountNo,'TB')
      oItem.SetApproval()

      #oItems.Next()
      oRes.Next()
    #-- while
    #----------
    oTran.AutoApproval()
      
    config.Commit() 
  except:
    config.Rollback()
    status = 1
    err_message = str(sys.exc_info()[1])
  
  return status,err_message
