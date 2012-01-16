import sys

def FormSetDataEx(uideflist,params):
  config = uideflist.Config
  
  if params.DatasetCount != 0 :
    recParam = params.FirstRecord
    FilterName = recParam.FilterName
    InvestmentType = recParam.InvestmentType
    
    if InvestmentType == 'E' :
      GenerateListDataEmployee(config, uideflist.uipInvestmentE, FilterName)
    else : # InvestmentType == 'X'
      GenerateListDataNonEmployee(config, uideflist.uipInvestmentNE, FilterName)
    
def ConvertDateTupleToFloat(config, tupDate):
  return config.ModLibUtils.EncodeDate(tupDate[0], tupDate[1], tupDate[2])

def GenerateListDataEmployee(config, uipInvestment, FilterName):
  sSQL = " \
    SELECT B.EMPLOYEEID, \
        B.EMPLOYEENAME, \
        D.ACCOUNTNAME, \
        D.OPENINGDATE, \
        A.INVESTMENTAMOUNT, \
        A.ACCOUNTNO, \
        D.BALANCE, \
        A.FUNDENTITY, \
        A.ACCOUNTNO \
    FROM \
      INVESTMENT A, \
      VEMPLOYEE B, \
      ACCOUNTRECEIVABLE C, \
      FINANCIALACCOUNT D \
    WHERE A.INVESTMENTTYPE = 'E' AND \
      A.EMPLOYEEID = B.EMPLOYEEID AND \
      A.AccountNo = C.AccountNo AND \
      C.AccountNo = D.AccountNo AND \
      upper( B.EMPLOYEENAME ) like '%%%s%%' \
    " % ( FilterName )

  res = config.CreateSQL(sSQL).rawresult

  uipInvestment = uipInvestment.Dataset
  while not res.Eof:
    rec = uipInvestment.AddRecord()
    rec.SetFieldByName('LEmployee.EmployeeId', res.EmployeeId)
    rec.SetFieldByName('LEmployee.EmployeeName', res.EmployeeName)
    rec.OpeningDate = ConvertDateTupleToFloat(config,res.OpeningDate)
    rec.InvestmentAmount = res.InvestmentAmount
    rec.AccountNo = res.AccountNo
    rec.Balance = res.Balance
    rec.FundEntity = res.FundEntity
    rec.AccountNo = res.AccountNo
    res.Next()
  # end while

def GenerateListDataNonEmployee(config, uipInvestment, FilterName):
  sSQL = " \
    SELECT B.INVESTEEID, \
        B.INVESTEENAME, \
        D.ACCOUNTNAME, \
        D.OPENINGDATE, \
        A.INVESTMENTAMOUNT, \
        A.ACCOUNTNO, \
        D.BALANCE, \
        A.FUNDENTITY, \
        A.ACCOUNTNO \
    FROM \
      INVESTMENT A, \
      INVESTEE B, \
      ACCOUNTRECEIVABLE C, \
      FINANCIALACCOUNT D \
    WHERE A.INVESTMENTTYPE = 'N' AND \
      A.INVESTEEID = B.INVESTEEID AND \
      A.AccountNo = C.AccountNo AND \
      C.AccountNo = D.AccountNo AND \
      upper( B.INVESTEENAME ) like '%%%s%%'  \
    " % ( FilterName )

  res = config.CreateSQL(sSQL).rawresult
  
  uipInvestment = uipInvestment.Dataset
  while not res.Eof:
    rec = uipInvestment.AddRecord()
    rec.SetFieldByName('LInvestee.InvesteeId', res.InvesteeId)
    rec.SetFieldByName('LInvestee.InvesteeName', res.InvesteeName)
    rec.OpeningDate = ConvertDateTupleToFloat(config,res.OpeningDate)
    rec.InvestmentAmount = res.InvestmentAmount
    rec.AccountNo = res.AccountNo
    rec.Balance = res.Balance
    rec.FundEntity = res.FundEntity
    rec.AccountNo = res.AccountNo
    res.Next()
  # end while


def OnSetData(sender):
  pass
  
