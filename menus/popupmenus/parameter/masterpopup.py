def ShowClick (sender, context) :
    FormParam = {
     'fProdukZakat':('New','Edit','View','NonAktif','parameter/','ProductId'),
     'fProgram':('New','Edit','View','NonAktif','parameter/','ProductId'),
     'fProject':('New','Edit','View','NonAktif','parameter/','ProductId'),
     'fSponsor':('New','Edit','View','SelaluAktif','parameter/','SponsorId'),
     'fRekeningKasKecil':('New','Edit','View','NonAktif','parameter/','AccountNo'),
     'fRekeningBank':('New','Edit','View','NonAktif','parameter/','AccountNo'),
     'fRekeningKasBank':('New','Edit','View','NonAktif','parameter/','AccountNo'),
     'fRekeningKasBank':('New','Edit','View','NonAktif','parameter/','AccountNo'),
     'fAssetCategory':('New','Edit','View','NonAktif','parameter/','AssetCategoryId'),
     'fVolunteer':('New','Edit','View','NonAktif','parameter/','VolunteerId'),
     'fBank':('New','Edit','View','NonAktif','parameter/','BankCode'),
     'fInvestee':('New','Edit','View','NonAktif','parameter/','InvesteeId'),
     'fExternalDebtor':('New','Edit','View','NonAktif','parameter/','DebtorId'),
     'SENTINEL':''
    }
    app = context.OwnerForm.ClientApplication
    app.SetLocalResourceMode(0)
    formname = FormParam[context.Name][4]+context.Name
    key = context.KeyObjConst
    mode = FormParam[context.Name][sender.NumberTag]
    if mode != 'New' and key == '' :
       raise 'PERINGATAN','Data Kosong! silakan pilih NEW'
    if mode == 'SelaluAktif' :
       raise 'PERINGATAN','Data Tidak Dapat di nonaktifkan'
    if mode == 'NonAktif' :
      if app.ConfirmDialog('Apakah anda yakin akan menonaktifkan data ini?') :
        app.ExecuteScript('NonAktifkanData',app.CreateValues(['key',key]))
        app.ShowMessage('Data Berhasil di non aktifkan')
    else :
      ph = app.CreateValues(['key',key],['mode',mode],['ID',FormParam[context.Name][5]])
      dlg = app.CreateForm(formname,formname,0,ph,[mode])
      dlg.FormShow(mode)

def ActivateClick(sender,context):
    app = context.OwnerForm.ClientApplication
    key = context.KeyObjConst

    #if context.GetFieldValue(context.Name + '.Status') in ['A','Active'] :
    #   app.ShowMessage('Data sudah dalam status aktif')
    #   return

    if app.ConfirmDialog('Apakah anda yakin akan mengaktifkan data ini?') :
       app.ExecuteScript('AktifkanData',app.CreateValues(['key',key]))
       app.ShowMessage('Data Berhasil di aktifkan')

def NonActivateClick(sender,context):
    app = context.OwnerForm.ClientApplication
    key = context.KeyObjConst

    #if context.GetFieldValue(context.Name + '.Status') in ['N','NonActive'] :
    #   app.ShowMessage('Data sudah dalam status nonaktif')
    #   return

    if app.ConfirmDialog('Apakah anda yakin akan menonaktifkan data ini?') :
       app.ExecuteScript('NonAktifkanData',app.CreateValues(['key',key]))
       app.ShowMessage('Data Berhasil di non aktifkan')

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
