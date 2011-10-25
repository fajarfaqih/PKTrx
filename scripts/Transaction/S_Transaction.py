import com.ihsan.foundation.pobjecthelper as phelper

def CreateTransactionObject(config,TransactionCode,ReferenceNo,Description,TransactionDate) :
  helper = phelper.PObjectHelper(config)
  oTran = helper.LoadScript('GeneralModule.S_ObjectEditor').CreateDataFromList(
       config,'Transaction',
       (('TransactionCode',TransactionCode),
        ('ReferenceNo',ReferenceNo),
        ('Description',Description),
        ('Inputer',(config.SecurityContext.UserId).upper()),
        ('BranchCode',config.SecurityContext.GetUserInfo()[4]),
        ('TransactionDate',TransactionDate),
        ('TransactionTime',config.Now() - int(config.Now())),
        ('AuthStatus','F'))
       )
  return oTran

def CreateTransactionItem(config, ClassItemName, oTran, oFA , rec, Mutation, IsUpdateSaldo, IsPos, BranchCode ) :
  helper = phelper.PObjectHelper(config)
  TransactionItemFields = ('Amount','BranchCode|BranchCode',
    'CurrencyCode','EkuivalenAmount','MutationType|Mutation','Rate','TransactionId|oTran.Key')
  ParamField = {
    'AccountTransactionItem':('AccountNo|oFA.AccountNo',),
    #'DonorTransactionItem':('LProduct.ProductId','AmountPerUnit|rec.GetFieldByName(\'LProduct.FixedValueAmount\')',
    'DonorTransactionItem':('AmountPerUnit|rec.GetFieldByName(\'LProduct.FixedValueAmount\')',
      'TotalUnit','AccountNo|oFA.AccountNo','DonorId|rec.DonorAccount'),
    'DistTransactionItem':('LProduct.ProductId',),
    'ZakahDistTransactItem':('LProduct.ProductId','Ashnaf'),
    'GLTransactionItem':('GLName|rec.GetFieldByName(\'LAccount.Account_Code\')','GLNumber|rec.GetFieldByName(\'LAccount.Account_Name\')'),
    'SENTINEL':'List of Field'
  }
  if ClassItemName == 'DistTransactionItem' and rec.Ashnaf != 'L':
    ClassItemName = 'ZakahDistTransactItem'  
  Fields = TransactionItemFields + ParamField[ClassItemName]
  strFieldValue = '('
  for Field in Fields :
    if Field.find('|') != -1 :
      fl,exp = Field.split('|')
      strFieldValue += '(\'%s\',%s),' % (fl, exp)
    elif Field.find('.') != -1 :
      ln,fl = Field.split('.')
      strFieldValue += '(\'%s\',rec.GetFieldByName(\'%s\')),' % (fl, Field) 
    else :
      strFieldValue += '(\'%s\',rec.GetFieldByName(\'%s\')),' % (Field,Field)
  strFieldValue = strFieldValue[:-1] + ')'
  
  oItem = helper.LoadScript('GeneralModule.S_ObjectEditor').CreateDataFromList(
         config,ClassItemName,eval(strFieldValue)
         )
  
  if IsUpdateSaldo and not oFA.IsNull:
    if IsPos :
      #if ClassItemName == 'DonorTransactionItem' :
      #  oDA = config.CreatePObjImplProxy('DonorAccount')
      #  oDA.key = rec.DonorAccount
      #  oDA.Balance += rec.Amount
        
      oFA.Balance += rec.Amount        
    else :
      #if ClassItemName in ('DistTransactionItem','ZakahDistTransactItem') :
        #oPTH = config.CreatePObject('ProductTransactionHistory')
        #oPTH.TransactionItemId = oItem.TransactionItemId
        #oPTH.LProductBalance = oFA
      
      oFA.Balance -= rec.Amount
  
  return oItem
  #SALDO BELUM DI UPDATE
  
def GeneralCheckBeforeTransaction(config, KT) :
  return 1
  
def GeneralCheckAfterTransaction(config, KT) :
  pass
  
def FindProductBalance(config, ProductId, Valuta = '000', BranchCode = '000') :
  strSQL = 'select * from ProductAccount p, FinancialAccount f where ProductId = %d \
    and p.AccountNo = f.AccountNo and CurrencyCode = \'%s\' ' % (ProductId,Valuta)
  resSQL = config.CreateSQL(strSQL).RawResult  
  resSQL.First()
  oPB = config.CreatePObjImplProxy('ProductAccount')
  oPB.key = resSQL.AccountNo or 0
  return oPB

def FindDonorAccount(config, DonorId, Valuta = '000', TypeAccount = '', IdentifierAccount = 0 ) :
  AccNo = 'NONE'
  strSQL = 'select * from DonorAccount d,FinancialAccount f \
    where DonorId = \'%s\' and CurrencyCode = \'%s\' and d.AccountNo = f.AccountNo ' % (DonorId,Valuta)
  resSQL = config.CreateSQL(strSQL).RawResult  
  resSQL.First()
  
  while not resSQL.Eof :
    if resSQL.DonorAccountType in (None,'') :
      AccNo = resSQL.AccountNo
    resSQL.Next()
  return AccNo
  
