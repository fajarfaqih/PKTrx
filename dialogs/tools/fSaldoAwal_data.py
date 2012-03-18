import com.ihsan.foundation.pobjecthelper as phelper
import sys
import pyFlexcel
import os

def FormSetDataEx(uideflist,params):
  config = uideflist.config

  rec = uideflist.uipData.Dataset.AddRecord()

  # Set Default Branch Info
  UserInfo = config.SecurityContext.GetUserInfo()
  rec.UserId = config.SecurityContext.InitUser.upper()
  rec.BranchCode = str(UserInfo[4])
  rec.BranchName = str(UserInfo[5])
  rec.HeadOfficeCode = config.SysVarIntf.GetStringSysVar('OPTION','HeadOfficeCode')

def UploadData(config,params,returns):
  status = returns.CreateValues(
    ['Is_Err',0],['Err_Message','']
  )

  try :
    helper = phelper.PObjectHelper(config)
    header = params.HeaderData.GetRecord(0)
    
    oService = helper.LoadScript('Transaction.BeginningBalance')
    
    if header.AccountType == 1 :
      is_err,err_message = oService.CashAccount(config ,params)
    elif header.AccountType == 2 :
      is_err,err_message = oService.Program(config ,params)
    elif header.AccountType == 3 :
      is_err,err_message = oService.Project(config ,params)
    elif header.AccountType == 4 :
      is_err,err_message = oService.EmployeeAR(config ,params)
    elif header.AccountType == 5 :
      is_err,err_message = oService.ExternalAR(config ,params)
    elif header.AccountType == 6 :
      is_err,err_message = oService.EmployeeInvestment(config ,params)
    elif header.AccountType == 7 :
      is_err,err_message = oService.ExternalInvestment(config ,params)
    elif header.AccountType == 8 :
      is_err,err_message = oService.FixedAsset(config ,params)
    elif header.AccountType == 9 :
      is_err,err_message = oService.AmortizedCost(config ,params)

    # end if elif

    if is_err == 1 : raise '',err_message
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
    
def GetTemplate(config,params,returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
    ['BranchName','']
  )
  param = params.FirstRecord
  try :
    status.BranchName = param.GetFieldByName('LBranch.BranchName') #config.SecurityContext.GetUserInfo()[5]
    BranchCode = param.GetFieldByName('LBranch.BranchCode')
    if param.AccountType == 1 :
      GetTemplateCashAccount(config, BranchCode, returns)
    elif param.AccountType == 2 :
      GetTemplateProgram(config, returns)
    elif param.AccountType == 3 :
      GetTemplateProject(config, returns)
    elif param.AccountType == 4 :
      GetListEmployee(config, returns)
    elif param.AccountType == 5:
      GetListExternalDebtor(config, returns)
    elif param.AccountType == 6:
      GetListEmployeeInvestment(config, returns)
    elif param.AccountType == 7:
      GetListInvestee(config, returns)
    elif param.AccountType == 8:
      GetListFixedAsset(config, returns)
    elif param.AccountType == 9:
      GetAmortizedCost(config, returns)

  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
    
def GetTemplateCashAccount( config, BranchCode, returns):
  helper = phelper.PObjectHelper(config)
  
  #BranchCode = config.SecurityContext.GetUserInfo()[4]
  
  dsListAccount = returns.AddNewDatasetEx(
      'ListAccount',
    ';'.join([
      'AccountNo: string',
      'AccountName: string',
      'Currency:string',
      'Balance: float',
      'Rate: float',
    ])
  )
  
  sOQL = "select from CashAccount \
            [BranchCode=:BranchCode] \
            ( AccountNo, \
              AccountName, \
              CurrencyCode, \
              LCurrency.Short_Name, \
              CashAccountType, \
              self) then order by desc CashAccountType,AccountNo;"

  oql = config.OQLEngine.CreateOQL(sOQL)
  oql.SetParameterValueByName('BranchCode', BranchCode)

  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  while not ds.Eof:
    recAccount = dsListAccount.AddRecord()
    recAccount.AccountNo = ds.AccountNo
    recAccount.AccountName = ds.AccountName
    recAccount.Currency = '%s - %s' % (ds.CurrencyCode,ds.Short_Name)

    # Cek jika sudah pernah ada saldo awal
    TransactionNo = 'BB-CB-%s-%s' % (ds.CurrencyCode,BranchCode)
    oTranItem = helper.GetObjectByNames('AccountTransactionItem',
        {'AccountNo' : ds.AccountNo ,
         'LTransaction.TransactionNo' : TransactionNo ,
         'LTransaction.TransactionCode' : 'TB' }
     )
     
    if oTranItem.isnull :
      recAccount.Balance = 0.0
      recAccount.Rate = 1.0
    else :
      recAccount.Balance = oTranItem.Amount
      recAccount.Rate = oTranItem.Rate
    # end if
    
    ds.Next()
  # end while
  
