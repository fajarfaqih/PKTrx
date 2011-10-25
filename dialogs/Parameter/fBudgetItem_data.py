import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter) :
    helper = phelper.PObjectHelper(uideflist.config)
    paramMode = {
    'New':'ClearDataMode(uideflist,rec, parameter)',
    'Edit':'FillDataMode(uideflist,rec, parameter)',
    'View':'FillDataMode(uideflist,rec, parameter)',
    'SENTINEL':''
    }
    mode = parameter.FirstRecord.mode
    rec = uideflist.uipData.Dataset.AddRecord()
    rec = eval('helper.LoadScript(\'GeneralModule.S_ObjectEditor\').'+ \
      paramMode[mode])
    ID = parameter.FirstRecord.ID
    rec.ID = ID
    rec.mode = mode
    rec.SetFieldByName(ID+'ID',rec.GetFieldByName(ID))

    config = uideflist.config
    
def OnSetData(sender):
  rec = sender.ActiveRecord
  helper = phelper.PObjectHelper(sender.uideflist.config)

  oItem = helper.GetObjectByInstance('BudgetItem', sender.ActiveInstance)
  if (rec.ParentBudgetItemCode or 0) != 0:
    oParent = oItem.LParent

    rec.SetFieldByName('LParent.BudgetItemCode',oParent.BudgetItemCode)
    rec.SetFieldByName('LParent.BudgetItemDescription',oParent.BudgetItemDescription)
    
def OnBeginProcessData (uideflist, AData) :
  config = uideflist.Config
  helper = phelper.PObjectHelper(config)
  uData = AData.uipData.GetRecord(0)
  if uData.mode == 'New' :
     pass

def SimpanData(config, parameter, returnpacket) :
    rsrc = parameter.uipData.GetRecord(0)
    #Parameter
    ObjName = 'BudgetItem'
    LsFieldInput = ('BudgetItemDescription','Level','Is_Detail','ParentBudgetItemCode')
    config.BeginTransaction()
    try :
        helper = phelper.PObjectHelper(config)
        rsrc.SetFieldByName(rsrc.ID,rsrc.GetFieldByName(rsrc.ID+'ID'))

        obj = helper.LoadScript('GeneralModule.S_ObjectEditor').CreateOrEditDataObject\
         (config, ObjName, ((rsrc.ID,rsrc.GetFieldByName(rsrc.ID)),), rsrc, LsFieldInput,
         False, rsrc.mode =='New')

        if rsrc.mode =='New':
           obj = helper.GetObjectByInstance(ObjName,obj)
           obj.SetHierarchy()
           
        config.Commit()
    except :
        config.Rollback()
        raise
    return 1
