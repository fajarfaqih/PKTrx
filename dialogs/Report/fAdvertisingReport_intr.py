class fAdvertisingReport:
  def __init__(self, formObj, parentForm):
    self.app=formObj.ClientApplication
    self.userapp = self.app.UserAppObject

  def Show(self):
    return self.FormContainer.Show()


  def PrintClick(self,sender) :
    self.FormObject.CommitBuffer()
    ph = self.FormObject.GetDataPacket()
    ph = self.app.ExecuteScript("Report/S_AdvertisingReport", ph)
    sw = ph.Packet.GetStreamWrapper(0)

    fileName = self.app.SaveFileDialog("Save to file..", "Format File(*.txt)|*.txt")
    if fileName.find(".txt") == -1 : fileName += ".txt"
    sw.SaveToFile(fileName)

    self.app.ShellExecuteFile(fileName)
    sender.ExitAction = 1

    return 1

