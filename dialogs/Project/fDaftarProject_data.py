import sys

def FormSetDataEx(uideflist,params):
  config = uideflist.Config
  
  rec = uideflist.uipFilter.Dataset.AddRecord()
  
  SecContext = config.SecurityContext
  
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])

def GetDataProject(config,parameters,returns):
  status = returns.CreateValues(
    ['IsErr',0],
    ['ErrMessage','']
  )

  dsData = returns.AddNewDatasetEx(
      'MasterData',
    ';'.join([
      'ProductCode: string',
      'ProductName: string',
      'Description: string',
      'ProductNameParent: string',
      'Rate: float',
      'PercentageOfAmilFunds: float',
      'Level: integer',
      'IsDetail: string',
      'Status: string',
    ])
  )

  try:
    dStatus = {'A' : 'Active','N' : 'Not Active'}
    strSQL = " \
      SELECT A.ACCOUNTNO, \
        D.ACCOUNTNAME, \
        C.PRODUCTNAME, \
        A.STARTDATE, \
        A.FINISHDATE, \
        A.BUDGETAMOUNT, \
        F.Enum_Description, \
        A.ACCOUNTNO, \
        D.STATUS \
        FROM \
        PROJECTACCOUNT A, \
        PRODUCTACCOUNT B, \
        PRODUCT C, \
        FINANCIALACCOUNT D, \
        FINANCIALACCOUNT E LEFT OUTER JOIN Enum_Varchar F ON \
        ((E.STATUS = F.Enum_Value AND F.Enum_Name = 'eStatus')) \
        WHERE A.AccountNo = B.AccountNo AND \
        B.PRODUCTID = C.PRODUCTID AND \
        B.AccountNo = D.AccountNo AND \
        D.ACCOUNTNO = E.ACCOUNTNO AND \
        (((C.STATUS = 'A' OR \
        C.STATUS = 'N')) AND D.BRANCHCODE = '001') \
        ORDER BY \
        A.ACCOUNTNO ASC "

    oRes = config.CreateSQL(strSQL).RawResult
    oRes.First()
    while not oRes.Eof:
      recData = dsData.AddRecord()
      recData.ProductCode = oRes.AccountNo
      recData.ProductName = oRes.AccountName
      recData.Description = oRes.AccountName
      recData.ProductNameParent = oRes.PRODUCTNAME
      recData.Status = dStatus[oRes.Status]

      oRes.Next()
    # end while

  except:
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])
