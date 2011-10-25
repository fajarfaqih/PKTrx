new = 1
edit = 1
def NewClick(sender,context):
  app = context.OwnerForm.ClientApplication
  
  formname = 'Project/fNewProjectDetail'
  ph = app.CreateValues(['mode',new])
  dlg = app.CreateForm(formname,formname,0,ph,None)
  dlg.Show(1)

def ViewProjectClick(sender,context):
  app = context.OwnerForm.ClientApplication
  key = context.KeyObjConst
    
  formname = 'Project/fProjectView'
  ph = app.CreateValues(['key',key])

  dlg = app.CreateForm(formname,formname,0,ph,None)
  dlg.Show()
  
def ShowFormWithdataClick(sender,context):
    app = context.OwnerForm.ClientApplication
    key = context.KeyObjConst
    formname = sender.StringTag

    ph = app.CreateValues(['key',key])
    dlg = app.CreateForm(formname,formname,0,ph,None)
    dlg.FormShow()

def ActivateClick(sender,context):
    app = context.OwnerForm.ClientApplication
    key = context.KeyObjConst

    if context.GetFieldValue('ProjectAccount.Status') in ['A','Active'] :
       app.ShowMessage('Data sudah dalam status aktif')
       return

    if app.ConfirmDialog('Apakah anda yakin akan mengaktifkan data ini?') :
       app.ExecuteScript('AktifkanData',app.CreateValues(['key',key]))
       app.ShowMessage('Data Berhasil di aktifkan')

def NonActivateClick(sender,context):
    app = context.OwnerForm.ClientApplication
    key = context.KeyObjConst

    if context.GetFieldValue('ProjectAccount.Status') in ['N','NonActive'] :
       app.ShowMessage('Data sudah dalam status nonaktif')
       return

    if app.ConfirmDialog('Apakah anda yakin akan menonaktifkan data ini?') :
       app.ExecuteScript('NonAktifkanData',app.CreateValues(['key',key]))
       app.ShowMessage('Data Berhasil di nonaktifkan')
       
def DeleteClick(sender,context):
    app = context.OwnerForm.ClientApplication
    key = context.KeyObjConst
    
    if app.ConfirmDialog('Proses ini akan menghapus seluruh transaksi yang terkait dengan project ini.\nApakah anda yakin akan menghapus data project ini ?') :
      rph = app.ExecuteScript('HapusData',app.CreateValues(['key',key]))
      
      status = rph.FirstRecord
      if status.Is_Err : raise 'PERINGATAN',status.Err_Message
      app.ShowMessage('Data Project Berhasil Dihapus')

      qProjectList = context.OwnerForm.GetPanelByName(context.Name)
      qProjectList.DeleteRow()
