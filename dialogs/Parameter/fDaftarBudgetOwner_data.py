import sys
import com.ihsan.foundation.pobjecthelper as phelper

def GetDataBudgetOwner(config,parameters,returns):
  status = returns.CreateValues(
    ['IsErr',0],
    ['ErrMessage','']
  )

  dsData = returns.AddNewDatasetEx(
      'MasterData',
    ';'.join([
      'OwnerCode: string',
      'OwnerName: string',
      'Level: integer',
      'Is_Detail: string',
    ])
  )

  try:
    helper = phelper.PObjectHelper(config)
    corporate = helper.CreateObject('Corporate')

    dStatus = {'A' : 'Active','N' : 'Not Active'}
    strSQL = "select * from BudgetOwner order by OwnerCode"

    oRes = config.CreateSQL(strSQL).RawResult
    oRes.First()
    dictCabang = {}
    while not oRes.Eof:
      recData = dsData.AddRecord()
      recData.OwnerCode = oRes.OwnerCode
      recData.OwnerName = oRes.OwnerName
      recData.Level = oRes.Level
      recData.Is_Detail = oRes.Is_Detail

      oRes.Next()
    # end while

  except:
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])
