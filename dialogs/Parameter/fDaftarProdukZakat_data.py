import sys

def GetDataProdukZakat(config,parameters,returns):
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
      'Rate: float',
      'PercentageOfAmilFunds: float',
      'Level: integer',
      'IsDetail: string',
      'Status: string',
    ])
  )
  
  try:
    dStatus = {'A' : 'Active','N' : 'Not Active'}
    strSQL = "select * from Product where producttype = 'Z' order by ProductCode"
    
    oRes = config.CreateSQL(strSQL).RawResult
    oRes.First()
    while not oRes.Eof:
      recData = dsData.AddRecord()
      recData.ProductCode = oRes.ProductCode
      recData.ProductName = oRes.ProductName
      recData.Description = oRes.Description
      recData.Rate = oRes.Rate
      recData.PercentageOfAmilFunds = oRes.PercentageOfAmilFunds
      recData.Level = oRes.Level
      recData.IsDetail = oRes.IsDetail
      recData.Status = dStatus[oRes.Status]
      
      oRes.Next()
    # end while

  except:
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])
