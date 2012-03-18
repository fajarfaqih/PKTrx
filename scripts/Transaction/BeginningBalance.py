# GeneralTransaction.py
import simplejson
import com.ihsan.foundation.pobjecthelper as phelper
import sys

status = 0
msg = ''
FileKwitansi = ''

# *** Beginning Balance Date Variable ***
year = 2010
month = 12
date = 31

# *** RULES
# - Setiap cabang memiliki 1 batch saldo awal dengan batch no = 'SYS-BALANCE-{KODECABANG}'
# - User System / Admin / Pusat boleh membuatkan batch milik cabang 
# - Transaksi dibuat per jenis saldo awal per cabang per valuta

def GetBatch( helper, BranchCode = None):
  config = helper.Config
  
  if BranchCode == None :
    BranchCode = config.SecurityContext.GetUserInfo()[4]
  BatchNo = 'SYS-BALANCE-%s' % BranchCode
  
  oBatch = helper.GetObjectByNames(
       'TransactionBatch', 
         { 'BatchNo' : BatchNo,
           'BranchCode' : BranchCode,
         })
  
  if oBatch.isnull:
    oBatch = helper.CreatePObject('TransactionBatch')
    oBatch.BatchNo = BatchNo
    oBatch.BranchCode = BranchCode 
    oBatch.BatchDate = config.ModLibUtils.EncodeDate(year, month, date)
    oBatch.Inputer = config.SecurityContext.InitUser
    oBatch.Description = 'Saldo Awal'
    oBatch.IsPosted = 'T'
    oBatch.BatchTag = 'SYS'
  # end if
    
  return oBatch

def GetTransaction(helper, oBatch, PrefTransactionNo, Description, CurrencyCode = '000', Rate = 1.0):
  config = helper.Config     
  BranchCode = oBatch.BranchCode #config.SecurityContext.GetUserInfo()[4]
  TransactionNo = '%s-%s' % (PrefTransactionNo,BranchCode)
  
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
    oTran.ReferenceNo = PrefTransactionNo
    oTran.Description = Description
    oTran.TransactionDate = config.ModLibUtils.EncodeDate(year, month, date)
    oTran.ActualDate  = config.ModLibUtils.EncodeDate(year, month, date)
    oTran.IsPosted = 'T'
    oTran.TransactionNo = TransactionNo
    oTran.CurrencyCode = CurrencyCode
    oTran.Rate = Rate
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
    recHeader = params.HeaderData.GetRecord(0)

    app.ConWriteln( 'Get Batch', 'TB')
    oBatch = GetBatch( helper, recHeader.BranchCode)
    app.ConWriteln( 'Get Transaction', 'TB')
    
    #oTran = GetTransaction(helper,oBatch,PrefTransactionNo,'Saldo Awal Kas')
    
    BalanceData = params.BalanceData
    TotalAmount = 0.0
    TotalData = BalanceData.RecordCount
    LsTran = {}
    LsRate = {}
    for i in range(TotalData):
      recBalance = BalanceData.GetRecord(i)
      app.ConWriteln('Proses data ke-%s , %s' %(str(i+1),recBalance.AccountName),'TB')     
      
      AccountNo = recBalance.AccountNo
      oAccount = helper.GetObjectByNames('CashAccount',{'AccountNo':AccountNo})
      if oAccount.isnull:
        raise 'PERINGATAN','Rekening produk %s tidak dapat ditemukan' % (AccountNo)
      
      # Get Rate  
      aCurrencyCode = oAccount.CurrencyCode
      aRate = recBalance.Rate
      #if LsRate.has_key(aCurrencyCode):
      #  aRate = LsRate[aCurrencyCode]
      #else:
      #  aRate = oAccount.LCurrency.Kurs_Tengah_BI
      #  LsRate[aCurrencyCode] = aRate
      # end if  

      # Get Transaction  
      PrefTransactionNo = 'BB-CB-%s' % aCurrencyCode
      if LsTran.has_key(PrefTransactionNo):
        oTran = LsTran[PrefTransactionNo]
      else:
        oTran = GetTransaction(helper, oBatch, PrefTransactionNo, 'Saldo Awal Kas', aCurrencyCode, aRate)
        LsTran[PrefTransactionNo] = oTran
        oTran.Amount = 0.0
        oTran.UpdatedDate = int(config.Now())
        oTran.UpdatedUserId =  config.SecurityContext.InitUser
      # end if

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
      
      oItem.SetMutation('D', BeginningBalance, aRate)
      oItem.Description = 'Saldo Awal'
      oItem.SetJournalParameter('10')
            
      #TotalAmount += BeginningBalance
      oTran.Amount += BeginningBalance      
    # end for

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
    oTran = GetTransaction(helper, oBatch, 'BB-EXTINVS', 'Saldo Awal Investasi Non Karyawan')
    
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

