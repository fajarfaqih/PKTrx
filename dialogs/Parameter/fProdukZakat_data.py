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

    mode = parameter.FirstRecord.mode
    ID = parameter.FirstRecord.ID
    
    rec = uideflist.uipData.Dataset.AddRecord()
    rec = eval('helper.LoadScript(\'GeneralModule.S_ObjectEditor\').'+ \
      paramMode[mode])

    rec.ID = ID
    rec.mode = mode
    rec.SetFieldByName(ID+'ID',rec.GetFieldByName(ID))

def ProductOnSetData(sender):
  rec = sender.ActiveRecord
  helper = phelper.PObjectHelper(sender.uideflist.config)

  oProduct = helper.GetObjectByInstance('ZakahProduct', sender.ActiveInstance)
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
    ObjName = 'ZakahProduct'
    LsFieldInput = ('ProductCode','ProductName','Description','Status',
      'PercentageOfAmilFunds','FundCategory','Rate','ParentProductId',
      'Nishab','Haul','IsDetail','Level')
    config.BeginTransaction()
    try :
        helper = phelper.PObjectHelper(config)
        if rsrc.mode in ['NewGroup','NewDetail'] :
          oProduct = helper.GetObjectByNames('Product',{'ProductCode' :rsrc.ProductCode})
          if not oProduct.isnull:
            raise '','Kode produk telah digunakan, silahkan ubah kode produk'
           
        rsrc.SetFieldByName(rsrc.ID,rsrc.GetFieldByName(rsrc.ID+'ID'))
        obj = helper.LoadScript('GeneralModule.S_ObjectEditor').CreateOrEditDataObject\
         (config, ObjName, ((rsrc.ID,rsrc.GetFieldByName(rsrc.ID)),), rsrc, LsFieldInput, True)
        if rsrc.mode in ['NewGroup','NewDetail']:
          oZProduct = helper.GetObjectByInstance(ObjName,obj)
          oZProduct.SetHierarchy()
          if rsrc.mode == 'NewDetail' :
            oZProduct.GenerateGLInterface()
            helper.LoadScript('Product.CreateProductAccount').CreateAccount(oZProduct)
            
        config.Commit()
    except :
        config.Rollback()
        raise
    return 1
