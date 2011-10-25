def ShowClick (sender, context) :
    app = context.OwnerForm.ClientApplication
    app.SetLocalResourceMode(0)
    formname = 'parameter/fBudgetOwner'

    key = context.KeyObjConst
    mode = sender.StringTag
    if mode != 'New' and key == '' :
       raise 'PERINGATAN','Data Kosong! silakan pilih NEW'
    else :
      ph = app.CreateValues(['key',key],['mode',mode],['ID','OwnerID'])
      dlg = app.CreateForm(formname,formname,0,ph,[mode])
      dlg.FormShow(mode)

def DeleteClick(sender,context):
    app = context.OwnerForm.ClientApplication
    key = context.KeyObjConst
    ph = app.CreateValues(['key',key])
    
    resp = app.ExecuteScript('',ph)
    
    
