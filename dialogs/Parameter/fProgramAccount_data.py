import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter) :
    helper = phelper.PObjectHelper(uideflist.config)
    
    ID = parameter.FirstRecord.ID
    
    rec = uideflist.uipData.Dataset.AddRecord()
    rec = helper.LoadScript('GeneralModule.S_ObjectEditor').FillDataMode(uideflist,rec, parameter)

    rec.ID = ID
    rec.SetFieldByName(ID+'ID',rec.GetFieldByName(ID))

def ProductOnSetData(sender):
  rec = sender.ActiveRecord
  helper = phelper.PObjectHelper(sender.uideflist.config)

  oProduct = helper.GetObjectByInstance('Program', sender.ActiveInstance)
  if (rec.ParentProductId or 0) != 0:
    oParent = oProduct.LProductParent

    rec.SetFieldByName('LProductParent.ProductId',oParent.ProductId)
    rec.SetFieldByName('LProductParent.ProductName',oParent.ProductName)

