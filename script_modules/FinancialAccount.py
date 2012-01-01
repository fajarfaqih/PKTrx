# FinancialAccount.py

import com.ihsan.foundation.pobject as pobject
import com.ihsan.util.customidgenAPI as customidgenAPI
import sys

class FinancialAccount(pobject.PObject):
  # static variable
  pobject_classname = 'FinancialAccount'
  pobject_keys = ['AccountNo']

  def OnCreate(self):
    self.Status = 'A'
    self.Balance = 0.0
    self.OpeningDate = int(self.Config.Now())

  def GetAccountInterface(self):
    pass

  def UpdateDailyBalance(self,jenis,amount):
    self.GetLastDailyBalance().UpdateBalance(jenis,amount)

  def CreateNewDailyBalance(self):
    oDailyBalance = self.Helper.CreatePObject('DailyBalance',self.AccountNo)
    return oDailyBalance

  def GetLastDailyBalance(self):
    if self.LastDailyBalanceID in [None,0]:
      oLastDailyBalance = self.CreateNewDailyBalance()
    else:
      oLastDailyBalance = self.LLastDailyBalance
    # end if

    if oLastDailyBalance.IsClosed == 'T' :
      LastDayBalance = oLastDailyBalance.TrialBalance
      oLastDailyBalance = self.CreateNewDailyBalance()
      oLastDailyBalance.TrialBalance = LastDayBalance
      oLastDailyBalance.LastDayBalance = LastDayBalance

      self.LastDailyBalanceId = oLastDailyBalance.dailybalanceid

    return oLastDailyBalance

  def CheckForDelete(self): return 1

class CashAccount(FinancialAccount):
  # static variable
  pobject_classname = 'CashAccount'

  def UpdateBalance(self, jenis, amount,isBalanceIgnored=0):
    if jenis == 'D':
      self.Balance += amount
    else: # jenis == 'C'
      # SEMENTARA PEMERIKSAAN SALDO DITUTUP DULU by Wisnu 04 Nov 2011
      #if self.Balance < amount:
      #  raise 'Balance', 'Saldo tidak cukup!'
      self.Balance -= amount
    #self.UpdateDailyBalance(jenis,amount)

  def GetBalanceByDate(self,Date):
    strSQL = "select sum(case when a.mutationtype='D' then a.Amount \
                           else -a.Amount \
                      end) \
              from transactionitem a, transaction b, accounttransactionitem c\
              where a.transactionid=b.transactionid \
                 and a.transactionitemid=c.transactionitemid \
                 and c.accountno = '%s' " % self.AccountNo

    if Date != None :
      FormattedDate = self.Config.FormatDateTime('yyyy-mm-dd',Date)
      strSQL += " and b.actualdate < '%s' " % FormattedDate

    resSQL = self.Config.CreateSQL(strSQL).rawresult

    return resSQL.GetFieldValueAt(0) or 0.0

  def CheckForDelete(self):
    sqlCheck = "select count(TransactionItemId) from accounttransactionitem where AccountNo='%s' "% (self.AccountNo)

    resSQL = self.Config.CreateSQL(sqlCheck).rawresult
    if resSQL.GetFieldValueAt(0) > 0:
      raise '','Data tidak dapat dihapus karena menjadi referensi oleh data lain'

    return 1

class BankCash(CashAccount):
  # static variable
  pobject_classname = 'BankCash'

  def OnCreate(self):
    CashAccount.OnCreate(self)

    rsSeq = config.CreateSQL("select nextval('seq_bankcashid')").RawResult
    sequence = str(rsSeq.GetFieldValueAt(0)).zfill(8)
    self.AccountNo = 'BA.%s.%s' % (self.BankCode,sequence)

  def GetAccountInterface(self):
    return self.Helper.GetObject('ParameterGlobal', 'GLIBANK').Get()

class BranchCash(CashAccount):
  # static variable
  pobject_classname = 'BranchCash'

  def GetAccountInterface(self):
    return self.Helper.GetObject('ParameterGlobal', 'GLIBRANCH').Get()

class PettyCash(CashAccount):
  # static variable
  pobject_classname = 'PettyCash'

  def GetAccountInterface(self):
    return self.Helper.GetObject('ParameterGlobal', 'GLICASH').Get()

