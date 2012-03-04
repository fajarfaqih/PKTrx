class fKodeJurnal:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication

  def Show(self):
    #self.FormObject.SetDataFromQuery('uipJournal', '', '')
    self.FormObject.SetDataWithParameters(self.app.CreateValues())
    self.uipJournal.First()
    self.FormContainer.Show()

  def ItemNewRecord (self, sender):
    sender.IsSendJournalDescription = 'F'
