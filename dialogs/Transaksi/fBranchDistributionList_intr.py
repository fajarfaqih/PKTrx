class fBranchDistributionList:
  def __init__(self,formObj,parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.TransactionItemId = 0
    self.Amount = 0.0
    self.Description = ''
    self.Tgl = None
    self.TransactionItemId = None
    self.TransactionNo = None
    self.TransactionDate = None
    self.Amount = None
    self.Description = None
    self.fReturnTrans = None
    self.fCADetail = None
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

  def GetTransaction(self,BranchCode):
    self.uipFilter.Edit()
    self.DisplayTransaction()
    
    st = self.FormContainer.Show()
    if st == 1 :
      return 1

    return 0

  def Show(self):
    uipFilter = self.uipFilter
    uipFilter.Edit()
    uipFilter.IsReportedShow = 'F'

    IsHeadOffice = (uipFilter.BranchCode == uipFilter.HeadOfficeCode)
    self.MasterBranchCode = ''
    if not IsHeadOffice :
      uipFilter.MasterBranchCode = uipFilter.BranchCode

    self.DisplayTransaction()
    self.FormContainer.Show()
    
  def bApplyClick(self,sender):
    self.DisplayTransaction()

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
    

  def CreateReturnTransactionClick(self,sender):
    app = self.app
    form = self.form
    
    TransactionNo = self.uipDistributionList.TransactionNo or ''
    
    if TransactionNo == '' : return
    
    if self.fReturnTrans == None :
      form = app.CreateForm('Transaksi/fBranchDistributionReturn',
                            'Transaksi/fBranchDistributionReturn',
                            0,None,None)
      self.fReturnTrans = form
    else:
      form = self.fReturnTrans
    # end if
    
    if form.CreateReturnTrans(TransactionNo):
      pass
    # end if
    
  def DetilUMClick(self,sender):
    DistributionId = self.uipDistributionList.DistributionId or 0
    
    if DistributionId == 0 : return
    
    if self.fCADetail == None :
      form = self.app.CreateForm('Transaksi/fDistCADetail',
                            'Transaksi/fDistCADetail',
                            0,None,None)
      self.fCADetail = form
    else:
      form = self.fCADetail
    # end if


    form.ShowDetail(DistributionId)


  def GenerateParamFromFilter(self):
    app = self.app
    uipFilter = self.uipFilter

    SourceBranchCode = uipFilter.GetFieldValue('LSourceBranch.BranchCode') or ''
    DestBranchCode = uipFilter.GetFieldValue('LDestBranch.BranchCode') or ''
    IsReportedShow = uipFilter.IsReportedShow
    ph = app.CreateValues(
      ['BeginDate',uipFilter.BeginDate],
      ['EndDate',uipFilter.EndDate],
      ['SourceBranchCode',SourceBranchCode],
      ['DestBranchCode',DestBranchCode],
      ['IsReportedShow',IsReportedShow]
    )

    return ph
    
  def DisplayTransaction(self):
    app = self.app

    ph = self.GenerateParamFromFilter()
    self.form.SetDataWithParameters(ph)

  def GridDoubleClick(self,sender):
    self.ProsesClick(self.pAction_bPilih)
    
  def ProsesClick(self,sender):
    self.FormObject.Close(1)
