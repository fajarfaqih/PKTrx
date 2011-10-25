class fCIAList:
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.FormView = None
    
  def Show(self):
    self.ShowFixedAssetData()
    self.FormContainer.Show()

  def ViewData(self):
    if self.FormView == None :
      form = self.app.CreateForm(
          'DepreciableAsset/fCIAView',
          'DepreciableAsset/fCIAView',
           0, None, None)
      self.FormView = form
    else:
      form = self.FormView
    # end if
    AccountNo = self.qFixedAsset.GetFieldValue('FixedAsset.AccountNo')
    form.Show(AccountNo)

  def FilterClick(self,sender):
    self.ShowFixedAssetData()
    
    
  def ShowFixedAssetData(self):
    qCPIA = self.qCPIA
    uipData = self.uipData
    AddParam = ''
    
    AccountProduct = uipData.GetFieldValue('LProductAccount.AccountNo') or ''
    if AccountProduct != '' :
      AddParam += " and AccountNoProduct='%s' " % AccountProduct

    BranchCode = self.uipData.BranchCode
    qCPIA.OQLText = " select from CostPaidInAdvance \
      [ BranchCode = '%s' \
        %s] \
      ( AccountNo, \
        AccountName, \
        LProductAccount.AccountName as ProductName, \
        NilaiAwal, \
        Qty, \
        self \
      ) ;" % (BranchCode,AddParam)
      
    qCPIA.DisplayData()
    
