import sys
import com.ihsan.foundation.pobjecthelper as phelper

TES = 'tes'
def tes():
  raise '','tes'

def CreateAccount(oProduct, BranchCode = None , CurrencyCode = None):
  config = oProduct.Config
  app = config.AppObject
  helper = oProduct.Helper
  
  ProductId = oProduct.ProductId
  AccountName = oProduct.ProductName
  ProductCode = oProduct.ProductCode
  
  #ambil account cabang valuta yang baru
  
  ## AMBIL SEMUA DATA CABANG ##
  newCabang = []
        
  #res = app.rexecscript('corporate','appinterface/Cabang.GetAllCode',app.CreateValues())
  #rec = res.FirstRecord
  #if rec.Is_Error : raise '',rec.Err_Message
  #newCabang = eval(rec.StrLsCabang)
  AddParam = ''
  if BranchCode != None :
    AddParam = " where BranchCode = '%s' " % BranchCode 
  sSQL = 'select BranchCode from Branch ' + AddParam  
  rSQL = config.CreateSQL(sSQL).RawResult
  rSQL.First()
  while not rSQL.Eof:
    newCabang.append(rSQL.BranchCode)
    rSQL.Next()
  # end While
  
  ## AMBIL SEMUA DATA VALUTA ##  
  newValuta = []    
  
  #res = app.rexecscript('accounting','appinterface/Currency.GetAllCode',app.CreateValues())  
  #rec = res.FirstRecord
  #if rec.Is_Error : raise '',rec.Err_Message
  #newValuta = eval(rec.StrLsValuta)
  AddParam = ''
  if CurrencyCode != None :
    AddParam = " where Currency_Code = '%s' " % CurrencyCode
  sSQL = 'select Currency_Code from Currency ' + AddParam
  rSQL = config.CreateSQL(sSQL).RawResult
  rSQL.First()
  while not rSQL.Eof:
    newValuta.append(rSQL.Currency_Code)
    rSQL.Next()
  # end While 
    
  newCabangValuta = [[cabang,valuta] for cabang in newCabang for valuta in newValuta]
   
  for CabangValuta in newCabangValuta:
    oProduct = helper.GetObjectByNames('ProductAccount',
        {'ProductId' : ProductId,
         'BranchCode':CabangValuta[0],
         'CurrencyCode':CabangValuta[1]
         })
    if oProduct.isnull :                
      param = [ProductCode,CabangValuta[0],CabangValuta[1]]        
      oProductAccount = helper.CreatePObject('ProductAccount',param)
      oProductAccount.AccountName = AccountName
      oProductAccount.BranchCode = CabangValuta[0]
      oProductAccount.CurrencyCode = CabangValuta[1]
      oProductAccount.ProductId = ProductId
      oProductAccount.Status = 'A'
    #endif  
  #end for