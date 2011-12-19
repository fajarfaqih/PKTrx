class fInvestmentTransList:
  def __init__(self,formObj,parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

  def Show(self):
    uipFilter = self.uipFilter
    uipFilter.Edit()

    IsHeadOffice = (uipFilter.BranchCode == uipFilter.HeadOfficeCode)
    self.MasterBranchCode = ''
    if not IsHeadOffice :
      uipFilter.MasterBranchCode = uipFilter.BranchCode

    self.DisplayTransaction()
    self.FormContainer.Show()
    
  def bApplyClick(self,sender):
    self.DisplayTransaction()

  def GenerateParamFromFilter(self):
    app = self.app
    uipFilter = self.uipFilter
    
    BeginDate = uipFilter.BeginDate or 0
    if BeginDate == 0 :
      raise 'PERINGATAN', 'Inputkan Tanggal Awal'
    
    EndDate = uipFilter.EndDate or 0
    if EndDate == 0 :
      raise 'PERINGATAN', 'Inputkan Tanggal Akhir'
      
    if EndDate < BeginDate :
      raise 'PERINGATAN', 'Tanggal Awal tidak boleh lebih besar dari Tanggal Akhir'
      
    ph = app.CreateValues(
      ['BeginDate',BeginDate],
      ['EndDate',EndDate],
    )

    return ph

  def DisplayTransaction(self):
    app = self.app

    ph = self.GenerateParamFromFilter()
    self.form.SetDataWithParameters(ph)

  def bExcelClick(self,sender):
    app = self.app
    uipFilter = self.uipFilter

    resp = self.form.CallServerMethod('GetExcelData',self.GenerateParamFromFilter())

    status = resp.FirstRecord

    if status.Is_Err :
      raise 'PERINGATAN',status.Err_Message

    sw = resp.Packet.GetStreamWrapper(0)

    fileName = self.oPrint.ConfirmDestinationPath(app,'xls')

    if fileName in ['',None,0] :
      return

    sw.SaveToFile(fileName)
    self.app.ShellExecuteFile(fileName)


