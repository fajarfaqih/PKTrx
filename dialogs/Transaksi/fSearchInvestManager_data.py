import sys

def FormSetDataEx(uideflist,params):
  config = uideflist.Config

  strSQL = GetSQLManager(config)
  resSQL = config.CreateSQL(strSQL).RawResult
  resSQL.First()

  dsManager = uideflist.uipInvestManager.Dataset
  while not resSQL.Eof :
    rec = dsManager.AddRecord()
    rec.ManagerId = resSQL.ManagerId
    rec.ManagerName = resSQL.ManagerName

    resSQL.Next()
  # end while

def GetSQLManager(config,Name=None):

  BranchCode = config.SecurityContext.GetUserInfo()[4]
  strSQL = "select ManagerId,ManagerName from InvestmentManager where BranchCode='%s'" % BranchCode

  if Name != None :
    strSQL += " and upper(ManagerName) like '%%%s%%' " % (Name)
  strSQL += " order by ManagerName "
  return strSQL


  
def GetDataManager(config,params,returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
  )

  dsManager = returns.AddNewDatasetEx(
      'ListManager',
    ';'.join([
      'ManagerId: integer',
      'ManagerName: string',
      'BranchCode: string',
      'BranchName: string',
    ])
  )

  try:
    NameFilter = params.FirstRecord.NameFilter

    strSQL = GetSQLManager(config,NameFilter)
    resSQL = config.CreateSQL(strSQL).RawResult
    resSQL.First()

    while not resSQL.Eof :
      rec = dsManager.AddRecord()
      rec.ManagerId = resSQL.ManagerId
      rec.ManagerName = resSQL.ManagerName
      
      resSQL.Next()
    # end while

  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