class ProductAccount(FinancialAccount):
  # static variable
  pobject_classname = 'ProductAccount'

  def OnCreate(self, param):
    ProductCode, Cabang, Valuta = param
    self.AccountNo = ProductCode + '.' + Cabang + '.' + Valuta

  def GetNextIdProductAccount(self):
    rId = self.Config.CreateSQL("select nextval('seq_productaccountid')").RawResult
    return rId.GetFieldValueAt(0)

  def UpdateBalance(self, jenis, amount,isBalanceIgnored=0):
    if jenis == 'D':
      #if self.Balance < amount:
      #  raise 'Balance', 'Saldo tidak cukup!'
      self.Balance -= amount
    else: # jenis == 'C'
      self.Balance += amount
    #self.UpdateDailyBalance(jenis,amount)

  def GetCollectionInterface(self, aFundEntity):
    ENTITY_MAP = {
      1: 'PHP_ZAKAT', 2: 'PHP_INFAQ', 3: 'PHP_WAKAF', 5: 'PHP_NONHALAL'
    }
    aIntfCode = ENTITY_MAP[aFundEntity]

    return self.LProduct.GetAccountInterface(aIntfCode).AccountCode

  def GetDistributionInterface(self, aFundEntity):
    ENTITY_MAP = {
      1: 'PDG_ZAKAT', 2: 'PDG_INFAQ', 3: 'PDG_WAKAF', 4:'PDG_AMIL', 5: 'PDG_NONHALAL'
    }
    aIntfCode = ENTITY_MAP[aFundEntity]

    return self.LProduct.GetAccountInterface(aIntfCode).AccountCode

  def GetBalanceByDate(self,Date):
    strSQL = "select sum(case when a.mutationtype='C' then a.Amount \
                           else -a.Amount \
                      end) \
              from transactionitem a, transaction b, accounttransactionitem c\
              where a.transactionid=b.transactionid \
                 and a.transactionitemid=c.transactionitemid \
                 and c.accountno = '%s' " % self.AccountNo

    if Date != None :
      FormattedDate = self.Config.FormatDateTime('yyyy-mm-dd',int(Date))
      strSQL += " and b.actualdate < '%s' " % FormattedDate

    resSQL = self.Config.CreateSQL(strSQL).rawresult

    return resSQL.GetFieldValueAt(0) or 0.0

  def GetEntityBalance(self,Entity=0,Date=None):
    strSQL = "select sum(case when a.mutationtype='C' then a.Amount \
                           else -a.Amount \
                      end) \
              from transactionitem a, transaction b, accounttransactionitem c\
              where a.transactionid=b.transactionid \
                 and a.transactionitemid=c.transactionitemid \
                 and c.accountno = '%s' " % self.AccountNo

    if Entity != 0 :
      strSQL += ' and c.FundEntity=%d ' % Entity

    if Date != None :
      FormattedDate = self.Config.FormatDateTime('yyyy-mm-dd',Date)
      strSQL += " and b.actualdate < '%s' " % FormattedDate

    resSQL = self.Config.CreateSQL(strSQL).rawresult

    return resSQL.GetFieldValueAt(0) or 0.0

  def GetOtherBalance(self,Date=None):
    strSQL = "select sum(case when a.mutationtype='C' then a.Amount \
                           else -a.Amount \
                      end) \
              from transactionitem a, transaction b, accounttransactionitem c\
              where a.transactionid=b.transactionid \
                 and a.transactionitemid=c.transactionitemid \
                 and c.accountno = '%s' \
                 and (c.FundEntity not in (1,2,3) or c.FundEntity is null)  " % self.AccountNo

    if Date != None :
      FormattedDate = self.Config.FormatDateTime('yyyy-mm-dd',Date)
      strSQL += " and b.actualdate < '%s' " % FormattedDate

    resSQL = self.Config.CreateSQL(strSQL).rawresult

    return resSQL.GetFieldValueAt(0) or 0.0

class ProjectAccount(ProductAccount):
  # static variable
  pobject_classname = 'ProjectAccount'

  def OnCreate(self, param):
    ProductCode, Cabang, Valuta = param
    
    self.AccountNo = self.GenerateAccountNo(ProductCode, Cabang, Valuta) 
  
  def GenerateAccountNo(self, aProductCode, aCabang, aValuta):
    prefix = 'P' + aProductCode + '.' + aCabang
    sequence = self.CreateProjectAccSequence(prefix)
    return prefix + '.' + sequence
    
  def CreateProjectAccSequence(self,prefix):
    sequence = '' 
    
    customid = customidgenAPI.custom_idgen(self.Config)
    customid.PrepareGetID('PROJECTACCOUNT', prefix)
    try:
      id = customid.GetLastID()
      sequence = str(id).zfill(4)
      customid.Commit()
    except:
      customid.Cancel()
      raise '', str(sys.exc_info()[1])

    return sequence
  
  def GetListDataTransaction(self):
    config = self.Config
    
    oqlCheck = "select from AccountTransactionItem \
                 [ AccountNo = :AccountNo ] \
                 (TransactionId,TransactionItemId,self); "
                  
    oql = config.OQLEngine.CreateOQL(oqlCheck)
    oql.SetParameterValueByName('AccountNo', self.AccountNo)
    oql.ApplyParamValues()
    oql.active = 1
    return oql.rawresult
    
    
  def CheckForDelete(self):
    # Override Parent (FinancialAccount) CheckForDelete Function
    
    #recTrans = self.GetListDataTransaction()    
    #if not recTrans.Eof :
    #  raise '','Proyek tidak dapat dihapus karena telah memiliki transaksi'

    return 1
    
  def OnDelete(self):
    helper = self.Helper
    config = self.Config
    
    recTrans = self.GetListDataTransaction()

    while not recTrans.Eof:      
      oTran = helper.GetObject('Transaction',recTrans.TransactionId)
      oTran.Delete()
      recTrans.Next()
    # end while
    
