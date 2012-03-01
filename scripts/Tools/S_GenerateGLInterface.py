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
    
    strSQL = "select productid,productname,productcode from transaction.product \
        where isdetail='T' order by productcode"
    oRes = config.CreateSQL(strSQL).RawResult
    
    while not oRes.Eof:
      app.ConWriteln('Proses : '+oRes.ProductName,'GL')
      AccountName = oRes.ProductName
      oProduct = helper.GetObject('Product',oRes.ProductId).CastToLowestDescendant()
      
      #if not oProduct.GLInterfaceExist():
      app.ConWriteln('Generate GL Interface','GL')
      oProduct.GenerateGLInterface()
  
      # end if
      oRes.Next()
    # end while    
    config.Commit()    
  except :
    config.Rollback()
    status.Is_Error = 1
    status.Error_Message = str(sys.exc_info()[1])
