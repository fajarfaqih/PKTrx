import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter) :
    helper = phelper.PObjectHelper(uideflist.config)
    paramMode = {
    'NewGroup':'ClearDataMode(uideflist,rec, parameter)',
    'NewDetail':'ClearDataMode(uideflist,rec, parameter)',
    'Edit':'FillDataMode(uideflist,rec, parameter)',
    'View':'FillDataMode(uideflist,rec, parameter)',
    'SENTINEL':''
    }
    rec = uideflist.uipData.Dataset.AddRecord()
    rec = eval('helper.LoadScript(\'GeneralModule.S_ObjectEditor\').'+ \
      paramMode[parameter.FirstRecord.mode])
    ID = parameter.FirstRecord.ID
    rec.ID = ID
    rec.mode = parameter.FirstRecord.mode
    rec.SetFieldByName(ID+'ID',rec.GetFieldByName(ID))

def ProductOnSetData(sender):
  rec = sender.ActiveRecord
  helper = phelper.PObjectHelper(sender.uideflist.config)

  oProduct = helper.GetObjectByInstance('Program', sender.ActiveInstance)
  if (rec.ParentProductId or 0) != 0:
    oParent = oProduct.LProductParent

    rec.SetFieldByName('LProductParent.ProductId',oParent.ProductId)
    rec.SetFieldByName('LProductParent.ProductName',oParent.ProductName)

