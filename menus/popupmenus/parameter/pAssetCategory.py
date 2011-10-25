FormParam = {
 'AssetCategory':('NewGroup','NewDetail','Edit','View','AssetCategoryId','parameter/','fAssetCategory','fAssetCategory'),
 'SENTINEL':''
}

def ShowClick (sender, context) :
  app = context.OwnerForm.ClientApplication
  app.SetLocalResourceMode(0)
  fullform = FormParam[context.Name][5]+FormParam[context.Name][6]
  formname = FormParam[context.Name][6]
  key = context.KeyObjConst

  mode = FormParam[context.Name][sender.NumberTag]
  if mode not in  ['NewGroup','NewDetail'] and key == '' :
     raise 'PERINGATAN','Data Kosong! silakan pilih NEW'
  if mode == 'SelaluAktif' :
     raise 'PERINGATAN','Data Tidak Dapat di nonaktifkan'
  else :
    ph = app.CreateValues(['key',key],['mode',mode],['ID',FormParam[context.Name][4]])
    dlg = app.CreateForm(fullform,formname,0,ph,[mode])
    dlg.FormShow(mode)

def GLClick(sender,context):
  app = context.OwnerForm.ClientApplication
  key = context.KeyObjConst
  formname = sender.StringTag

  ph = app.CreateValues(['key',key])
  dlg = app.CreateForm(formname,formname,0,ph,None)
  dlg.FormShow()

