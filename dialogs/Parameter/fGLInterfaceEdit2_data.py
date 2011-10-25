import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter) :
    config = uideflist.config
    #helper = phelper.PObjectHelper(uideflist.config)
    #key = parameter.FirstRecord.key.replace('ZakahProduct','Product')

    #uideflist.SetData('uipProduct', parameter.FirstRecord.key)

    uipProduct = uideflist.uipProduct.Dataset.AddRecord()
    uipProduct.SetFieldAt(0, 'PObj:Product#ProductId=%d' % 2)
    uipProduct.ProductId = 2
    
    # get detil
    resGL = config.CreateSQL("\
        select * from glinterface where productid = %d \
    " % uipProduct.ProductId ).rawresult

    resGL.First()
    while not resGL.Eof:
      recGL = uideflist.Ls_GLInterface.Dataset.AddRecord()
      #oDetil = oTran.uipDetil.AddRecord()
      InterfaceId = int(resGL.InterfaceId)

      recGL.SetFieldAt(0, 'PObj:GLInterface#InterfaceId=%d' % InterfaceId)
#      recGL.SetFieldAt(1,resGL.InterfaceCode)
      recGL.InterfaceCode = resGL.InterfaceCode
      recGL.Description = resGL.Description
      recGL.AccountCode = resGL.AccountCode
      recGL.AccountName = resGL.AccountName
      recGL.ProductId = resGL.ProductId
      resGL.Next()
    # end while
      

    #uideflist.Ls_GLInterface.Dataset.AddRecord()
    
def GLOnSetData(sender):
  rec = sender.ActiveRecord
  #rec.SetFieldByName('LAccount.Account_Code',rec.ItemCode)


