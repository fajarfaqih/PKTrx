class fFixedAssetList:
  #--- FORM EVENT

  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    self.FormView = None

  def AssetTypeChange(self,sender):
    self.pFilter_LProductAccount.Enabled = sender.ItemIndex == 0
    if sender.ItemIndex == 1 :
      self.uipData.SetFieldValue('LProductAccount.ProductCode','')
      self.uipData.SetFieldValue('LProductAccount.ProductName','')
      
  def IsAllAssetOnClick(self,sender):
    lsControl = ['AssetType','LAssetCategory','LProductAccount','BeginDate','EndDate']
    for controlname in lsControl :
      self.form.GetPanelByName('pFilter').GetControlByName(controlname).Enabled = not sender.Checked

    #if sender.Checked != 0 : self.ShowFixedAssetData()

  def FilterClick(self,sender):
    self.uipFixedAsset.ClearData()
    self.ShowFixedAssetData()

  def bExportExcel(self,sender):
    self.ShowFixedAssetData(1)

  def Show(self):
    self.uipData.Edit()
    self.uipData.AssetType = 'N'
    self.uipData.IsAllAsset = 'T'
    self.AssetTypeChange(self.pFilter_AssetType)
    
    self.ShowFixedAssetData()
    self.FormContainer.Show()

  #--- FORM METHOD
  def ViewData(self):
    if self.FormView == None :
      form = self.app.CreateForm(
          'DepreciableAsset/fFixedAssetView',
          'DepreciableAsset/fFixedAssetView',
           0, None, None)
      self.FormView = form
    else:
      form = self.FormView
    # end if
    
    AccountNo = self.uipFixedAsset.AccountNo
    form.Show(AccountNo)


  def ShowFixedAssetData(self,mode = 0):
    app = self.app
    form = self.form
    uipData = self.uipData

    IsAllAsset = uipData.IsAllAsset
    AssetType = uipData.AssetType
    AccountProduct = uipData.GetFieldValue('LProductAccount.AccountNo') or ''
    AssetCategoryId = uipData.GetFieldValue('LAssetCategory.AssetCategoryId') or ''
    BeginDate = uipData.BeginDate
    EndDate = uipData.EndDate

    BranchCode = self.uipData.BranchCode

    param = self.app.CreateValues(
     ['IsAllAsset',IsAllAsset],
     ['BranchCode',BranchCode],
     ['AssetType',AssetType],
     ['AssetCategoryId',AssetCategoryId],
     ['AccountProduct',AccountProduct],
     ['BeginDate',BeginDate],
     ['EndDate',EndDate],
    )

    if mode == 0 :
      self.form.SetDataWithParameters(param)
    else:
      filename = self.oPrint.ConfirmDestinationPath(app,'xls')
      if filename in ['',None] : return
      
      ph = self.form.CallServerMethod("GetAssetList", param)

      status = ph.FirstRecord
      if status.Is_Err : raise 'PERINGATAN',status.Err_Message

      workbook = self.oPrint.OpenExcelTemplate(app,'tplAssetList.xls')
      workbook.ActivateWorksheet('data')
      try:
        workbook.SetCellValue(2, 3, status.BranchName)
        if IsAllAsset == 'F' :
          workbook.SetCellValue(3, 3, status.PeriodStr)
          workbook.SetCellValue(4, 3, status.AssetTypeName)
          CategoryName = uipData.GetFieldValue('LAssetCategory.AssetCategoryName') or ''
          if CategoryName != '' :
            workbook.SetCellValue(5, 3,  CategoryName)
        
        ds = ph.packet.AssetList
        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          row = i + 8

          workbook.SetCellValue(row, 1, str(i+1))
          workbook.SetCellValue(row, 2, rec.AccountNo)
          workbook.SetCellValue(row, 3, rec.AccountName)
          workbook.SetCellValue(row, 4, rec.NilaiAwal)
          workbook.SetCellValue(row, 5, rec.Balance)
          workbook.SetCellValue(row, 6, rec.TotalPenyusutan)
          workbook.SetCellValue(row, 7, rec.OpeningDate)
          workbook.SetCellValue(row, 8, rec.ProductName)
          workbook.SetCellValue(row, 9, rec.TransactionNo)
          workbook.SetCellValue(row, 10, rec.AssetTypeName)
          workbook.SetCellValue(row, 11, rec.AssetCategoryName)

          i += 1
        # end of while


        workbook.SaveAs(filename)
        app.ShellExecuteFile(filename)

      finally:
        # close
        workbook = None

