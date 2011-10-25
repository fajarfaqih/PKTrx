import com.ihsan.foundation.pobjecthelper as phelper
import sys

def GenerateAllAccountByBranch(config, params, returns):
  status = returns.CreateValues(
    ['Is_Error',0],['Error_Message','']
  )
  config.BeginTransaction()
  try:
    app = config.AppObject
    app.ConCreate('CPA')
    helper = phelper.PObjectHelper(config)    
    BranchCode = params.FirstRecord.BranchCode
    BranchName = params.FirstRecord.BranchName
    
    ScriptHelper = helper.LoadScript('Product.CreateProductAccount')
    app.ConWriteln('Proses Akses Product Untuk Cabang %s' % BranchName,'CPA') 
    sSQL = "select ProductId,ProductName from Product where ProductType in ('Z','G') and IsDetail='T'"
    rSQL = config.CreateSQL(sSQL).RawResult
    rSQL.First()
    while not rSQL.Eof:
      app.ConWriteln("Proses buka akses produk '%s' " % rSQL.ProductName ,'CPA')
      oProduct = helper.GetObject('Product',rSQL.ProductId)      
      ScriptHelper.CreateAccount(oProduct,BranchCode)
      rSQL.Next()
    # end while
    
    config.Commit()
  except:
    config.Rollback()
    status.Is_Error = 1
    status.Error_Message = str(sys.exc_info()[1])
    config.SendDebugMsg(status.Error_Message)