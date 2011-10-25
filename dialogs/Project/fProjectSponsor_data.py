import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist,parameters):
  oKey = parameters.FirstRecord.key
  #oProductAccount = uideflist.config.AccessPObject(oKey)
  #oKey = "PObj:ProjectAccount#ACCOUNTNO=%d" % oProductAccount.ProductId
  uideflist.SetData('uipProject',oKey)
  
def ProjectSponsorOnSetData(sender):
  rec = sender.ActiveRecord
  helper = phelper.PObjectHelper(sender.uideflist.config)

  #oProduct = helper.GetObjectByInstance('ZakahProduct', sender.ActiveInstance)
  oDonor = helper.CreateObject('ExtDonor')
  oDonor.GetData(rec.SponsorId)
  
  rec.ExtSponsor = oDonor.full_name
  


