def ShowQueryClick (menu, app) :
    app.SetLocalResourceMode(0)
    formname = menu.StringTag
    state = app.FindForm(formname)
    if state != None :
      dlg = state.FormObject.PyFormObject
    else :
      dlg = app.CreateForm(formname,formname,2,None,None)
    dlg.FormContainer.Show()

def ShowClick (menu, app) :
    app.SetLocalResourceMode(0)
    formname = menu.StringTag
    dlg = app.CreateForm(formname,formname,0,None,None)
    dlg.FormContainer.Show()

def ParameterJournalClick (menu, app):
  ph = app.CreateValues()
  fParam = app.CreateForm('Parameter/fKodeJurnal', 'Parameter/fKodeJurnal', 0, ph, None)
  fParam.Show()