class AccountReceivable(FinancialAccount):
  # static variable
  pobject_classname = 'AccountReceivable'

  def OnDelete(self):    
    sDelete = "delete from DailyBalance where accountno='%s' " % (self.AccountNo)
    sqlRes = self.Config.ExecSQL(sDelete)
    
    if sqlRes == -9999:
      raise "SQL Error", config.GetDBConnErrorInfo()
    
 
  def UpdateBalance(self, jenis, amount,isBalanceIgnored=0):
    if jenis == 'D':
      self.Balance += amount
    else: # jenis == 'C'       
      #if self.Balance < amount and not isBalanceIgnored:
      #  raise 'Balance', 'Nilai transaksi melebihi outstanding!'

      self.Balance -= amount
    #self.UpdateDailyBalance(jenis,amount)

  def GetBalanceByDate(self,Date):
    strSQL = "select sum(case when a.mutationtype='D' then a.Amount \
                           else -a.Amount \
                      end) \
              from transactionitem a, transaction b, accounttransactionitem c\
              where a.transactionid=b.transactionid \
                 and a.transactionitemid=c.transactionitemid \
                 and c.accountno = '%s' " % self.AccountNo

    if Date != None :
      FormattedDate = self.Config.FormatDateTime('yyyy-mm-dd',Date)
      strSQL += " and b.actualdate < '%s' " % FormattedDate

    resSQL = self.Config.CreateSQL(strSQL).rawresult

    return resSQL.GetFieldValueAt(0) or 0.0

    

class EmployeeAccountReceivable(AccountReceivable):
  # static variable
  pobject_classname = 'EmployeeAccountReceivable'

  def OnCreate(self, aEmployeeId):
    FinancialAccount.OnCreate(self)
    #self.AccountNo = aEmployeeId
    self.AccountNo = 'PKPU' + str(aEmployeeId).zfill(7)
    #self.EmployeeId = str(aEmployeeId)
    self.EmployeeIdNumber = aEmployeeId

  def GetAccountInterface(self):
    return self.Helper.GetObject('ParameterGlobal', 'GLIEMP').Get()
    
class ExternalAccountReceivable(AccountReceivable):
  # static variable
  pobject_classname = 'ExternalAccountReceivable'

  def OnCreate(self, aDebtorId):
    FinancialAccount.OnCreate(self)
    self.AccountNo = 'EXT.AR.' + str(aDebtorId).zfill(7)
    self.DebtorId = aDebtorId

  def GetAccountInterface(self):
    return self.Helper.GetObject('ParameterGlobal', 'GLIXDEB').Get()    

class EmployeeCashAdvance(AccountReceivable):
  # static variable
  pobject_classname = 'EmployeeCashAdvance'

  def OnCreate(self, params ):
    aEmployeeId , aCurrencyCode = params
    FinancialAccount.OnCreate(self)

    self.AccountNo = 'CA.%s.%s' % (aCurrencyCode, str(aEmployeeId).zfill(7))
    self.CurrencyCode = aCurrencyCode
    #self.EmployeeId = str(aEmployeeId)
    self.EmployeeIdNumber = aEmployeeId
  
  # Fungsi in dipake sementara dan mengijinkan untuk saldo minus !!!!!
  # Nanti perlu ditutup lagi  26 Oct 2011 by Wisnu 
  def UpdateBalance(self, jenis, amount,isBalanceIgnored=0):
    if jenis == 'D':
      self.Balance += amount
    else: # jenis == 'C'       
      self.Balance -= amount
    #self.UpdateDailyBalance(jenis,amount)
    
  def GetAccountInterface(self):
    return self.Helper.GetObject('ParameterGlobal', 'GLICASHADV').Get()

     
class InvestmentManager(pobject.PObject):
  # static variable
  pobject_classname = 'InvestmentManager'
  pobject_keys = ['ManagerID']
  
