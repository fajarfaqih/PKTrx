import com.ihsan.foundation.pobjecthelper as phelper
import sys

def GetDataBank(config,parameters,returns):
  status = returns.CreateValues(
    ['IsErr',0],
    ['ErrMessage','']
  )

  dsData = returns.AddNewDatasetEx(
      'MasterData',
    ';'.join([
      'BankCode: string',
      'BankName: string',
      'BankShortName: string',
    ])
  )

  try:

    strSQL = "select * from Bank order by BankCode"

    oRes = config.CreateSQL(strSQL).RawResult
    oRes.First()
    while not oRes.Eof:
      recData = dsData.AddRecord()
      recData.BankCode = oRes.BankCode
      recData.BankName = oRes.BankName
      recData.BankShortName = oRes.BankShortName

      oRes.Next()
    # end while

  except:
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])
