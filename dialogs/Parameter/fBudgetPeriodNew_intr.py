class fBudgetPeriodNew :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication

  def bCreateClick(self, sender):
    app = self.app
    if app.ConfirmDialog('Yakin simpan data ?'):
      ph = self.app.CreateValues(['PeriodValue', self.uipBudgetPeriod.PeriodValue])
      ph = self.FormObject.CallServerMethod("CreateBudgetPeriod", ph)
      
      res = ph.FirstRecord
      if res.IsErr:
        raise 'PERINGATAN',res.ErrMessage

      app.ShowMessage('Periode Baru telah berhasil di buat')

      queryform = app.FindForm('parameter/fDaftarBudgetPeriod')
      query = queryform.FormObject.GetPanelByName('qBudgetPeriod')
      query.Refresh()

      sender.ExitAction = 1
    #-- if

    
