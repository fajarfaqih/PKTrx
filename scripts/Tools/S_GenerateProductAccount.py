import sys
import com.ihsan.foundation.pobjecthelper as phelper

def DAFScriptMain(config,parameters,returnpacket):
  app = config.AppObject
  helper = phelper.PObjectHelper(config)
  status = returnpacket.CreateValues(
      ['Is_Error',0],
      ['Error_Message','']
  )
  config.BeginTransaction()
  try:
    
    #ambil account cabang valuta yang baru
    newCabang = []
    #ambil semua data cabang      
    res = app.rexecscript('corporate','appinterface/Cabang.GetAllCode',app.CreateValues())
    rec = res.FirstRecord
    if rec.Is_Error : raise '',rec.Err_Message
    
    newCabang = eval(rec.StrLsCabang)
      
    newValuta = []    
    #ambil semua data cabang
    res = app.rexecscript('accounting','appinterface/Currency.GetAllCode',app.CreateValues())
    
    rec = res.FirstRecord
    if rec.Is_Error : raise '',rec.Err_Message
    newValuta = eval(rec.StrLsValuta)
    
    newCabangValuta = [[cabang,valuta] for cabang in newCabang for valuta in newValuta]
     
        
    strSQL = "select productid,productname,productcode from transaction.product where isdetail='T' and producttype in ('Z','G') order by productcode"
    oRes = config.CreateSQL(strSQL).RawResult
    
    while not oRes.Eof:
      AccountName = oRes.ProductName
      for CabangValuta in newCabangValuta:
        oProduct = helper.GetObjectByNames('ProductAccount',
            {'ProductId' : oRes.ProductId,
             'BranchCode':CabangValuta[0],
             'CurrencyCode':CabangValuta[1]
             })
        if oProduct.isnull :                
          param = [oRes.ProductCode,CabangValuta[0],CabangValuta[1]]        
          oProductAccount = helper.CreatePObject('ProductAccount',param)
          oProductAccount.AccountName = AccountName
          oProductAccount.BranchCode = CabangValuta[0]
          oProductAccount.CurrencyCode = CabangValuta[1]
          oProductAccount.ProductId = oRes.ProductId
          oProductAccount.Status = 'A'
        #endif  
      #end for
      oRes.Next()    
    config.Commit()    
  except :
    config.Rollback()
    status.Is_Error = 1
    status.Error_Message = str(sys.exc_info()[1])
