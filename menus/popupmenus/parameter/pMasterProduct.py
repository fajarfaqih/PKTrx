FormParam = {
 'ZakahProduct':('NewGroup','NewDetail','Edit','View','ProductId','parameter/','fProdukZakat','fProdukZakatAccount'),
 'Program':('NewGroup','NewDetail','Edit','View','ProductId','parameter/','fProgram','fProgramAccount'),
 'Project':('NewGroup','NewDetail','Edit','View','ProductId','parameter/','fProject','fProjectAccount'),
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

def ActivateClick(sender,context):
    app = context.OwnerForm.ClientApplication
    key = context.KeyObjConst

    if context.GetFieldValue(context.Name + '.Status') in ['A','Active'] :
       app.ShowMessage('Data sudah dalam status aktif')
       return
       
    if app.ConfirmDialog('Apakah anda yakin akan mengaktifkan data ini?') :
       app.ExecuteScript('AktifkanData',app.CreateValues(['key',key]))
       app.ShowMessage('Data Berhasil di aktifkan')

def NonActivateClick(sender,context):
    app = context.OwnerForm.ClientApplication
    key = context.KeyObjConst

    if context.GetFieldValue(context.Name + '.Status') in ['N','NonActive'] :
       app.ShowMessage('Data sudah dalam status nonaktif')
       return

    if app.ConfirmDialog('Apakah anda yakin akan menonaktifkan data ini?') :
       app.ExecuteScript('NonAktifkanData',app.CreateValues(['key',key]))
       app.ShowMessage('Data Berhasil di nonaktifkan')
       
def DeleteClick(sender,context):
    app = context.OwnerForm.ClientApplication
    key = context.KeyObjConst

    if app.ConfirmDialog('Apakah anda yakin akan menghapus data ini?') :

      resp = app.ExecuteScript('HapusData',app.CreateValues(['key',key]))
      
      status = resp.FirstRecord
      if status.Is_Err :
        app.ShowMessage(status.Err_Message)
        return
      app.ShowMessage('Data Berhasil di hapus')
      qPanel = context.OwnerForm.GetPanelByName(context.Name)
      qPanel.DeleteRow()

def NewAccountClick(sender,context):
    app = context.OwnerForm.ClientApplication
    key = context.KeyObjConst
    
    if context.GetFieldValue(context.Name + '.IsDetail') == 'F' :
       productname = context.GetFieldValue(context.Name +'.Nama_Produk')
       raise 'PERINGATAN','Rekening %s bukan Rekening Level Detil, tidak bisa ditambah Cabang atau Valuta.' % productname

    if key == '' :
       raise 'PERINGATAN','Data Kosong! silakan pilih NEW'

    fullform = FormParam[context.Name][5]+FormParam[context.Name][7]
    formname = FormParam[context.Name][7]
    
    ph = app.CreateValues(['key',key],['mode','View'],['ID',FormParam[context.Name][4]])

    dlg = app.CreateForm(fullform,formname,0,ph,None)
    dlg.FormShow()
    
def ShowFormWihtdataClick(sender,context):
    app = context.OwnerForm.ClientApplication
    key = context.KeyObjConst
    formname = sender.StringTag
    
    ph = app.CreateValues(['key',key])
    dlg = app.CreateForm(formname,formname,0,ph,None)
    dlg.FormShow()
    
    