def GetTemplateProgram( config, returns):
  BranchCode = config.SecurityContext.GetUserInfo()[4]
  dsListAccount = returns.AddNewDatasetEx(
      'ListAccount',
    ';'.join([
      'AccountNo: string',
      'AccountName: string',
      'Currency:string',
      'Balance: float',
    ])
  )

  sOQL = "select from ProductAccount \
            [BranchCode=:BranchCode and \
             LProduct.ProductType = 'G'] \
            ( AccountNo, \
              AccountName, \
              CurrencyCode, \
              LCurrency.Short_Name, \
              self) then order by AccountNo;"

  oql = config.OQLEngine.CreateOQL(sOQL)
  oql.SetParameterValueByName('BranchCode', BranchCode)

  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  while not ds.Eof:
    recAccount = dsListAccount.AddRecord()
    recAccount.AccountNo = ds.AccountNo
    recAccount.AccountName = ds.AccountName
    recAccount.Currency = '%s - %s' % (ds.CurrencyCode,ds.Short_Name)
    recAccount.Balance = 0.0
    ds.Next()
  # end while
  
def GetTemplateProject( config, returns):
  BranchCode = config.SecurityContext.GetUserInfo()[4]
  dsListAccount = returns.AddNewDatasetEx(
      'ListAccount',
    ';'.join([
      'AccountNo: string',
      'AccountName: string',
      'SponsorId: integer',
      'SponsorName: string',
      'Currency:string',
      'Balance: float',
    ])
  )

  helper = phelper.PObjectHelper(config)
  sOQL = "select from ProjectAccount \
            [BranchCode=:BranchCode] \
            ( AccountNo, \
              AccountName, \
              CurrencyCode, \
              LCurrency.Short_Name, \
              self) then order by AccountNo;"

  oql = config.OQLEngine.CreateOQL(sOQL)
  oql.SetParameterValueByName('BranchCode', BranchCode)

  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  while not ds.Eof:
    recAccount = dsListAccount.AddRecord()
    recAccount.AccountNo = ds.AccountNo
    recAccount.AccountName = ds.AccountName
    recAccount.Currency = '%s - %s' % (ds.CurrencyCode,ds.Short_Name)
    recAccount.Balance = 0.0

    sSQL = "select * from ProjectSponsor where AccountNo ='%s'" % ds.AccountNo
    dsSponsor = config.CreateSQL(sSQL).rawresult
    if not dsSponsor.Eof :
      oDonor = helper.CreateObject('ExtDonor')
      oDonor.GetData(dsSponsor.SponsorId)
      recAccount.SponsorId = dsSponsor.SponsorId
      recAccount.SponsorName = oDonor.full_name

    ds.Next()
  # end while
  
def GetListEmployee( config, returns):
  BranchCode = config.SecurityContext.GetUserInfo()[4]
  BranchId = int(config.SecurityContext.GetUserInfo()[2])
  dsListAccount = returns.AddNewDatasetEx(
      'ListAccount',
    ';'.join([
      'AccountNo: integer',
      'AccountName: string',
      'Balance: float',
    ])
  )

  sSQL = "select * from public.sdm_employee where branch_id=%d order by full_name" % BranchId

  ds = config.CreateSQL(sSQL).rawresult

  while not ds.Eof:
    recAccount = dsListAccount.AddRecord()
    recAccount.AccountNo = ds.id
    recAccount.AccountName = ds.full_name
    recAccount.Balance = 0.0
    ds.Next()
  # end while
  
