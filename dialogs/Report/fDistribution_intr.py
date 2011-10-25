class fCollectionReport:

  def __init__(self,formObj,parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.fSelectProgram = None
    self.fSelectDonor = None
    
  def Show(self):
    uipFilter = self.uipFilter
    uipFilter.Edit()
    uipFilter.IsAllDonor = 'T'
    uipFilter.IsAllChannel = 'T'
    uipFilter.IsAllProgram = 'T'
    uipFilter.IsAllSponsor = 'T'
    uipFilter.IsAllVolunteer = 'T'
    uipFilter.IsAllFundEntity = 'T'
    self.FormContainer.Show()
    
    
  def bSelectProgram(self,sender):
    if self.fSelectProgram == None:
      fData = self.app.CreateForm('Report/fSelectProgram', 'fSelectProgram', 0, None, None)
      self.fSelectProduct = fData
    else:
      fData = self.fSelectProgram
    BranchCode = self.uipFilter.BranchCode
    if fData.GetProgram(BranchCode) == 1:
      AccountNo = fData.AccountNo
      ProgramName = fData.ProductName

      self.uipFilter.Edit()
      self.uipFilter.AccountNo = AccountNo
      self.uipFilter.ProgramName = ProgramName

    return 1


  def bPilihDonor(self,sender):
    if self.fSelectProgram == None:
      fData = self.app.CreateForm('Donatur/fSearchDonor', 'Donatur/fSearchDonor', 0, None, None)
      self.fSelectDonor = fData
    else:
      fData = self.fSelectDonor

    if fData.GetDonorData() == 1:
      uipFilter = self.uipFilter
      uipFilter.Edit()
      uipFilter.IdDonor = fData.DonorIntId
      uipFilter.NoDonor = fData.DonorId
      uipFilter.NamaDonor = fData.DonorName


  def CheckClick(self,sender):
    form = self.form
    CtlNames = {
      'IsAllDonor' : ['NoDonor','NamaDonor','bSelectDonor'],
      'IsAllChannel' : ['ChannelCode'],
      'IsAllProgram' : ['ProgramName','bSelectProgram'],
      'IsAllSponsor' : ['LSponsor'],
      'IsAllVolunteer' : ['LVolunteer'],
      'IsAllFundEntity' : ['FundEntity'],
    }
    
    for controlname in CtlNames[sender.Name] :
      form.GetPanelByName('pFilter3').GetControlByName(controlname).Visible = not sender.Checked
      
  def bCetakClick(self,sender):
    uipFilter = self.uipFilter
    if uipFilter.BeginDate > uipFilter.EndDate :
       raise 'PERINGATAN','Tanggal Awal tidak boleh lebih besar dari tanggal akhir'

    self.FormObject.CommitBuffer()
    ph = self.FormObject.GetDataPacket()
    ph = self.app.ExecuteScript("Report/S_CollectionReport", ph)
    sw = ph.Packet.GetStreamWrapper(0)

    fileName = self.app.SaveFileDialog("Save to file..", "Format File(*.txt)|*.txt")
    if fileName.find(".txt") == -1 : fileName += ".txt"
    sw.SaveToFile(fileName)

    self.app.ShellExecuteFile(fileName)

