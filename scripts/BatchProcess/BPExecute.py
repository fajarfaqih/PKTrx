# L_TestScript.py
# script untuk test runtime POD

import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.util.logsvrclient as lclib
import sys

# globals
gid = -1
oLogger = lclib.LogSvrClient(None, 'localhost', 2423, 'dafapp')

def DoProcess(config,ScenarioCode,Params):

  helper = phelper.PObjectHelper(config)
   
  app = config.AppObject
  app.ConCreate('BP')
  app.ConWriteln('Mulai Proses Skenario %s ' % ScenarioCode ,'BP')
    
  oBPScenario = helper.GetObjectByNames("BPScenario", {"BPScenarioCode" : ScenarioCode})  
  oBPScenario.Execute(app , Params)
  
  
def DAFLongScriptMain(config, parameter, pid, monfilename):
  global gid, oLogger
  
  gid = pid
  helper = phelper.PObjectHelper(config)    
  oLogger.writeLog('pid:%d. Proses depresiasi di mulai...' % gid)
  Proses(helper)
  oLogger.writeLog('pid:%d. Proses depresiasi selesai...' % gid)

  return 1

def DAFScriptMain(config,params,returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],    
  )

  helper = phelper.PObjectHelper(config)
  param = params.FirstRecord
  Month = param.DeprMonth
  Year = param.DeprYear
  
  try:
    Proses(helper,Month,Year)
  except:
    status.Is_Err =1
    status.Err_Message = str(sys.exc_info()[1])
  # end try except  

  return 1
  
def CreateBatch(helper, branchCode,DeprDate):
  config = helper.Config
  
  config.BeginTransaction()
  try:
    oBatch = helper.CreatePObject('TransactionBatch')
    oBatch.BranchCode   = branchCode
    oBatch.Inputer      = config.SecurityContext.InitUser
    oBatch.Description  = 'Depresiasi Aktiva Tetap'
    oBatch.BatchDate = DeprDate
    oBatch.BatchTag = 'SYS'
    
    config.Commit()
  except:
    config.Rollback()
    raise
  
  config.BeginTransaction()
  try:
    oBatch.PostToAccounting()
    
    config.Commit()
  except:
    config.Rollback()
    raise
  
  return oBatch

def Proses(helper,Month,Year):
  global gid, oLogger
  
  config = helper.Config
  app = config.AppObject
  app.ConCreate('DEPR')
  
#   if strDate == None:
#     aParam = helper.GetObject('ParameterGlobal', 'DEPR_DATE')
#     #sNow = config.FormatDateTime('YYYY-MM-DD', config.Now())
#     sNow = aParam.GetFormatted('YYYY-MM-DD')
#   else:
#     sNow = strDate
  strDeprDate = "%s-%s-25" % (str(Year),str(Month).zfill(2))
  intDeprDate = config.ModDateTime.EncodeDate(Year,Month,25)
   
  res = config.CreateSQL("\
    select accountno from depreciableasset where deprstate='A' and \
      tanggalprosesberikut <= '%s' \
  " % strDeprDate).rawresult
  
  ListBatch = {}
  while not res.Eof:
    oAccount = helper.GetObject(
      'DepreciableAsset', res.accountno
    ).CastToLowestDescendant()
    
    branchCode = oAccount.BranchCode
    if ListBatch.has_key(branchCode):
      oBatch = ListBatch[branchCode]
    else:
      oBatch = CreateBatch(helper, branchCode,intDeprDate)
      ListBatch[branchCode] = oBatch
    #-- if.else
    app.ConWriteln('Cek Depresiasi Rekening Aktiva : ' + oAccount.AccountNo,'DEPR')
    if not oAccount.CheckForDepreciation():
      res.Next()
      continue
    #--if

    #oLogger.writeLog('Depresiasi Rekening Aktiva : ' + oAccount.accountno)
    app.ConWriteln('Depresiasi Rekening Aktiva : ' + oAccount.AccountNo,'DEPR')
    config.BeginTransaction()
    try:
      oTran = oBatch.NewTransaction('DEPR')
      
      aRate = 1.0
      
      oTran.Inputer      = 'SYSTEM'
      oTran.BranchCode   = branchCode
      oTran.ReferenceNo  = oAccount.accountno
      oTran.CurrencyCode = oAccount.CurrencyCode
      oTran.Rate         = aRate
      oTran.ActualDate   = oBatch.BatchDate #int(config.Now())
      
      nominal = oAccount.Depreciation(intDeprDate)
      oTran.Amount = nominal
      
      oItem = oTran.CreateAccountTransactionItem(oAccount)
      oItem.SetMutation('C', nominal, aRate)
      if oAccount.IsA('FixedAsset'):
        oTran.Description  = 'Depresiasi Aktiva Tetap'
        oItem.Description = 'Depresiasi Aktiva Tetap'
        oItem.SetJournalParameter('DA04')
        oItem.AccountCode = oAccount.GetDeprAccount()
      else: # IsA('CostPaidInAdvance')
        oTran.Description  = 'Amortisasi BDD'
        oItem.Description = 'Amortisasi BDD'
        oItem.SetJournalParameter('BDD02')
        oItem.AccountCode = oAccount.CostAccountNo
      #-- if.else
      
      oTran.GenerateTransactionNumber('000')
      #oTran.SaveInbox(params)
      oTran.AutoApproval()
      
      config.Commit()
    except:
      config.Rollback()
      raise
    #-- try..except
    
    res.Next()  
  #-- while        