class InvestmentCategory(pobject.PObject):
  # static variable
  pobject_classname = 'InvestmentCategory'
  pobject_keys = ['InvestmentCatId']
  
  def GLInterfaceExist(self):  
    sql = "select count(*) from \
        GLInterfaceContainer c ,GLInterfaceMember m \
        where c.GLIContainerId = m.GLIContainerId \
        and c.GLIContainerId=%d " % self.GLIContainerId or 0

    resSQL = self.Config.CreateSQL(sql).rawresult     
    return resSQL.GetFieldValueAt(0) or 0
      
  def GenerateGLContainer(self):
    oGLIContainer = self.Helper.CreatePObject('GLInterfaceContainer')
    oGLIContainer.GLIContainerName = self.InvestmentCatName
    self.GLIContainerId = oGLIContainer.GLIContainerId
      
  def GenerateGLInterface(self):
    if self.GLIContainerId in ['',0,None] :
      self.GenerateGLContainer()
      
    DefaultGL = {
      'INVEST_ACC'  : ('AKUN INVESTASI',''),
    }     
    
    if self.InvestmentCatType == 'L' : # INVESTASI JANGKA PANJANG
      DefaultGL['INVEST_ACC'] = ('AKUN INVESTASI','1210201')
    elif self.InvestmentCatType == 'S' : # INVESTASI JANGKA PENDEK 
      DefaultGL['INVEST_ACC'] = ('AKUN INVESTASI','1170201')          
    # endif      
      
    for kode,item in DefaultGL.items():
      oGLIMember = self.Helper.GetObjectByNames(
        'GLInterfaceMember',
        { 'GLIMemberCode' : kode ,
          'GLIContainerId' : self.GLIContainerId
        }
      )
      if oGLIMember.isnull :
        oGLIMember = self.Helper.CreatePObject('GLInterfaceMember')
        oGLIMember.GLIContainerId = self.GLIContainerId
        oGLIMember.GLIMemberCode = kode
        oGLIMember.Description = item[0]
        oGLIMember.AccountCode = item[1]
    
        
class Investment(AccountReceivable):
  # static variable
  pobject_classname = 'Investment'
  
  def SetLifeTime(self,LifeTime):
    self.LifeTime = LifeTime
    self.InvestmentShare = self.InvestmentAmount // LifeTime
    
  def GetAccountInterface(self):
    return self.Helper.GetObject('ParameterGlobal', 'GLIINVEST').Get()

class InvestmentNonEmployee(Investment):
  # static variable
  pobject_classname = 'InvestmentNonEmployee'
  
  def OnCreate(self, InvesteeId):
    Investment.OnCreate(self)
    
    # Generate Id Investment
    BranchCode = self.Config.SecurityContext.GetUserInfo()[4]
    prefix = 'INVEST.%s' % BranchCode
    customid = customidgenAPI.custom_idgen(self.Config)
    customid.PrepareGetID('INVESTMENT', prefix)
    try:
      id = customid.GetLastID()
      sequence = str(id).zfill(5)
      customid.Commit()
    except:
      customid.Cancel()
      raise '', str(sys.exc_info()[1])
    
    self.AccountNo = '%s.%s' % (prefix , sequence)
    self.InvesteeId = InvesteeId

  def GetInvesteeName(self):
    return self.LInvestee.InvesteeName
    
class InvestmentEmployee(Investment):
  # static variable
  pobject_classname = 'InvestmentEmployee'
  
  def OnCreate(self, EmployeeId):
    Investment.OnCreate(self)
    
    # Generate Id Investment
    BranchCode = self.Config.SecurityContext.GetUserInfo()[4]
    prefix = 'INVEST.EMP.%s' % BranchCode
    customid = customidgenAPI.custom_idgen(self.Config)
    customid.PrepareGetID('INVESTMENT', prefix)
    try:
      id = customid.GetLastID()
      sequence = str(id).zfill(5)
      customid.Commit()
    except:
      customid.Cancel()
      raise '', str(sys.exc_info()[1])
    
    self.AccountNo = '%s.%s' % (prefix , sequence)
    self.EmployeeId = EmployeeId

  def GetAccountInterface(self):
    return self.Helper.GetObject('ParameterGlobal', 'GLIINVEST').Get()

  def GetInvesteeName(self):
    oEmployee = self.Helper.GetObject('VEmployee',self.EmployeeId)
    if oEmployee.isnull:
      return ''
    else:  
      return self.LEmployee.EmployeeName
       
class DailyBalance(pobject.PObject):
  #static variable
  pobject_classname = 'DailyBalance'
  pobject_keys = ['DailyBalanceID']

  def OnCreate(self,AccountNo):
    self.AccountNo = AccountNo
    self.Credit = 0.0
    self.Debit = 0.0
    self.Balance = 0.0
    self.TrialBalance = 0.0
    self.Balancedate = int(self.Config.Now())
    self.LastDayBalance = 0.0
    self.IsClosed = 'F'

  def UpdateBalance(self,jenis,amount):

    if self.LFinancialAccount.FinancialAccountType in ['C']:
      amounttrialbalance = amount
    else:
      amounttrialbalance = -1 * amount
    #  end if

    if jenis == 'D':
      self.Debit += amount
      self.TrialBalance += amounttrialbalance
    else:
      self.Credit += amount
      self.TrialBalance -= amounttrialbalance
    # end if

    #self.Balance = 0.0

  def CloseDay(self,debet,credit):
    self.Debit = debet
    self.Credit = credit
    if self.LFinancialAccount.FinancialAccountType in ['C']:
      DebetCredit = debet - credit
    else:
      DebetCredit = credit - debet

    self.TrialBalance = self.LastDayBalance + DebetCredit
    self.IsClosed = 'T'