def FindSourceAccount(config, AccountNo, ClassAccount, Valuta = '000', Cabang = '000', IsBank = 0) :
  helper = phelper.PObjectHelper(config)
  if IsBank :
    ClassAccount = 'BankCash'
  else :
    if ClassAccount == 'PettyCash' :
      strSQL = 'select * from CashAccount c, FinancialAccount f where \
        username = \'%s\' and c.AccountNo = f.AccountNo and CurrencyCode = \'%s\'' \
          % ((config.SecurityContext.UserId).upper(), Valuta)
  
      resSQL = config.CreateSQL(strSQL).RawResult
      resSQL.First()
      if resSQL.Eof :
        raise 'PERINGATAN','Kas User : %s belum dibuat' % config.SecurityContext.UserId
      AccountNo = resSQL.AccountNo
  
    else : #Cabang Kas
      raise 'PERINGATAN','Kas Cabang tidak ditemukan'
      ##Masih perlu diperbaiki
      Cabang = ''
      strSQL = 'select * from CashAccount where BranchCode = \'%s\' ' % Cabang
  
      resSQL = config.CreateSQL(strSQL).RawResult
      resSQL.First()
      if resSQL.Eof :
        raise 'PERINGATAN','Kas Cabang : %s belum dibuat' % Cabang
      AccountNo = resSQL.AccountNo
  
  oAcc,Field = helper.LoadScript('GeneralModule.S_ObjectEditor').FindObj(
      config, ClassAccount,(('AccountNo',AccountNo),))

  return oAcc
  
def CreateTransaction(config, parameter, KT) :
  ParamKT = {
   'SD001':'CreateDataTransaction(config, parameter, KT, AutoOto)',
   'DD001':'CreateDataTransaction(config, parameter, KT, AutoOto)',
   'CI001':'CreateDataTransaction(config, parameter, KT, AutoOto)',
   'CO001':'CreateDataTransaction(config, parameter, KT, AutoOto)',
   'TU001':'CreateDataTransaction(config, parameter, KT, AutoOto)',
   'SENTINEL':'Function'
  }
  AutoOto = GeneralCheckBeforeTransaction(config, KT)
  eval(ParamKT[KT])
  GeneralCheckAfterTransaction(config, KT)
  
def CreateDataTransaction(config, parameter, KT, AutoOto = 0, DAccount = '') :
  OppositeMutation = {
   'D':'C',
   'C':'D'
  }
  GTrans = ['DonorTransactionItem','DistTransactionItem','AccountTransactionItem','GLTransactionItem']
  sTrans = parameter.uipTransaction.GetRecord(0)
  PCash = 'PettyCash'
  BCash = 'BranchCash'
  IsUpdateSaldo = 1
  IsAddProduct = 1
  BaseListTran = 'C'
  IsPos = 1
  IsNeg = 0
  IsProd = 1
  Amt = {
   '000':0.0,
   '411':0.0,
   'SENTINEL':0.0
   }
  EkivAmt = 0.0
  ParamTrans = {
   'SD001':('S',PCash,BaseListTran,not IsUpdateSaldo, 'DonorTransactionItem', IsPos, IsPos, IsProd),
   'DD001':('S',PCash,OppositeMutation[BaseListTran],not IsUpdateSaldo,'DistTransactionItem', IsNeg, IsNeg, IsProd),
   'CI001':('S',PCash,BaseListTran,not IsUpdateSaldo,'GLTransactionItem', IsPos, 0, not IsProd),
   'CO001':('S',PCash,OppositeMutation[BaseListTran],not IsUpdateSaldo,'GLTransactionItem',IsNeg,0, not IsProd),
   'NTD001':('C','','',not IsUpdateSaldo),
   'NTC001':('C','','',not IsUpdateSaldo),
   'TU001':('C','','',not IsUpdateSaldo),
   'SENTINEL':''
  } 
  
  oTran = CreateTransactionObject(config,KT,sTrans.ReferenceNo,sTrans.Description,sTrans.TransactionDate)
  Param = ParamTrans[KT]
  oFA = ''
  if Param[0] == 'S' : #Single (source cash or bank)
    donorID = parameter.uipData.GetRecord(0).DonorId
    for i in range(parameter.uipItem.RecordCount) :
      rec = parameter.uipItem.GetRecord(i)
      if Param[7] :
        oFA = FindProductBalance(config, rec.GetFieldByName('LProduct.ProductId'), rec.CurrencyCode, config.SecurityContext.GetUserInfo()[4])
        if oFA.IsNull :
          raise 'PERINGATAN','Produk belum dilengkap data account-nya'
        #if KT in ('SD001') :
        #  rec.DonorAccount = FindDonorAccount(config, parameter.uipData.GetRecord(0).DonorId, rec.CurrencyCode)
        #  if rec.DonorAccount == 'NONE' :
        #    raise 'PERINGATAN','Rekening donor belum dibuat'
        rec.DonorAccount = donorID
      if Amt.has_key(rec.CurrencyCode) :
        Amt[rec.CurrencyCode] += rec.Amount
      else :
        raise 'PERINGATAN','Kode Valuta belum didefinisikan'
      EkivAmt += rec.EkuivalenAmount
      oItem = CreateTransactionItem(config, Param[4], oTran, oFA, 
        rec, Param[2], Param[3], Param[6], config.SecurityContext.GetUserInfo()[4])
    
    #Insert Data and Nominal
    rec = parameter.uipItem.GetRecord(0)
    for Valuta in Amt.keys() :
      if Amt[Valuta] != 0.0 :      
        oAcc = FindSourceAccount(config, sTrans.GetFieldByName('LBank.AccountNo'), 
         Param[1], Valuta, config.SecurityContext.GetUserInfo()[4], sTrans.Cara_Bayar == 'B')
        rec.Amount = Amt[Valuta] 
        oItem = CreateTransactionItem(config, 'AccountTransactionItem', oTran, 
          oAcc, rec, OppositeMutation[Param[2]], Param[3],Param[5], config.SecurityContext.GetUserInfo()[4])
  else : #Custom
    for i in range(parameter.uipItem.RecordCount) :
        rec = parameter.uipItem.GetRecord(i)
        if (rec.TransType-2) in (0,1) :
          oFA = FindProductBalance(config, eval(rec.Id_Produk_Rekening))
          if GTrans[rec.TransType-2] == 'DonorTransactionItem' :
            #rec.DonorAccount =  FindDonorAccount(config, rec.DonorId)
            rec.DonorAccount =  rec.DonorId
        elif (rec.TransType-2) in (2,) :
          oFA = config.CreatePObjImplProxy('FinancialAccount')
          oFA.key = rec.GetFieldByName('LCashAccount.AccountNo')
        oItem = CreateTransactionItem(config, GTrans[rec.TransType-2], oTran, oFA, 
          rec, rec.MutationType, Param[3],0, config.SecurityContext.GetUserInfo()[4])  
  
  if AutoOto :
    OtoTransaction(config, oTran.Key, config.Now(), not Param[3])

