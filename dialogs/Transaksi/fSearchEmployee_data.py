import sys

def FormSetDataEx(uideflist,params):
  config = uideflist.Config

  strSQL = GetSQLEmployee(config)
  resSQL = config.CreateSQL(strSQL).RawResult
  resSQL.First()

  dsEmployee = uideflist.uipEmployee.Dataset
  while not resSQL.Eof :
    rec = dsEmployee.AddRecord()
    rec.EmployeeId = resSQL.EmployeeId
    rec.EmployeeName = resSQL.EmployeeName

    resSQL.Next()
  # end while

def GetSQLEmployee(config,Name=None):
  BranchId = int(config.SecurityContext.GetUserInfo()[2])
  strSQL = "select EmployeeId,EmployeeName from vemployee where branch_id=%d" % BranchId


  if Name != None :
    strSQL += " and upper(employeename) like '%%%s%%' " % (Name)
  strSQL += " order by employeename "
  return strSQL


  
def GetDataEmployee(config,params,returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
  )

  dsEmployee = returns.AddNewDatasetEx(
      'ListEmployee',
    ';'.join([
      'EmployeeId: integer',
      'EmployeeName: string',
      'BranchId: integer',
      'BranchName: string',
    ])
  )

  try:
    NameFilter = params.FirstRecord.NameFilter

    strSQL = GetSQLEmployee(config,NameFilter)
    resSQL = config.CreateSQL(strSQL).RawResult
    resSQL.First()

    while not resSQL.Eof :
      rec = dsEmployee.AddRecord()
      rec.EmployeeId = resSQL.EmployeeId
      rec.EmployeeName = resSQL.EmployeeName
      
      resSQL.Next()
    # end while

  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