def GetListExternalDebtor( config, returns):
  BranchCode = config.SecurityContext.GetUserInfo()[4]
  BranchId = int(config.SecurityContext.GetUserInfo()[2])
  dsListAccount = returns.AddNewDatasetEx(
      'ListAccount',
    ';'.join([
      'AccountNo: integer',
      'AccountName: string',
      'Balance: float',
    ])
  )

  sSQL = "select * from externaldebtor where branchcode='%s' order by debtorname" % BranchCode
  
  ds = config.CreateSQL(sSQL).rawresult
  
  while not ds.Eof:
    recAccount = dsListAccount.AddRecord()
    recAccount.AccountNo = ds.debtorid
    recAccount.AccountName = ds.debtorname
    recAccount.Balance = 0.0
    ds.Next()
  # end while
  
def GetListInvestmentCategory(config):

  sSQLInvestCat = "select * from investmentcategory "
  dsInvestCat = config.CreateSQL(sSQLInvestCat).rawresult
  ListInvestmentCat = {}
  while not dsInvestCat.Eof:
    ListInvestmentCat[dsInvestCat.investmentcatcode] = dsInvestCat.investmentcatname
    dsInvestCat.Next()

  return ListInvestmentCat

def GetListEmployeeInvestment( config, returns):

  BranchCode = config.SecurityContext.GetUserInfo()[4]
  BranchId = int(config.SecurityContext.GetUserInfo()[2])
  dsListAccount = returns.AddNewDatasetEx(
      'ListAccount',
    ';'.join([
      'AccountNo: integer',
      'AccountName: string',
      'CatCode: string',
      'CatName: string',
      'InvestAmount: float',
      'Balance: float',
      'StartDate: datetime',
      'LifeTime: integer',
      'Nisbah: float',
    ])
  )

  sSQL = "select * from public.sdm_employee where branch_id=%d order by full_name" % BranchId
  ds = config.CreateSQL(sSQL).rawresult
  
  StartDate = config.ModLibUtils.EncodeDate(2011,1,1)
  ListInvestmentCat = GetListInvestmentCategory(config)
  while not ds.Eof:
    recAccount = dsListAccount.AddRecord()
    recAccount.AccountNo = ds.id
    recAccount.AccountName = ds.full_name
    recAccount.CatCode = 'IL001'
    recAccount.CatName = ListInvestmentCat['IL001']
    recAccount.Balance = 0.0
    recAccount.InvestAmount = 0.0
    recAccount.StartDate = StartDate
    recAccount.LifeTime = 0
    recAccount.Nisbah = 0.0
    
    ds.Next()
  # end while
  
def GetListInvestee( config, returns):

  BranchCode = config.SecurityContext.GetUserInfo()[4]
  BranchId = int(config.SecurityContext.GetUserInfo()[2])
  dsListAccount = returns.AddNewDatasetEx(
      'ListAccount',
    ';'.join([
      'AccountNo: integer',
      'AccountName: string',
      'CatCode: string',
      'CatName: string',
      'InvestAmount: float',
      'Balance: float',
      'StartDate: datetime',
      'LifeTime: integer',
      'Nisbah: float',
    ])
  )

  sSQL = "select * from investee where branchcode='%s' order by investeename" % BranchCode
  ds = config.CreateSQL(sSQL).rawresult

  StartDate = config.ModLibUtils.EncodeDate(2011,1,1)
  ListInvestmentCat = GetListInvestmentCategory(config)
  while not ds.Eof:
    recAccount = dsListAccount.AddRecord()
    recAccount.AccountNo = ds.investeeid
    recAccount.AccountName = ds.investeename
    recAccount.CatCode = 'IS001'
    recAccount.CatName = ListInvestmentCat['IS001']
    recAccount.Balance = 0.0
    recAccount.InvestAmount = 0.0
    recAccount.StartDate = StartDate
    recAccount.LifeTime = 0
    recAccount.Nisbah = 0.0

    ds.Next()
  # end while

def GetListFixedAsset( config, returns):
  return

def GetAmortizedCost( config, returns):
  return