class Invoice(pobject.PObject): 
  pobject_classname = 'Invoice'
  pobject_keys = ['InvoiceId']
  
  def OnCreate(self):
    self.InvoicePaymentStatus = 'F'
    self.BranchCode = self.Config.SecurityContext.GetUserInfo()[4]
  
  def OnDelete(self):
    #if self.TransactionId not in ['',0,None] :
    #  oTransaction = self.LTransaction
    #  oTransaction.Delete()
    if self.PaymentTransactionItemId not in [0,None,''] :
      raise '',"Data invoice tidak dapat dihapus karena telah memiliki transaksi pembayaran. \nSilahkan hapus dahulu transaksi pembayarannya"
    
  def GenerateInvoicePrintData(self):
    helper = self.Helper
    config = self.Config
     
    # Get Corporate Object
    corporate = helper.CreateObject('Corporate')
    login_context = corporate.LoginContext
    UserName = login_context.Nama_User
     
    # Get Tools
    ToolsConvert = helper.LoadScript('Tools.S_Convert')
  
    # Set Terbilang
    Total = self.InvoiceAmount or 0.0
     
    Terbilang = ToolsConvert.Terbilang(config,Total,
              KodeMataUang = self.CurrencyCode,
              NamaMataUang = self.LCurrency.Symbol_Says)
    
    Terbilang = ToolsConvert.Divider(Terbilang,45)
    if len(Terbilang) == 1 : Terbilang.append('')
    
    # Get Template
    PrintHelper = helper.CreateObject('PrintHelper')
    #templateInvoice = PrintHelper.LoadHtmTemplate('tplinvoice')
    templateInvoice = PrintHelper.LoadRtfTemplate('tplInvoiceNew')
    
    NamaLembaga = helper.GetObject('ParameterGlobal', 'COMPNAME').Get()
    dataInvoice = {}
    dataInvoice['INVOICENO'] = self.InvoiceNo
    dataInvoice['CUSTOMERNAME'] = self.LSponsor.Full_Name
    dataInvoice['CUSTOMERADDRESS'] = self.InvoiceAddress
    dataInvoice['INVOICEDATE'] = config.FormatDateTime('dd mmm yyyy',self.GetAsTDateTime('InvoiceDate'))
    dataInvoice['TERMDATE'] = config.FormatDateTime('dd mmm yyyy',self.GetAsTDateTime('InvoiceTermDate'))
    dataInvoice['SAYS'] = Terbilang[0] + ' ' + Terbilang[1]
    dataInvoice['AMOUNT'] = '%(SYMBOL)s %(AMOUNT)s' % { 'SYMBOL' : self.LCurrency.Symbol , 'AMOUNT' : config.FormatFloat('#,##0.00',Total)} 
    dataInvoice['QTY'] = '1'
    dataInvoice['DESCRIPTION'] = self.Description
    dataInvoice['BANKNAME'] = self.InvoiceBankName
    dataInvoice['BANKACCOUNTNO'] = self.InvoiceBankAccountNumber
    dataInvoice['BANKACCOUNTNAME'] = self.InvoiceBankAccountName
    dataInvoice['SIGNNAME'] = self.InvoiceOfficerName
    dataInvoice['JOBPOSITION'] = self.InvoiceOfficerPosition
    dataInvoice['USER_CETAK'] = UserName
    dataInvoice['CONTACTPERSON'] = self.InvoiceContactPerson
    dataInvoice['CONTACTPHONE'] = self.InvoiceContactPhone

    Invoice = ''
  
    Invoice  += templateInvoice % dataInvoice
    
    return Invoice
    
class InvoiceFA(Invoice):
  pobject_classname = 'InvoiceFA'
  pobject_keys = ['InvoiceId']

class InvoiceProduct(Invoice):
  pobject_classname = 'InvoiceProduct'
  pobject_keys = ['InvoiceId']

class InvoiceProductDefaultData(pobject.PObject):
  pobject_classname = 'InvoiceProductDefaultData'
  pobject_keys = ['BranchCode']
  
