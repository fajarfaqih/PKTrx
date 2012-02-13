import pyFlexcel

class fSaldoAwal:
  def __init__(self,formObj,parentObj):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    
  # -- FORM EVENT --
  def BrowseClick(self,sender):
    FileName = self.app.OpenFileDialog("Open file..", "Excel Files(*.xls)|*.xls")

    if FileName != "":
      self.uipData.Edit()
      self.uipData.FileName = FileName

  def UploadDataClick(self,sender):
    app = self.app
    form = self.form
    uipData = self.uipData

    form.CommitBuffer()

    AccountType = uipData.AccountType or 0
    if AccountType == 0 :
      raise 'Peringatan','Silahkan pilih jenis rekening'

    if uipData.FileName == '' :
      raise 'Peringatan','Silahkan pilih file data saldo'


    ph = app.CreatePacket()
    dsHeader = ph.Packet.AddNewDatasetEx(
      'HeaderData',
      ';'.join(
        ['AccountType:integer',
         'BranchCode:string'
        ]
      )
    )
    
    recHeader = dsHeader.AddRecord()
    recHeader.AccountType = AccountType
    recHeader.BranchCode = uipData.GetFieldValue('LBranch.BranchCode')

    filename = uipData.FileName
    if AccountType == 1 :
      param = self.ConvertFileToPacket1(ph,filename)
    elif AccountType == 2 :
      param = self.ConvertFileToPacket2(ph,filename)
    elif AccountType == 3 :
      param = self.ConvertFileToPacket3(ph,filename)
    elif AccountType == 4 :
      param = self.ConvertFileToPacket4(ph,filename)
    elif AccountType == 5 :
      param = self.ConvertFileToPacket5(ph,filename)
    elif AccountType == 6 :
      param = self.ConvertFileToPacket6(ph,filename)
    elif AccountType == 7 :
      param = self.ConvertFileToPacket6(ph,filename)
    elif AccountType == 8 :
      param = self.ConvertFileToPacket8(ph,filename)
    # end if

    resp = form.CallServerMethod('UploadData',param)
    status = resp.FirstRecord
    if status.Is_Err : raise 'PERINGATAN',status.Err_Message
    
    app.ShowMessage('Data Saldo Telah Berhasil di Upload')
      
  def DownloadTemplateClick(self,sender):
    app = self.app
    form = self.form
    uipData = self.uipData
    
    form.CommitBuffer()
    
    AccountType = uipData.AccountType or 0
    if AccountType == 0 :
      raise 'Peringatan','Silahkan pilih jenis rekening'
    
    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename in ['',None] : return

    resp = form.CallServerMethod('GetTemplate',form.GetDataPacket())
    
    status = resp.FirstRecord
    if status.Is_Err : raise 'Peringatan',status.Err_Message
    
    if AccountType == 1 :
      self.ShowTemplateCashAccount(resp,filename)
    elif AccountType == 2 :
      self.ShowTemplateProgram(resp,filename)
    elif AccountType == 3 :
      self.ShowTemplateProject(resp,filename)
    elif AccountType == 4 :
      self.ShowTemplateEmployeeAR(resp,filename)
    elif AccountType == 5 :
      self.ShowTemplateExternalAR(resp,filename)
    elif AccountType == 6 :
      self.ShowTemplateEmployeeInvestment(resp,filename)
    elif AccountType == 7 :
      self.ShowTemplateExternalInvestment(resp,filename)
    elif AccountType == 8 :
      self.ShowTemplateFixedAsset(resp,filename)
    # end if
    
    app.ShellExecuteFile(filename)
    
  # -- USER DEFINE METHOD --

  def Show(self):
    uipData = self.uipData
    uipData.Edit()
    
    IsHeadOffice = (uipData.BranchCode == uipData.HeadOfficeCode)
    self.pOption_LBranch.Enabled = IsHeadOffice
    self.MasterBranchCode = ''

    if not IsHeadOffice :
      uipData.MasterBranchCode = uipData.BranchCode

    uipData.SetFieldValue('LBranch.BranchCode', uipData.BranchCode)
    uipData.SetFieldValue('LBranch.BranchName', uipData.BranchName)
    
    self.FormContainer.Show()

  # ------------------ FUNCTION FOR SHOW FILE DATA
  def ShowTemplateCashAccount(self,resp,filename):
    app = self.app
    workbook = self.oPrint.OpenExcelTemplate(app,'tplBBalanceCashBank.xls')
    workbook.ActivateWorksheet('data')
    try:

      workbook.SetCellValue(2, 3, resp.FirstRecord.BranchName)

      ds = resp.packet.ListAccount
      TotalAccount = ds.RecordCount
      i = 0
      while i < TotalAccount:
        rec = ds.GetRecord(i)
        row = i + 5

        workbook.SetCellValue(row, 1, i+1)
        workbook.SetCellValue(row, 2, rec.AccountNo)
        workbook.SetCellValue(row, 3, rec.AccountName)
        workbook.SetCellValue(row, 4, rec.Currency)
        workbook.SetCellValue(row, 5, rec.Rate)
        workbook.SetCellValue(row, 6, rec.Balance)

        i += 1
      # end of while

      workbook.SaveAs(filename)
    finally:
      # close
      workbook = None

  def ShowTemplateProgram(self,resp,filename):
    app = self.app
    workbook = self.oPrint.OpenExcelTemplate(app,'tplBBalanceProgram.xls')
    workbook.ActivateWorksheet('data')
    try:

      workbook.SetCellValue(2, 3, resp.FirstRecord.BranchName)

      ds = resp.packet.ListAccount
      TotalAccount = ds.RecordCount
      i = 0
      while i < TotalAccount:
        rec = ds.GetRecord(i)
        row = i + 5

        workbook.SetCellValue(row, 1, i+1)
        workbook.SetCellValue(row, 2, rec.AccountNo)
        workbook.SetCellValue(row, 3, rec.AccountName)
        workbook.SetCellValue(row, 4, rec.Currency)
        workbook.SetCellValue(row, 5, rec.Balance)

        i += 1
      # end of while

      workbook.SaveAs(filename)
    finally:
      # close
      workbook = None
      
  def ShowTemplateProject(self,resp,filename):
    app = self.app
    workbook = self.oPrint.OpenExcelTemplate(app,'tplBBalanceProject.xls')
    workbook.ActivateWorksheet('data')
    try:

      workbook.SetCellValue(2, 3, resp.FirstRecord.BranchName)

      ds = resp.packet.ListAccount
      TotalAccount = ds.RecordCount
      i = 0
      while i < TotalAccount:
        rec = ds.GetRecord(i)
        row = i + 5

        workbook.SetCellValue(row, 1, i+1)
        workbook.SetCellValue(row, 2, rec.AccountNo)
        workbook.SetCellValue(row, 3, rec.AccountName)
        workbook.SetCellValue(row, 4, str(rec.SponsorId))
        workbook.SetCellValue(row, 5, rec.SponsorName)
        workbook.SetCellValue(row, 6, rec.Currency)
        workbook.SetCellValue(row, 7, rec.Balance)
        i += 1
      # end of while

      workbook.SaveAs(filename)
    finally:
      # close
      workbook = None
      
  def ShowTemplateEmployeeAR(self,resp,filename):
    app = self.app
    workbook = self.oPrint.OpenExcelTemplate(app,'tplBBalanceEmployeeAR.xls')
    workbook.ActivateWorksheet('data')
    try:

      workbook.SetCellValue(2, 3, resp.FirstRecord.BranchName)

      ds = resp.packet.ListAccount
      TotalAccount = ds.RecordCount
      i = 0
      while i < TotalAccount:
        rec = ds.GetRecord(i)
        row = i + 5

        workbook.SetCellValue(row, 1, i+1)
        workbook.SetCellValue(row, 2, rec.AccountNo)
        workbook.SetCellValue(row, 3, rec.AccountName)
        workbook.SetCellValue(row, 4, rec.Balance)

        i += 1
      # end of while

      workbook.SaveAs(filename)
    finally:
      # close
      workbook = None

  def ShowTemplateExternalAR(self,resp,filename):
    app = self.app
    workbook = self.oPrint.OpenExcelTemplate(app,'tplBBalanceExternalAR.xls')
    workbook.ActivateWorksheet('data')
    try:

      workbook.SetCellValue(2, 3, resp.FirstRecord.BranchName)

      ds = resp.packet.ListAccount
      TotalAccount = ds.RecordCount
      i = 0
      while i < TotalAccount:
        rec = ds.GetRecord(i)
        row = i + 5

        workbook.SetCellValue(row, 1, i+1)
        workbook.SetCellValue(row, 2, rec.AccountNo)
        workbook.SetCellValue(row, 3, rec.AccountName)
        workbook.SetCellValue(row, 4, rec.Balance)

        i += 1
      # end of while

      workbook.SaveAs(filename)
    finally:
      # close
      workbook = None

  def ShowTemplateEmployeeInvestment(self,resp,filename):
    app = self.app
    workbook = self.oPrint.OpenExcelTemplate(app,'tplBBalanceEmployeeInvestment.xls')
    workbook.ActivateWorksheet('data')
    try:

      workbook.SetCellValue(2, 3, resp.FirstRecord.BranchName)

      ds = resp.packet.ListAccount
      TotalAccount = ds.RecordCount
      i = 0
      while i < TotalAccount:
        rec = ds.GetRecord(i)
        row = i + 6

        workbook.SetCellValue(row, 1, i+1)
        workbook.SetCellValue(row, 2, rec.AccountNo)
        workbook.SetCellValue(row, 3, rec.AccountName)
        workbook.SetCellValue(row, 4, rec.CatCode)
        workbook.SetCellValue(row, 5, rec.CatName)
        workbook.SetCellValue(row, 6, rec.InvestAmount)
        workbook.SetCellValue(row, 7, rec.Balance)
        workbook.SetCellValue(row, 8, rec.StartDate)
        workbook.SetCellValue(row, 9, rec.LifeTime)
        workbook.SetCellValue(row, 10, rec.Nisbah)

        i += 1
      # end of while

      workbook.SaveAs(filename)
    finally:
      # close
      workbook = None

  def ShowTemplateExternalInvestment(self,resp,filename):
    app = self.app
    workbook = self.oPrint.OpenExcelTemplate(app,'tplBBalanceExternalInvestment.xls')
    workbook.ActivateWorksheet('data')
    try:

      workbook.SetCellValue(2, 3, resp.FirstRecord.BranchName)

      ds = resp.packet.ListAccount
      TotalAccount = ds.RecordCount
      i = 0
      while i < TotalAccount:
        rec = ds.GetRecord(i)
        row = i + 6

        workbook.SetCellValue(row, 1, i+1)
        workbook.SetCellValue(row, 2, rec.AccountNo)
        workbook.SetCellValue(row, 3, rec.AccountName)
        workbook.SetCellValue(row, 4, rec.CatCode)
        workbook.SetCellValue(row, 5, rec.CatName)
        workbook.SetCellValue(row, 6, rec.InvestAmount)
        workbook.SetCellValue(row, 7, rec.Balance)
        workbook.SetCellValue(row, 8, rec.StartDate)
        workbook.SetCellValue(row, 9, rec.LifeTime)
        workbook.SetCellValue(row, 10, rec.Nisbah)

        i += 1
      # end of while

      workbook.SaveAs(filename)
    finally:
      # close
      workbook = None
      
  def ShowTemplateFixedAsset(self,resp,filename):
    app = self.app
    workbook = self.oPrint.OpenExcelTemplate(app,'tplBBalanceFixAsset.xls')
    workbook.ActivateWorksheet('data')
    try:
      workbook.SaveAs(filename)
    finally:
      # close
      workbook = None
      
  # ------------------ FUNCTION FOR CONVERT TO DATAPACKET
  def ConvertFileToPacket1(self,ph,filename):
    app = self.app
    dsBalance = ph.Packet.AddNewDatasetEx(
      'BalanceData',
      ';'.join([
        'AccountNo:string',
        'AccountName:string',
        'Balance:float',
        'Rate:float',
      ])
    )
    
    workbook = pyFlexcel.Open(filename)
    workbook.ActivateWorksheet('data')
    try:
      row = 5
      while workbook.GetCellValue(row, 1) not in ['',None]:
        recBalance = dsBalance.AddRecord()
        recBalance.AccountNo = str(workbook.GetCellValue(row, 2))
        recBalance.AccountName = str(workbook.GetCellValue(row, 3))
        recBalance.Rate = workbook.GetCellValue(row, 5)
        recBalance.Balance = workbook.GetCellValue(row, 6)
        
        row += 1
      # end while
    finally:
      workbook = None


    return ph
    
  def ConvertFileToPacket2(self,ph,filename):
    app = self.app
    dsBalance = ph.Packet.AddNewDatasetEx(
      'BalanceData',
      ';'.join([
        'AccountNo:string',
        'AccountName:string',
        'Balance:float',
      ])
    )

    workbook = pyFlexcel.Open(filename)
    workbook.ActivateWorksheet('data')
    try:
      row = 5
      while workbook.GetCellValue(row, 1) not in ['',None]:
        recBalance = dsBalance.AddRecord()
        recBalance.AccountNo = str(workbook.GetCellValue(row, 2))
        recBalance.AccountName = str(workbook.GetCellValue(row, 3))
        recBalance.Balance = workbook.GetCellValue(row, 5)

        row += 1
      # end while
    finally:
      workbook = None

    return ph

  def ConvertFileToPacket3(self,ph,filename):
    app = self.app
    dsBalance = ph.Packet.AddNewDatasetEx(
      'BalanceData',
      ';'.join([
        'AccountNo:string',
        'AccountName:string',
        'SponsorId:integer',
        'SponsorName:string',
        'Balance:float',
      ])
    )

    workbook = pyFlexcel.Open(filename)
    workbook.ActivateWorksheet('data')
    try:
      row = 5
      while workbook.GetCellValue(row, 1) not in ['',None]:
        recBalance = dsBalance.AddRecord()
        recBalance.AccountNo = str(workbook.GetCellValue(row, 2))
        recBalance.AccountName = str(workbook.GetCellValue(row, 3))
        recBalance.SponsorId = int(workbook.GetCellValue(row, 4))
        recBalance.SponsorName = str(workbook.GetCellValue(row, 5))
        recBalance.Balance = workbook.GetCellValue(row, 7)

        row += 1
      # end while
    finally:
      workbook = None

    return ph
    
  def ConvertFileToPacket4(self,ph,filename):
    app = self.app
    dsBalance = ph.Packet.AddNewDatasetEx(
      'BalanceData',
      ';'.join([
        'AccountNo:integer',
        'AccountName:string',
        'Balance:float',
      ])
    )

    workbook = pyFlexcel.Open(filename)
    workbook.ActivateWorksheet('data')
    try:
      row = 5
      while workbook.GetCellValue(row, 1) not in ['',None]:
        recBalance = dsBalance.AddRecord()
        recBalance.AccountNo = int(workbook.GetCellValue(row, 2))
        recBalance.AccountName = str(workbook.GetCellValue(row, 3))
        recBalance.Balance = workbook.GetCellValue(row, 4)

        row += 1
      # end while
    finally:
      workbook = None

    return ph
    
  def ConvertFileToPacket5(self,ph,filename):
    app = self.app
    dsBalance = ph.Packet.AddNewDatasetEx(
      'BalanceData',
      ';'.join([
        'AccountNo:integer',
        'AccountName:string',
        'Balance:float',
      ])
    )

    workbook = pyFlexcel.Open(filename)
    workbook.ActivateWorksheet('data')
    try:
      row = 5
      while workbook.GetCellValue(row, 1) not in ['',None]:
        recBalance = dsBalance.AddRecord()
        recBalance.AccountNo = int(workbook.GetCellValue(row, 2))
        recBalance.AccountName = str(workbook.GetCellValue(row, 3))
        recBalance.Balance = workbook.GetCellValue(row, 4)

        row += 1
      # end while
    finally:
      workbook = None

    return ph
    
  def ConvertFileToPacket6(self,ph,filename):
    app = self.app
    dsBalance = ph.Packet.AddNewDatasetEx(
      'BalanceData',
      ';'.join([
        'AccountNo:integer',
        'AccountName:string',
        'CatCode: string',
        'CatName: string',
        'InvestAmount: float',
        'Balance: float',
        'StartDate: datetime',
        'LifeTime: integer',
        'Nisbah: float',
      ])
    )

    workbook = pyFlexcel.Open(filename)
    workbook.ActivateWorksheet('data')
    try:
      row = 6
      while workbook.GetCellValue(row, 1) not in ['',None]:
        recBalance = dsBalance.AddRecord()
        recBalance.AccountNo = int(workbook.GetCellValue(row, 2))
        recBalance.AccountName = str(workbook.GetCellValue(row, 3))
        recBalance.CatCode = str(workbook.GetCellValue(row, 4))
        recBalance.CatName = str(workbook.GetCellValue(row, 5))

        recBalance.InvestAmount = workbook.GetCellValue(row, 6)
        if recBalance.InvestAmount <= 0 : raise 'PERINGATAN','Data Nilai Investasi Untuk Data No %d belum diinputkan ' % (row - 5)
        
        recBalance.Balance = workbook.GetCellValue(row, 7)
        recBalance.StartDate = workbook.GetCellValue(row, 8)

        recBalance.LifeTime = workbook.GetCellValue(row, 9)
        if recBalance.LifeTime <= 0 : raise 'PERINGATAN','Data Jangka Waktu Untuk Data No %d belum diinputkan ' % (row - 5)

        recBalance.Nisbah = workbook.GetCellValue(row, 10)
        if recBalance.Nisbah <= 0 : raise 'PERINGATAN','Data Nisbah Untuk Data No %d belum diinputkan ' % (row - 5)

        row += 1
      # end while
    finally:
      workbook = None

    return ph
    
  def ConvertFileToPacket8(self,ph,filename):
    app = self.app
    dsBalance = ph.Packet.AddNewDatasetEx(
      'BalanceData',
      ';'.join([
        'AssetName:string',
        'AssetCategoryId: integer',
        'StartDate: datetime',
        'Amount: float',
        'DeprAmount: float',
        'AccumDeprAmount: float',
      ])
    )

    workbook = pyFlexcel.Open(filename)
    workbook.ActivateWorksheet('data')
    try:
      row = 5
      while workbook.GetCellValue(row, 1) not in ['',None]:
        recBalance = dsBalance.AddRecord()
        recBalance.AssetName = str(workbook.GetCellValue(row, 2))
        recBalance.AssetCategoryId = int(workbook.GetCellValue(row, 3))
        recBalance.StartDate = workbook.GetCellValue(row, 4)
        recBalance.Amount = workbook.GetCellValue(row, 5)
        recBalance.DeprAmount = workbook.GetCellValue(row, 6)
        recBalance.AccumDeprAmount = workbook.GetCellValue(row, 7)

        row += 1
      # end while
    finally:
      workbook = None

    return ph
