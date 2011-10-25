import sys
import com.ihsan.foundation.pobjecthelper as phelper

def DAFScriptMain(config,parameters,returnpacket):
  app = config.AppObject
  helper = phelper.PObjectHelper(config)
  status = returnpacket.CreateValues(
      ['Is_Error',0],
      ['Error_Message','']
  )
  app.ConCreate('GL')
  config.BeginTransaction()
  try:
    
    strSQL = "select assetcategoryid,assetcategoryname,productcode from transaction.assetcategory"
    oRes = config.CreateSQL(strSQL).RawResult
    
    while not oRes.Eof:
      app.ConWriteln('Proses : '+oRes.ProductName,'GL')
      AccountName = oRes.AssetCategoryName
      oAsset = helper.GetObject('AssetCategory',oRes.AssetCategoryId).CastToLowestDescendant()
      
      #if not oProduct.GLInterfaceExist():
      app.ConWriteln('Generate GL Interface ' + AccountName,'GL')
      oAsset.GenerateGLInterface()
  
      # end if
      oRes.Next()
    # end while
    
    config.Commit()    
  except :
    config.Rollback()
    status.Is_Error = 1
    status.Error_Message = str(sys.exc_info()[1])