def OtoTransaction(config, TransactionKey, TglTrans, IsUpdateSaldo, UserId = 'OTOMATIS') :
  helper = phelper.PObjectHelper(config)
  oTran,Field = helper.LoadScript('GeneralModule.S_ObjectEditor').FindObj(
        config, 'Transaction',
        (('TransactionId',TransactionKey),))
  oTran.AuthDate = TglTrans
  oTran.AuthStatus = 'T'
  oTran.AuthUser = UserId
  if IsUpdateSaldo :
    IsPos = 1
    IsNeg = 0
    ParamUpd = {
       'AccountTransactionItem':(IsPos,IsNeg),
       'DonorTransactionItem':(IsNeg,IsPos),
       'DistTransactionItem':(IsPos,IsNeg),
       'SENTINEL':''
    }
    #Get Transaction Item
    config.FlushUpdates()
    strSQL = 'select * from TransactionItem where TransactionId = %d' % oTran.Key
    resSQL = config.CreateSQL(strSQL).RawResult  
    resSQL.First()
    while not resSQL.Eof :
      #Get Account
      oItem = config.CreatePObjImplProxy('TransactionItem')
      oItem.Key = resSQL.TransactionItemId
      oItem = oItem.CastToLowestDescendant()
      #Update Saldo
      if ParamUpd.has_key(oItem.ClassName) :
        oAccount = helper.GetObject('FinancialAccount', oItem.AccountNo).CastToLowestDescendant()
        oAccount.UpdateBalance(oItem.MutationType, oItem.Amount)
        #oFA = config.CreatePObjImplProxy('FinancialAccount')
        #oFA.Key = oItem.AccountNo 
        #if (ParamUpd[oItem.ClassName][0] and oItem.MutationType == 'D') or \
        #   (ParamUpd[oItem.ClassName][1] and oItem.MutationType == 'C'):
        #  if oItem.ClassName == 'DonorTransactionItem' :
            #oDA = config.CreatePObjImplProxy('DonorAccount')
            #oDA.key = rec.DonorAccount
            #oDA.Balance += rec.Amount
        #    pass
          
            #oPTH = config.CreatePObject('ProductTransactionHistory')
            #oPTH.TransactionItemId = oItem.TransactionItemId
            #oPTH.LProductBalance = oPB
        #  oFA.Balance += oItem.Amount        
        #else :
          #if oItem.ClassName in ('DistTransactionItem','ZakahDistTransactItem') :
            #oPTH = config.CreatePObject('ProductTransactionHistory')
            #oPTH.TransactionItemId = oItem.TransactionItemId
            #oPTH.LProductBalance = oFA
          
        #  oFA.Balance -= oItem.Amount
      resSQL.Next()
    
def DAFScriptMain(config, parameter, returnpacket):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  pass
  
  return 1