class DepreciableAsset(FinancialAccount):
  # static variable
  pobject_classname = 'DepreciableAsset'
  
  def OnCreate(self):
    FinancialAccount.OnCreate(self)
    
    res = self.Config.CreateSQL("select nextval('seq_deprassetid')").RawResult
    seq = str(res.GetFieldValueAt(0)).zfill(8)
    self.AccountNo = '%s.%s' % (self.TagCode, seq)
    self.AccountName = self.AccountNo
    self.CurrencyCode = '000'
    self.DeprState = 'A'
    self.NilaiAwal = 0.0
    self.NominalPenyusutan = 0.0
    self.PenyusutanKe = 0
    self.TotalDibayar = 0.0 
  
  def SetInitialProcessDate(self):
    libUtils = self.Config.ModLibUtils
    
    y, m, d = self.OpeningDate[:3]    
    self.TanggalProsesBerikut = libUtils.EncodeDate(y, m, 25)    
    if d > 25:       
      self.TanggalProsesBerikut = libUtils.IncMonth(self.GetAsTDateTime('TanggalProsesBerikut'), 1)      
          
  def SetLifeTime(self,):
    pass
        
  def SetInitialValue(self, amount):
    self.NilaiAwal = amount
    self.NominalPenyusutan = round(amount/self.LifeTime, 2)
    
  def CheckForDepreciation(self):
    return (self.DeprState == 'A' and self.Balance > 0)
  
  def Depreciation(self,DeprDate):
    self.PenyusutanKe += 1
    if (self.PenyusutanKe < self.LifeTime and 
      self.Balance > self.NominalPenyusutan):
      deprValue = self.NominalPenyusutan
    else:
      deprValue = self.Balance
      self.DeprState = 'N'
    #-- if.else
    
    libUtils = self.Config.ModLibUtils
    self.TanggalProsesTerakhir = DeprDate #libUtils.Now()
    self.TanggalProsesBerikut = libUtils.IncMonth(DeprDate, 1)
    self.TotalPenyusutan += deprValue
    
    return deprValue

  def UpdateBalance(self, jenis, amount,isBalanceIgnored=0):
    if jenis == 'D':
      self.Balance += amount
    else: # jenis == 'C'
      if self.Balance < amount:
        raise 'Balance', 'Saldo tidak cukup!'
      self.Balance -= amount
    #self.UpdateDailyBalance(jenis,amount)

class FixedAsset(DepreciableAsset):
  # static variable
  pobject_classname = 'FixedAsset'

  def OnCreate(self):
    self.TagCode = 'AK'
    DepreciableAsset.OnCreate(self)
  
  def SetAssetCategory(self,AssetCategoryId):
    self.AssetCategoryId = AssetCategoryId
    self.LifeTime = self.LAssetCategory.DefaultLifeTime

  def GetAssetAccount(self):
    return self.LAssetCategory.LGLIContainer.GetAccountInterface('ASSET_ACC').AccountCode

  def GetDeprAccount(self):
    return self.LAssetCategory.LGLIContainer.GetAccountInterface('DEPR_ACC').AccountCode
  
  def GetLiabilityAccount(self):
    return self.LAssetCategory.LGLIContainer.GetAccountInterface('ASSET_LIAB').AccountCode  
    
  def GetAssetFromAmilAccount(self):
    return self.LAssetCategory.LGLIContainer.GetAccountInterface('ASSETFROMAMIL').AccountCode

  def GetAssetKelolaanPlusAccount(self,aFundEntity):
    ENTITY_MAP = {
      1: 'ASSET_FROM_ZAKAT', 2: 'ASSET_FROM_INFAQ', 3: 'ASSET_FROM_WAKAF', 5: 'ASSET_FROM_NONHALAL'
    }
    aIntfCode = ENTITY_MAP[aFundEntity]

    return self.LProductAccount.LProduct.GetAccountInterface(aIntfCode).AccountCode

  def GetAssetKelolaanMinusAccount(self,FundEntity):
    ENTITY_MAP = {
      1: 'ASSET_TO_ZAKAT', 2: 'ASSET_TO_INFAQ', 3: 'ASSET_TO_WAKAF', 5: 'ASSET_TO_NONHALAL'
    }
    aIntfCode = ENTITY_MAP[aFundEntity]

    return self.LProductAccount.LProduct.GetAccountInterface(aIntfCode).AccountCode        

  def CreateSellTransactInfo(self,oTransactItem,SellAmount):
    self.HargaJual = SellAmount
    
    # --- Sementara kode ini tidak dipake dulu
    #param = {'TransactionItem' : oTransactItem, 'FixedAsset': self}    
    #oFATInfo = self.Helper.CreatePObject('FixedAssetTransactInfo',param)
    #FATInfo.SetSellAmount(SellAmount)        
    #return oFATInfo    
    
class AmortizedCost(DepreciableAsset):
  # static variable
  pobject_classname = 'AmortizedCost'

  def GetAccountInterface(self):
    return self.Helper.GetObject('ParameterGlobal', 'GLICPA').Get()

class CPIACategory(pobject.PObject):
  # static variable
  pobject_classname = 'CPIACategory'
  pobject_keys = ['CPIACategoryId']
  
  def GLInterfaceExist(self):  
    sql = "select count(*) from \
        GLInterfaceContainer c ,GLInterfaceMember m \
        where c.GLIContainerId = m.GLIContainerId \
        and c.GLIContainerId=%d " % self.GLIContainerId or 0

    resSQL = self.Config.CreateSQL(sql).rawresult     
    return resSQL.GetFieldValueAt(0) or 0
      
  def GenerateGLContainer(self):
    oGLIContainer = self.Helper.CreatePObject('GLInterfaceContainer')
    oGLIContainer.GLIContainerName = self.CPIACatName
    self.GLIContainerId = oGLIContainer.GLIContainerId
      
  def GenerateGLInterface(self):
    if self.GLIContainerId in ['',0,None] :
      self.GenerateGLContainer()
      
    DefaultGL = {
      'CPIA_ACC'  : ('Akun BIAYA Dibayar Dimuka','11601'),
    }           
      
    for kode,item in DefaultGL.items():
      oGLIMember = self.Helper.GetObjectByNames(
        'GLInterfaceMember',
        { 'GLIMemberCode' : kode ,
          'GLIContainerId' : self.GLIContainerId
        }
      )
      if oGLIMember.isnull :
        oGLIMember = self.Helper.CreatePObject('GLInterfaceMember')
        oGLIMember.GLIContainerId = self.GLIContainerId
        oGLIMember.GLIMemberCode = kode
        oGLIMember.Description = item[0]
        oGLIMember.AccountCode = item[1]
        
