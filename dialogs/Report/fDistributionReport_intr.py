MAPEntity = { 1 : 'Zakat',
              2 : 'Infaq',
              3 : 'Wakaf',
              4 : 'Amil',
              5 : 'Non Halal'}

MAPChannel = { 'P' : 'Kas Cabang',
               'R' : 'Kas Kecil',
               'A' : 'Banl',
               'G' : 'Aktiva'}

class fDistributionReport:

  def __init__(self,formObj,parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.fSelectProgram = None
    self.fSelectDonor = None
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    
  def Show(self):
    uipFilter = self.uipFilter
    uipFilter.Edit()
    uipFilter.IsAllBranch = 'F'
    uipFilter.IsAllDonor = 'T'
    uipFilter.IsAllChannel = 'T'
    uipFilter.IsAllProgram = 'T'
    uipFilter.IsAllSponsor = 'T'
    uipFilter.IsAllVolunteer = 'T'
    uipFilter.IsAllFundEntity = 'T'
    
    # Set Branch Filter
    IsHeadOffice = (uipFilter.BranchCode == uipFilter.HeadOfficeCode)
    #self.pFilter2_IsAllBranch.Enabled = IsHeadOffice
    #self.pFilter3_LBranch.Enabled = IsHeadOffice
    self.MasterBranchCode = ''
    if not IsHeadOffice :
      #self.form.GetControlByName('pFilter2.IsAllBranch').ControlCaption = 'Seluruh Cabang (Capem)'
      uipFilter.MasterBranchCode = uipFilter.BranchCode
      
    uipFilter.SetFieldValue('LBranch.BranchCode',uipFilter.BranchCode)
    uipFilter.SetFieldValue('LBranch.BranchName',uipFilter.BranchName)

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
      'IsAllBranch' : ['LBranch'],
      'IsAllDonor' : ['NoDonor','NamaDonor','bSelectDonor'],
      'IsAllChannel' : ['ChannelCode'],
      'IsAllProgram' : ['ProgramName','bSelectProgram'],
      'IsAllSponsor' : ['NoDonor','NamaDonor','bSelectSponsor'],
      'IsAllVolunteer' : ['LVolunteer'],
      'IsAllFundEntity' : ['FundEntity'],
    }
    
    for controlname in CtlNames[sender.Name] :
      form.GetPanelByName('pFilter3').GetControlByName(controlname).Visible = not sender.Checked
      
  def CheckFilter(self):
    uipFilter = self.uipFilter

    if uipFilter.IsAllBranch == 'F' and (uipFilter.GetFieldValue('LBranch.BranchCode') or '') == '' :
       raise 'PERINGATAN','Silahkan pilih cabang terlebih dahulu'
       
    if uipFilter.IsAllChannel == 'F' and (uipFilter.ChannelCode or '') == '' :
       raise 'PERINGATAN','Silahkan pilih jenis pembayaran terlebih dahulu'

    if uipFilter.IsAllProgram == 'F' and (uipFilter.AccountNo or '') == '' :
       raise 'PERINGATAN','Silahkan pilih program terlebih dahulu'

    if uipFilter.IsAllSponsor == 'F' and (uipFilter.IdDonor or 0) == 0 :
#    if uipFilter.IsAllSponsor == 'F' and (uipFilter.GetFieldValue('LSponsor.SponsorId') or 0) == 0 :
       raise 'PERINGATAN','Silahkan pilih sponsor terlebih dahulu'


    if uipFilter.IsAllFundEntity == 'F' and (uipFilter.FundEntity or 0) == 0 :
       raise 'PERINGATAN','Silahkan pilih jenis dana terlebih dahulu'

  def bCetakClick(self,sender):
    self.PrintReport(1)

  def bExportExcelClick(self,sender):
    self.PrintReport(2)

  def PrintReport(self,mode):
    app = self.app
    uipFilter = self.uipFilter
    if uipFilter.BeginDate > uipFilter.EndDate :
       raise 'PERINGATAN','Tanggal Awal tidak boleh lebih besar dari tanggal akhir'

    self.FormObject.CommitBuffer()
    self.CheckFilter()

    if mode == 1:
      ph = self.app.ExecuteScript("Report/S_DistributionReport", self.FormObject.GetDataPacket())
      sw = ph.Packet.GetStreamWrapper(0)

      fileName = self.app.SaveFileDialog("Save to file..", "Format File(*.txt)|*.txt")
      if fileName.find(".txt") == -1 : fileName += ".txt"
      sw.SaveToFile(fileName)

      self.app.ShellExecuteFile(fileName)
    else :
      filename = self.oPrint.ConfirmDestinationPath(app,'xls')
      if filename in ['',None] : return
      
      ph = self.app.ExecuteScript("Report/S_DistributionReport.GetDataTransaction", self.FormObject.GetDataPacket())

      status = ph.FirstRecord
      if status.Is_Err : raise 'PERINGATAN',status.Err_Message
      
      workbook = self.oPrint.OpenExcelTemplate(app,'tplDistributionReport.xls')
      workbook.ActivateWorksheet('data')
      try:

        workbook.SetCellValue(3, 3, status.Tanggal)
        workbook.SetCellValue(4, 3, status.TotalAmount)

        if uipFilter.IsAllBranch == 'F' :
          workbook.SetCellValue(2, 3, status.Cabang)

        if uipFilter.IsAllSponsor == 'F' :
           workbook.SetCellValue(5, 3, uipFilter.NoDonor + ' - ' + uipFilter.NamaDonor)

        if uipFilter.IsAllFundEntity == 'F' :
           workbook.SetCellValue(6, 3, MAPEntity[uipFilter.FundEntity])

        if uipFilter.IsAllProgram == 'F' :
           workbook.SetCellValue(7, 3, uipFilter.ProgramName)

        if uipFilter.IsAllChannel == 'F' :
           workbook.SetCellValue(8, 3, MAPChannel[uipFilter.ChannelCode])

        ds = ph.packet.ReportData
        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 11
          
          workbook.SetCellValue(row, 1, str(i+1))
          workbook.SetCellValue(row, 2, rec.TransactionDateStr)
          workbook.SetCellValue(row, 3, rec.InputDateStr)
          workbook.SetCellValue(row, 4, rec.AccountName)
          workbook.SetCellValue(row, 5, rec.Description)
          #workbook.SetCellValue(row, 6, rec.Channel)
          workbook.SetCellValue(row, 6, rec.Amount)
          workbook.SetCellValue(row, 7, rec.FundEntity)
          workbook.SetCellValue(row, 8, rec.SponsorName)
          workbook.SetCellValue(row, 9, rec.ReferenceNo)
          workbook.SetCellValue(row, 10,rec.Inputer)
          workbook.SetCellValue(row, 11,rec.BranchName)
          workbook.SetCellValue(row, 12,rec.TransactionNo)
          
          i += 1
        # end while
        
        workbook.SaveAs(filename)

      finally:
        workbook = None
        
      app.ShellExecuteFile(filename)
    
    
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
