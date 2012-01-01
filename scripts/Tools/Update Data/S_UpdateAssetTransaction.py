import com.ihsan.foundation.pobjecthelper as phelper
import sys

MAPFundEntity = {'Z' : 1 , 'I' : 2, 'W' : 3}
def DAFScriptMain(config, parameter, returnpacket):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  status = returnpacket.CreateValues(["Is_Error", 0], ["Error_Message", ""])
  helper = phelper.PObjectHelper(config)

  config.BeginTransaction()
  try:
    s = ' \
      SELECT FROM FixedAssetTransactItem \
      ( \
        TransactionItemId, \
        Self \
      );'

    oql = config.OQLEngine.CreateOQL(s)
    oql.active = 1
    ds  = oql.rawresult
    
    row = 1
    while not ds.Eof:      
      oAssetTransactItem = helper.GetObject('FixedAssetTransactItem',ds.TransactionItemId)
      oAsset = oAssetTransactItem.LFixedAsset
      config.SendDebugMsg('Data ke %d PROSES Asset %s ' % (row,oAsset.AccountNo + ' ' + oAsset.AccountName))      
      if oAsset.LAssetCategory.AssetType == 'T' :
        oProduct = oAsset.LProductAccount.LProduct
        FundEntity = MAPFundEntity[oProduct.FundCategory or 'I']
        oAsset.FundEntity = FundEntity
        oAssetTransactItem.FundEntity = FundEntity
      else :
        oAsset.FundEntity = 4
        oAssetTransactItem.FundEntity = 4
      # end if else  

      row += 1
      ds.Next()
    # end while  

    config.Commit()
  except:
    config.Rollback()
    status.Is_Error = 1
    status.Error_Message = str(sys.exc_info()[1])
  # end try except  

  return 1