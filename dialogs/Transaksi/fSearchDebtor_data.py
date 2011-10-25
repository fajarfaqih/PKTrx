import sys

def FormSetDataEx(uideflist,params):
  config = uideflist.Config

  # Set List Data Debtor
  strSQL = GetSQLDebtor(config)
  resSQL = config.CreateSQL(strSQL).RawResult
  resSQL.First()

  dsDebtor = uideflist.uipDebtor.Dataset
  while not resSQL.Eof :
    rec = dsDebtor.AddRecord()
    rec.DebtorId = resSQL.DebtorId
    rec.DebtorName = resSQL.DebtorName

    resSQL.Next()
  # end while

  # Set List Data Employee
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
    strSQL += " and upper(employeename) like '%%%s%%' " % (Name.upper())
  strSQL += " order by employeename "
  return strSQL


def GetSQLDebtor(config,Name=None):

  BranchCode = config.SecurityContext.GetUserInfo()[4]
  strSQL = "select DebtorId,DebtorName from ExternalDebtor where BranchCode='%s'" % BranchCode

  if Name != None :
    strSQL += " and upper(DebtorName) like '%%%s%%' " % (Name.upper())
  strSQL += " order by DebtorName "
  return strSQL


  
def GetDataDebtor(config,params,returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
  )

  dsDebtor = returns.AddNewDatasetEx(
      'ListDebtor',
    ';'.join([
      'DebtorId: integer',
      'DebtorName: string',
      'BranchCode: string',
      'BranchName: string',
    ])
  )

  try:
    NameFilter = params.FirstRecord.NameFilter

    strSQL = GetSQLDebtor(config,NameFilter)
    resSQL = config.CreateSQL(strSQL).RawResult
    resSQL.First()

    while not resSQL.Eof :
      rec = dsDebtor.AddRecord()
      rec.DebtorId = resSQL.DebtorId
      rec.DebtorName = resSQL.DebtorName
      
      resSQL.Next()
    # end while

  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
    
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