class CostPaidInAdvance(AmortizedCost):
  # static variable
  pobject_classname = 'CostPaidInAdvance'

  def OnCreate(self):
    self.TagCode = 'BDD'
    DepreciableAsset.OnCreate(self)
  
  def SetContract(self, aContractNo, aContractEndDate):
    if aContractEndDate <= self.GetAsTDateTime('OpeningDate'):
      raise 'SetContract', 'Tanggal berakhir kontrak tidak valid'
      
    self.HasContract = 'T'
    self.ContractNo = aContractNo
    self.TanggalAkhirPenyusutan = aContractEndDate
    
    libUtils = self.Config.ModLibUtils
    y, m, d = self.OpeningDate[:3]
    y2, m2, d2 = libUtils.DecodeDate(aContractEndDate)
    
    self.LifeTime = (y2-y)*12 + (m2-m)
    self.TanggalProsesBerikut = libUtils.EncodeDate(y, m, 25)
    if d > 25:
      self.TanggalProsesBerikut = libUtils.IncMonth(self.TanggalProsesBerikut, 1)
    else:
      self.LifeTime += 1
  
  def SetNoContract(self):
    self.HasContract = 'F'
    libUtils = self.Config.ModLibUtils
    y, m, d = libUtils.DecodeDate(libUtils.Now())
    self.TanggalAkhirPenyusutan = libUtils.EncodeDate(y, 12, 25)
    if d > 25:
      if m == 12:
        self.LifeTime = 12
        self.TanggalProsesBerikut = libUtils.EncodeDate(y+1, 1, 25)
        self.TanggalAkhirPenyusutan = libUtils.EncodeDate(y+1, 12, 25)
      else:
        self.LifeTime = 12 - m
        self.TanggalProsesBerikut = libUtils.EncodeDate(y, m+1, 25)
      #--if.else
    else:
      self.LifeTime = 12 - m + 1
      self.TanggalProsesBerikut = libUtils.EncodeDate(y, m, 25)
    #-- if.else
  
  def GetAccountInterface(self):
    return self.LCPIACategory.LGLIContainer.GetAccountInterface('CPIA_ACC').AccountCode
    

class Inventory(FinancialAccount):
  # static variable
  pobject_classname = 'Inventory'
  
