import pyFlexcel

class fBudgetImport:
  def __init__(self,formObj,parentObj):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.filename = ''

  def Show(self):
    ph = self.app.CreateValues()

    rph = self.form.CallServerMethod('GetRefData',ph)

    dsPeriod = rph.packet.perioddata
    
    i= 0
    tempItems = []
    tempValues = []
    while i < dsPeriod.RecordCount:
      recPeriod = dsPeriod.GetRecord(i)
      tempItems.append(str(recPeriod.periodvalue))
      tempValues.append(str(recPeriod.periodid))
        #self.pNomor_cParamTRR.Items = '\r'.join(
        #  tempParam
        #)
        #self.pNomor_cParamTRR.Values = '\r'.join(
        #  tempParam
        #)
        
      #self.uipData.EnumeratedValues += "%i=%i#13" % (recPeriod.PeriodId,recPeriod.PeriodValue)
      i += 1

    self.pInput_Tahun.Items = '\r'.join(tempItems)
    self.pInput_Tahun.Values = '\r'.join(tempValues)
    self.FormContainer.Show()


  def bBrowseClick(self,sender):
    FileName = self.app.OpenFileDialog("Open file..", "Excel Files(*.xls)|*.xls")
    #if fileName.find(".xls") == -1 : fileName += ".xls

    if FileName != "":
      self.oleXLS.CreateObjectFromFile(FileName)
      self.filename = FileName


  def TahunOnChange(self,sender):
    #raise '',sender.Values
    #self.uipData.Edit()
    #self.uipData.Tahun = sender.Values
    pass
    
  def OkClick(self,sender):
    app = self.app
    form = self.form
    
    if self.filename == '' :
      raise 'PERINGATAN','File data belum diinputkan'
      
    workbook = pyFlexcel.Open(self.filename)
    workbook.ActivateWorksheet('data')

    ph = app.CreatePacket()

    ds = ph.Packet.AddNewDatasetEx(
        'budgetdata',
        ';'.join(
        ['owner_code:string' ,
         'ItemGroup:string',
         'itemname:string',
         'budget_code:string',
         'no:integer',
         'amount1:float',
         'amount2:float',
         'amount3:float',
         'amount4:float',
         'amount5:float',
         'amount6:float',
         'amount7:float',
         'amount8:float',
         'amount9:float',
         'amount10:float',
         'amount11:float',
         'amount12:float'
        ])
    )

    try :
      uipBudgetDetail = self.uipBudgetDetail
      uipBudgetDetail.ClearData()
      row = 12
      PrevItemGroup = ''
      while workbook.GetCellValue(row, 1) not in ['',None]:
        uipBudgetDetail.Append()
        #rec = ds.AddRecord()
        uipBudgetDetail.RowNumber = workbook.GetCellValue(row, 1)
        uipBudgetDetail.OwnerCode = str(workbook.GetCellValue(row, 2))

        ItemGroup = workbook.GetCellValue(row, 3)

        if ItemGroup == None :
          ItemGroup = PrevItemGroup

        if ItemGroup != PrevItemGroup :
          PrevItemGroup = ItemGroup
          
        uipBudgetDetail.ItemGroup = str(ItemGroup)
        uipBudgetDetail.ItemName = str(workbook.GetCellValue(row, 4))
        uipBudgetDetail.BudgetCode = str(workbook.GetCellValue(row, 5))
        uipBudgetDetail.Amount1 = workbook.GetCellValue(row, 6) or 0.0
        uipBudgetDetail.Amount2 = workbook.GetCellValue(row, 7) or 0.0
        uipBudgetDetail.Amount3 = workbook.GetCellValue(row, 8) or 0.0
        uipBudgetDetail.Amount4 = workbook.GetCellValue(row, 9) or 0.0
        uipBudgetDetail.Amount5 = workbook.GetCellValue(row, 10) or 0.0
        uipBudgetDetail.Amount6 = workbook.GetCellValue(row, 11) or 0.0
        uipBudgetDetail.Amount7 = workbook.GetCellValue(row, 12) or 0.0
        uipBudgetDetail.Amount8 = workbook.GetCellValue(row, 13) or 0.0
        uipBudgetDetail.Amount9 = workbook.GetCellValue(row, 14) or 0.0
        uipBudgetDetail.Amount10 = workbook.GetCellValue(row, 15) or 0.0
        uipBudgetDetail.Amount11 = workbook.GetCellValue(row, 16) or 0.0
        uipBudgetDetail.Amount12 = workbook.GetCellValue(row, 17) or 0.0
        
        row += 1
      # end while
      form.CommitBuffer()

      rph = form.CallServerMethod('ExecuteImport',form.GetDataPacket())
      
      status = rph.FirstRecord
      if status.Is_Err : raise 'PERINGATAN',status.Err_Message
      
      app.ShowMessage('Data budget berhasil diimport')
      sender.ExitAction = 1

    finally:
      workbook = None
    
