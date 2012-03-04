MAPEntity = { 1 : 'Zakat',
              2 : 'Infaq',
              3 : 'Wakaf',
              4 : 'Amil',
              5 : 'Non Halal'}

MAPChannel = { 'P' : 'Kas Kecil',
               'R' : 'Kas Cabang',
               'A' : 'Bank',
               'G' : 'Aktiva'}

class fCollectionReport:

  def __init__(self,formObj,parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.fSelectProgram = None
    self.fSelectDonor = None
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    
  def Show(self):
    uipFilter = self.uipFilter
    uipFilter.Edit()

    # Set Branch Filter
    IsHeadOffice = (uipFilter.BranchCode == uipFilter.HeadOfficeCode)
    #self.pFilter2_IsAllBranch.Enabled = IsHeadOffice
    #self.pFilter3_LBranch.Enabled = IsHeadOffice
    self.MasterBranchCode = ''

    if not IsHeadOffice :
      uipFilter.MasterBranchCode = uipFilter.BranchCode

    uipFilter.SetFieldValue('LBranch.BranchCode',uipFilter.BranchCode)
    uipFilter.SetFieldValue('LBranch.BranchName',uipFilter.BranchName)


    uipFilter.IsAllBranch = 'F'
    uipFilter.IsIncludeChildBranch = 'F'
    uipFilter.IsAllDonor = 'T'
    uipFilter.IsAllChannel = 'T'
    uipFilter.IsAllPettyCash = 'T'
    uipFilter.IsAllProgram = 'T'
    uipFilter.IsAllSponsor = 'T'
    uipFilter.IsAllVolunteer = 'T'
    uipFilter.IsAllFundEntity = 'T'
    uipFilter.IsAllMarketer = 'T'

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


  def ChannelCodeOnChange(self, sender):
    dictChannelCode = {0 : 'P', 1 : 'R', 2 : 'A', 3 : 'G'}
    self.SetPettyCashControl(dictChannelCode[sender.ItemIndex])

  def IsAllPettyCashClick(self, sender):
    self.SetPettyCashControl(self.uipFilter.ChannelCode)

  def SetPettyCashControl(self, ChannelCode):
    uipFilter = self.uipFilter

    self.pFilter3_IsAllPettyCash.visible = (ChannelCode == 'P')
    self.pFilter3_LPettyCash.visible = (ChannelCode == 'P')
    self.pFilter3_LPettyCash.enabled = (ChannelCode == 'P' and not self.pFilter3_IsAllPettyCash.Checked)
    if self.pFilter3_IsAllPettyCash.Checked:
      uipFilter.SetFieldValue('LPettyCash.AccountNo','')
      uipFilter.SetFieldValue('LPettyCash.AccountName','')

  def CheckClick(self,sender):
    form = self.form
    CtlNames = {
      'IsAllBranch' : ['LBranch','IsIncludeChildBranch'],
      'IsAllDonor' : ['NoDonor','NamaDonor','bSelectDonor'],
      'IsAllChannel' : ['ChannelCode', 'IsAllPettyCash', 'LPettyCash'],
      'IsAllProgram' : ['ProgramName','bSelectProgram'],
      'IsAllSponsor' : ['LSponsor'],
      'IsAllVolunteer' : ['LVolunteer'],
      'IsAllFundEntity' : ['FundEntity'],
      'IsAllMarketer' : ['LMarketer'],
    }
    
    for controlname in CtlNames[sender.Name] :
      form.GetPanelByName('pFilter3').GetControlByName(controlname).Visible = not sender.Checked

    self.SetPettyCashControl(self.uipFilter.ChannelCode or '')

  def CheckFilter(self):
    uipFilter = self.uipFilter

    if uipFilter.IsAllBranch == 'F' and (uipFilter.GetFieldValue('LBranch.BranchCode') or '') == '' :
       raise 'PERINGATAN','Silahkan pilih cabang terlebih dahulu'

    if uipFilter.IsAllDonor == 'F' and (uipFilter.IdDonor or 0) == 0 :
       raise 'PERINGATAN','Silahkan pilih donatur terlebih dahulu'
       
    if uipFilter.IsAllChannel == 'F' and (uipFilter.ChannelCode or '') == '' :
       raise 'PERINGATAN','Silahkan pilih jenis pembayaran terlebih dahulu'

    if uipFilter.IsAllProgram == 'F' and (uipFilter.AccountNo or '') == '' :
       raise 'PERINGATAN','Silahkan pilih program terlebih dahulu'
       
    if uipFilter.IsAllSponsor == 'F' and (uipFilter.GetFieldValue('LSponsor.SponsorId') or 0) == 0 :
       raise 'PERINGATAN','Silahkan pilih sponsor terlebih dahulu'

    if uipFilter.IsAllVolunteer == 'F' and (uipFilter.GetFieldValue('LVolunteer.VolunteerId') or 0) == 0 :
       raise 'PERINGATAN','Silahkan pilih mitra terlebih dahulu'

    if uipFilter.IsAllFundEntity == 'F' and (uipFilter.FundEntity or 0) == 0 :
       raise 'PERINGATAN','Silahkan pilih jenis dana terlebih dahulu'

    if uipFilter.IsAllMarketer == 'F' and (uipFilter.GetFieldValue('LMarketer.MarketerId') or 0) == 0 :
       raise 'PERINGATAN','Silahkan pilih marketer terlebih dahulu'

  def bPrintTextClick(self,sender):
    self.Cetak(1)
    
  def bPrintExcelClick(self,sender):
    self.Cetak(2)
    
  def Cetak(self,mode):
    app = self.app
    uipFilter = self.uipFilter
    if uipFilter.BeginDate > uipFilter.EndDate :
       raise 'PERINGATAN','Tanggal Awal tidak boleh lebih besar dari tanggal akhir'

    self.FormObject.CommitBuffer()
    self.CheckFilter()
    ph = self.FormObject.GetDataPacket()
    if mode == 1:
      resp = self.app.ExecuteScript('Report/S_CollectionReport.PrintText', ph)
      sw = resp.Packet.GetStreamWrapper(0)

      fileName = self.oPrint.ConfirmDestinationPath(app,'txt')
      if fileName in ['',None] : return

      sw.SaveToFile(fileName)

      self.app.ShellExecuteFile(fileName)
      
    else:
      filename = self.oPrint.ConfirmDestinationPath(app,'xls')
      if filename in ['',None] : return
      
      resp = self.app.ExecuteScript('Report/S_CollectionReport.GetDataTransaction', ph)

      status = resp.FirstRecord
      if status.Is_Err : raise 'Error',status.Err_Message

      workbook = self.oPrint.OpenExcelTemplate(app,'tplCollectionReport.xls')
      workbook.ActivateWorksheet('rekap')
      workbook.SetCellValue(3,3,status.ZakatBalance)
      workbook.SetCellValue(4,3,status.InfaqBalance)
      workbook.SetCellValue(5,3,status.WakafBalance)
      workbook.SetCellValue(6,3,status.AmilBalance)
      workbook.SetCellValue(7,3,status.OtherBalance)
      workbook.SetCellValue(15,10,status.WorkDays)
      workbook.SetCellValue(16,10,"( %s )" %status.Tanggal)

      workbook.ActivateWorksheet('data')
      try:

        workbook.SetCellValue(3, 3, status.Tanggal)
        workbook.SetCellValue(4, 3, status.TotalAmount)

        if uipFilter.IsAllBranch == 'F' :
          workbook.SetCellValue(2, 3, status.Cabang)

        if uipFilter.IsAllDonor == 'F' :
           workbook.SetCellValue(5, 3, uipFilter.NoDonor + ' - ' + uipFilter.NamaDonor)

        if uipFilter.IsAllFundEntity == 'F' :
           workbook.SetCellValue(6, 3, MAPEntity[uipFilter.FundEntity])

        if uipFilter.IsAllProgram == 'F' :
           workbook.SetCellValue(7, 3, uipFilter.ProgramName)

        if uipFilter.IsAllChannel == 'F' :
           workbook.SetCellValue(8, 3, uipFilter.GetFieldValue('LVolunteer.VolunteerName'))
           
        if uipFilter.IsAllChannel == 'F' :
           workbook.SetCellValue(9, 3, MAPChannel[uipFilter.ChannelCode])

        if uipFilter.IsAllMarketer == 'F' :
           workbook.SetCellValue(10, 3, uipFilter.GetFieldValue('LMarketer.Full_Name'))

        ds = resp.packet.ReportData
        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 13

          workbook.SetCellValue(row, 1, str(i+1))
          workbook.SetCellValue(row, 2, rec.TransactionDateStr)
          workbook.SetCellValue(row, 3, rec.SponsorName)
          workbook.SetCellValue(row, 4, rec.AccountName)
          workbook.SetCellValue(row, 5, rec.Description)
          workbook.SetCellValue(row, 6, rec.Channel)
          workbook.SetCellValue(row, 7, rec.Amount)
          workbook.SetCellValue(row, 8, rec.CurrencyCode)
          workbook.SetCellValue(row, 9, rec.Rate)
          workbook.SetCellValue(row, 10,rec.EkuivalenAmount)
          workbook.SetCellValue(row, 11,rec.FundEntity)
          workbook.SetCellValue(row, 12,rec.VolunteerName)
          workbook.SetCellValue(row, 13,rec.Marketer)
          workbook.SetCellValue(row, 14,rec.ReferenceNo)
          workbook.SetCellValue(row, 15,rec.Inputer)
          workbook.SetCellValue(row, 16,rec.BranchName)
          workbook.SetCellValue(row, 17,rec.TransactionNo)
          
          i += 1
        # end while

        workbook.SaveAs(filename)
      finally:
        workbook = None

      app.ShellExecuteFile(filename)