class AssetCategory(pobject.PObject):
  # static variable
  pobject_classname = 'AssetCategory'
  pobject_keys = ['AssetCategoryId']
  
  def OnCreate(self):
    #self.GenerateGLContainer()
    pass
    
  def GLInterfaceExist(self):  
    sql = "select count(*) from \
        GLInterfaceContainer c ,GLInterfaceMember m \
        where c.GLIContainerId = m.GLIContainerId \
        and c.GLIContainerId=%d " % self.GLIContainerId or 0

    resSQL = self.Config.CreateSQL(sql).rawresult     
    return resSQL.GetFieldValueAt(0) or 0
  
  def GenerateGLContainer(self):
    oGLIContainer = self.Helper.CreatePObject('GLInterfaceContainer')
    oGLIContainer.GLIContainerName = self.AssetCategoryName
    self.GLIContainerId = oGLIContainer.GLIContainerId
      
  def GenerateGLInterface(self):
    if self.GLIContainerId in ['',0,None] :
      self.GenerateGLContainer()
      
    DefaultGL = {
      'PROFIT_ACC'  : ('PENDAPATAN LABA PENJUALAN','5520903'),
      'LOST_ACC'  : ('BEBAN RUGI PENJUALAN','5520903'),
      'MAN_ACC'  : ('AKUN DANA TERMANFAATKAN',''),
      'MANSAL_ACC'  : ('AKUN DANA TERMANFAATKAN TERSALURKAN',''),
    }     
    
    if self.AssetCategoryCode == 'BT' :
      DefaultGL['ASSET_ACC'] = ('AKUN ASSET','1220202')
      DefaultGL['DEPR_ACC'] = ('AKUN PENYUSUTAN','1220401')
      DefaultGL['COST_ACC'] = ('AKUN BIAYA','5520801')
      DefaultGL['ASSET_LIAB'] = ('AKUN ASSET HUTANG YAD','2130302')
      DefaultGL['ASSETFROMAMIL'] = ('BEBAN BIAYA AMIL ATAS ASSET','5530102')
    elif self.AssetCategoryCode == 'BTT' :
      DefaultGL['ASSET_ACC'] = ('AKUN ASSET','1220102')
      DefaultGL['DEPR_ACC'] = ('AKUN PENYUSUTAN','1220301')
      DefaultGL['COST_ACC'] = ('AKUN BIAYA','5520801')
      DefaultGL['ASSET_LIAB'] = ('AKUN ASSET HUTANG YAD','2130302')
      DefaultGL['ASSETFROMAMIL'] = ('BEBAN BIAYA AMIL ATAS ASSET','5530102')
    elif self.AssetCategoryCode == 'KT' :
      DefaultGL['ASSET_ACC'] = ('AKUN ASSET','1220203')
      DefaultGL['DEPR_ACC'] = ('AKUN PENYUSUTAN','1220402')
      DefaultGL['COST_ACC'] = ('AKUN BIAYA','5520802')
      DefaultGL['ASSET_LIAB'] = ('AKUN ASSET HUTANG YAD','2130303')
      DefaultGL['ASSETFROMAMIL'] = ('BEBAN BIAYA AMIL ATAS ASSET','5530103')
    elif self.AssetCategoryCode == 'KTT' :
      DefaultGL['ASSET_ACC'] = ('AKUN ASSET','1220103')
      DefaultGL['DEPR_ACC'] = ('AKUN PENYUSUTAN','1220302')
      DefaultGL['COST_ACC'] = ('AKUN BIAYA','5520802')
      DefaultGL['ASSET_LIAB'] = ('AKUN ASSET HUTANG YAD','2130303')
      DefaultGL['ASSETFROMAMIL'] = ('BEBAN BIAYA AMIL ATAS ASSET','5530103')
    elif self.AssetCategoryCode == 'PT' :
      DefaultGL['ASSET_ACC'] = ('AKUN ASSET','1220204')
      DefaultGL['DEPR_ACC'] = ('AKUN PENYUSUTAN','1220403')
      DefaultGL['COST_ACC'] = ('AKUN BIAYA','5520803')
      DefaultGL['ASSET_LIAB'] = ('AKUN ASSET HUTANG YAD','2130304')
      DefaultGL['ASSETFROMAMIL'] = ('BEBAN BIAYA AMIL ATAS ASSET','5530104')
    elif self.AssetCategoryCode == 'PTT' :
      DefaultGL['ASSET_ACC'] = ('AKUN ASSET','1220104')
      DefaultGL['DEPR_ACC'] = ('AKUN PENYUSUTAN','1220303')
      DefaultGL['COST_ACC'] = ('AKUN BIAYA','5520803')
      DefaultGL['ASSET_LIAB'] = ('AKUN ASSET HUTANG YAD','2130304')
      DefaultGL['ASSETFROMAMIL'] = ('BEBAN BIAYA AMIL ATAS ASSET','5530104')
    elif self.AssetCategoryCode == 'TT' :
      DefaultGL['ASSET_ACC'] = ('AKUN ASSET','1220201')
      DefaultGL['DEPR_ACC'] = ('AKUN PENYUSUTAN','')
      DefaultGL['COST_ACC'] = ('AKUN BIAYA','')
      DefaultGL['ASSET_LIAB'] = ('AKUN ASSET HUTANG YAD','2130302')
      DefaultGL['ASSETFROMAMIL'] = ('BEBAN BIAYA AMIL ATAS ASSET','5530101')
    elif self.AssetCategoryCode == 'TTT' :
      DefaultGL['ASSET_ACC'] = ('AKUN ASSET','1220101')
      DefaultGL['DEPR_ACC'] = ('AKUN PENYUSUTAN','')
      DefaultGL['COST_ACC'] = ('AKUN BIAYA','')
      DefaultGL['ASSET_LIAB'] = ('AKUN ASSET HUTANG YAD','2130302')
      DefaultGL['ASSETFROMAMIL'] = ('BEBAN BIAYA AMIL ATAS ASSET','5530101')
    # endif

    for kode,item in DefaultGL.items():
      oGLIMember = self.Helper.GetObjectByNames(
        'GLInterfaceMember',
        { 'GLIMemberCode' : kode ,
          'GLIContainerId' : self.GLIContainerId
        }
      )
      if oGLIMember.isnull :
        oGLIMember = self.Helper.CreatePObject('GLInterfaceMember')
        oGLIMember.GLIContainerId = self.GLIContainerId
        oGLIMember.GLIMemberCode = kode
        oGLIMember.Description = item[0]
        oGLIMember.AccountCode = item[1]
#       oAccount = self.Helper.GetObject('Account',oGLInt.item[1])
#       if oAccount.isnull : '','Account Code %s Tidak Ditemukan' % oGLIMember.AccountCode
#       oGLIMember.AccountName = oAccount.Account_Name
          
    # end for  
