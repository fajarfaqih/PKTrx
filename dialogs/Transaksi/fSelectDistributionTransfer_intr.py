class fSelectDistributionTransfer:
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


  def GetTransaction(self,DistType='IN'):
    # DistType ==> 'IN' atau 'OUT'
    
    self.uipFilter.Edit()
    self.uipFilter.DistType = DistType
    self.DisplayTransaction()

    SourceBranch = self.pFilter_LSourceBranch
    DestBranch = self.pFilter_LDestBranch
    
    SourceBranch.Visible = ( DistType == 'IN' )
    SourceBranch.Top = 38
    DestBranch.Visible = ( DistType == 'OUT' )
    DestBranch.Top = 38
    
    st = self.FormContainer.Show()
    if st == 1 :
      return 1

    return 0

  def Show(self):
    self.DisplayTransaction()
    self.FormContainer.Show()
    
  def bApplyFilterClick(self,sender):
    self.DisplayTransaction()

  def DisplayTransaction(self):
    app = self.app
    uipFilter = self.uipFilter
    
    SourceBranchCode = self.uipFilter.GetFieldValue('LSourceBranch.BranchCode') or ''
    DestBranchCode = self.uipFilter.GetFieldValue('LDestBranch.BranchCode') or ''
    
    ph = app.CreateValues(
      ['BeginDate', uipFilter.BeginDate],
      ['EndDate', uipFilter.EndDate],
      ['SourceBranchCode', SourceBranchCode],
      ['DestBranchCode', DestBranchCode],
      ['DistType', uipFilter.DistType]
    )
    
    self.form.SetDataWithParameters(ph)
    
  def GridDoubleClick(self,sender):
    self.bPilihClick(self.pAction_bPilih)
    
  def bPilihClick(self,sender):
    uipList = self.uipDistributionList
    
    if uipList.ReportStatus == 'T' and self.uipFilter.DistType == 'OUT' :
      raise 'PERINGATAN', 'Transaksi ini sudah memiliki LPJ'
    
    self.FormObject.Close(1)
    
