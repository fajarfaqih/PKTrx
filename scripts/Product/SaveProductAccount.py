import sys
import com.ihsan.foundation.pobjecthelper as phelper

def DAFScriptMain(config,parameters,returnpacket):
  app = config.AppObject
  helper = phelper.PObjectHelper(config)
  status = returnpacket.CreateValues(
      ['Is_Error',0],
      ['Err_Message','']
  )
  config.BeginTransaction()
  try:
    #ambil nama account
    AccountName = parameters.uipData.GetRecord(0).ProductName
    
    #ambil account cabang valuta yang sudah ada
    dsProductAccount = parameters.uipLsAccount
    currentCabangValuta = []
    for i in range(dsProductAccount.RecordCount):
      rec = dsProductAccount.GetRecord(i)
      currentCabangValuta.append([rec.GetFieldByName('BranchCode'),
                                 rec.GetFieldByName('CurrencyCode')])
    #--end for
    
    #ambil account cabang valuta yang baru
    recInput = parameters.uipInput.GetRecord(0)
    newCabang = []
    
    if recInput.isAllCabang:
      #ambil semua data cabang      
      res = app.rexecscript('corporate','appinterface/Cabang.GetAllCode',app.CreateValues())
      rec = res.FirstRecord
      if rec.Is_Error : raise '',rec.Err_Message
      
      newCabang = eval(rec.StrLsCabang)
    else:
      newCabang.append(recInput.GetFieldByName('LCabang.Kode_Cabang'))
    
      
    newValuta = []
    if recInput.isAllValuta:
      #ambil semua data cabang
      res = app.rexecscript('accounting','appinterface/Currency.GetAllCode',app.CreateValues())
      
      rec = res.FirstRecord
      if rec.Is_Error : raise '',rec.Err_Message
      newValuta = eval(rec.StrLsValuta)
    else:
      newValuta.append(recInput.GetFieldByName('LValuta.Currency_Code'))
    
    newCabangValuta = [[cabang,valuta] for cabang in newCabang for valuta in newValuta]
#    for cabang in newCabang:
#      for valuta in newValuta:
#        newCabangValuta.append([cabang,valuta])
      #end for  
    #end for
    # Create New Product Account
     
    recProductData = parameters.uipData.GetRecord(0)
    
    for CabangValuta in newCabangValuta:
      if CabangValuta not in currentCabangValuta:                
        param = [recProductData.ProductCode,CabangValuta[0],CabangValuta[1]]        
        oProductAccount = helper.CreatePObject('ProductAccount',param)
        oProductAccount.AccountName = AccountName
        oProductAccount.BranchCode = CabangValuta[0]
        oProductAccount.CurrencyCode = CabangValuta[1]
        oProductAccount.ProductId = recProductData.ProductId
        oProductAccount.Status = 'A'
      #endif  
    #end for    
    config.Commit()    
  except :
    config.Rollback()
    status.Is_Error = 1
    status.Err_Message = str(sys.exc_info()[1])
