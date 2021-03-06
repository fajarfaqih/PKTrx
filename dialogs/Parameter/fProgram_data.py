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

def OnBeginProcessData (uideflist, AData) :
  config = uideflist.Config
  helper = phelper.PObjectHelper(config)
  uData = AData.uipData.GetRecord(0)
  if uData.mode in ['NewGroup','NewDetail'] :
     pass

def SimpanData(config, parameter, returnpacket) :
    rsrc = parameter.uipData.GetRecord(0)
    #Parameter
    ObjName = 'Program'
    LsFieldInput = ('ProductCode','ProductName','Description','Status',
      'PercentageOfAmilFunds','FundCategory',
      'FixedValue','FixedValueAmount','MultiPackage','Level','ParentProductId','IsDetail')
    config.BeginTransaction()
    try :
        helper = phelper.PObjectHelper(config)

        if rsrc.mode in ['NewGroup','NewDetail'] :
          oProduct = helper.GetObjectByNames('Product',{'ProductCode' :rsrc.ProductCode})
          if not oProduct.isnull:
             raise '','Kode program telah digunakan, silahkan ubah kode program'
           
        rsrc.SetFieldByName(rsrc.ID,rsrc.GetFieldByName(rsrc.ID+'ID'))

        obj = helper.LoadScript('GeneralModule.S_ObjectEditor').CreateOrEditDataObject\
         (config, ObjName, ((rsrc.ID,rsrc.GetFieldByName(rsrc.ID)),), rsrc, LsFieldInput, True)

        if rsrc.mode in ['NewGroup','NewDetail']:
          oProgram = helper.GetObjectByInstance(ObjName,obj)
          oProgram.SetHierarchy()
          if rsrc.mode == 'NewDetail' :
            oProgram.GenerateGLInterface()
            helper.LoadScript('Product.CreateProductAccount').CreateAccount(oProgram)

            
        config.Commit()
    except :
        config.Rollback()
        raise
    return 1
