class fGeneralFilterReport:
  def __init__(self, formObj, parentForm, mode):
    self.app=formObj.ClientApplication
    self.userapp = self.app.UserAppObject
    self.mode = mode
    self.ObjectAccess = self.app.GetClientClass("ClientObjectAccess", "ObjectAccess")()
    self.ListFunc = {
      'RekapDonasi':('FilterCabang','FilterNilai','ID','Rekapitulasi Donasi' ),
      'RekapTransKas':('FilterCabang','FilterNilai','ID','Rekapitulasi Transaksi Kas'),
      'SENTINEL':''
    }

  def FormShow(self,captionMode):
    self.FormObject.Caption += self.ListFunc[self.mode][3]
    return self.FormContainer.Show()


  def PrintClick(self,sender) :
    if self.uipData.TglAwal > self.uipData.TglAkhir :
       raise 'PERINGATAN','Tanggal Awal tidak boleh lebih besar dari tanggal akhir'
    self.uipData.Edit()
    self.FormObject.CommitBuffer()
    ph = self.FormObject.GetDataPacket()
    result = self.app.ExecuteScript("Report/S_GeneralPrintReport",
           ph)
    streamWrapper = result.Packet.GetStreamWrapper(0)
    ExF = result.Packet.FirstRecord.ExF
    fileName = self.app.SaveFileDialog("Save to file..",
             "Format File(*%s)|*%s"%(ExF,ExF))
    if fileName.find(ExF) == -1 :
      fileName += ExF
    streamWrapper.SaveToFile(fileName)

    self.app.ShellExecuteFile(
        fileName
           )
    sender.ExitAction = 1

    return 1