def FixedAsset(config,params):
  LsAssetCategory = {
    1 : 1,
    2 : 2,
    3 : 3,
    4 : 4,
    5 : 8,
    6 : 5,
    7 : 6,
    8 : 7,
  }
  app = config.AppObject  
  app.ConCreate('TB')
  helper = phelper.PObjectHelper(config)
  
  status = 0
  err_message = ''
  config.BeginTransaction()
  try:
    recHeader = params.HeaderData.GetRecord(0)

    app.ConWriteln('Get Batch','TB')
    oBatch = GetBatch(helper, recHeader.BranchCode)
    app.ConWriteln('Get Transaction','TB')
    aCurrencyCode = '000'
    PrefTransactionNo = "BB-FA-%s" % aCurrencyCode
    oTran = GetTransaction(helper, oBatch, PrefTransactionNo, 'Saldo Awal Aset Tetap')
    
    aBranchCode = recHeader.BranchCode
        
    BalanceData = params.BalanceData
    TotalAmount = 0.0
    TotalData = BalanceData.RecordCount
    for i in range(TotalData):
      recBalance = BalanceData.GetRecord(i)
      app.ConWriteln('Proses data ke-%s , %s' %(str(i+1),recBalance.AssetName),'TB')

      ## Create Akun Aset Tetap
      oFAAccount = config.CreatePObject('FixedAsset')
      oFAAccount.Status = 'A'
      oFAAccount.OpeningDate = recBalance.StartDate
      
      # Create AccountNo 
      res = config.CreateSQL("select nextval('seq_deprassetid')").RawResult
      seq = str(res.GetFieldValueAt(0)).zfill(8)
      oFAAccount.AccountNo = '%s.%s' % ('AK', seq)
      oFAAccount.AccountName  = recBalance.AssetName
      oFAAccount.BranchCode = aBranchCode
      oFAAccount.CurrencyCode = aCurrencyCode
      oFAAccount.Qty = 1
      oFAAccount.UangMuka = 0
      oFAAccount.AssetDetailDescription = recBalance.Description

      # Set Kategori Aset
      oFAAccount.AssetCategoryId = LsAssetCategory[recBalance.AssetCategoryId]
      oFAAccount.LifeTime = oFAAccount.LAssetCategory.DefaultLifeTime

      NilaiAwal = recBalance.Amount

      if oFAAccount.AssetCategoryId in (1,8) :
        oFAAccount.DeprState = 'I'
        
        # Set Nilai Awal 
        oFAAccount.NilaiAwal = NilaiAwal
        oFAAccount.NominalPenyusutan = 0
        oFAAccount.PenyusutanKe = 0
        oFAAccount.TotalDibayar = NilaiAwal
        oFAAccount.Balance = NilaiAwal

      else :  
        oFAAccount.DeprState = 'A'

        # Set Nilai Awal 
        NominalPenyusutan = recBalance.DeprAmount #round( NilaiAwal / oFAAccount.LifeTime, 2)
        AkumulasiPenyusutan = recBalance.AccumDeprAmount

        oFAAccount.NilaiAwal = NilaiAwal
        oFAAccount.NominalPenyusutan = NominalPenyusutan
        oFAAccount.PenyusutanKe = recBalance.DeprSeq
        oFAAccount.TotalDibayar = NilaiAwal
        oFAAccount.Balance = NilaiAwal - AkumulasiPenyusutan 
        oFAAccount.TotalPenyusutan = AkumulasiPenyusutan

        # Set Tanggal Proses Depresiasi    
        y, m, d = oFAAccount.OpeningDate[:3]
        oFAAccount.TanggalProsesBerikut = config.ModLibUtils.EncodeDate(2011, 1, 15)

        if oFAAccount.Balance <= 0.0 :
          oFAAccount.DeprState = 'I'
      
      BeginningBalance = oFAAccount.Balance

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