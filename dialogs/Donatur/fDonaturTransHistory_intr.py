PI_NONE = -1
PI_INDIVIDU = 0
PI_CORPORATE = 1

class fDonaturTransHistory :
    def __init__(self, formObj, parentForm, mode) :
       self.app = formObj.ClientApplication
       self.form = formObj
       self.ObjectAccess = self.app.GetClientClass("ClientObjectAccess", "ObjectAccess")()
       self.mode = mode
       self.ParamDisplay = {
        'New':'self.DisplayNew()',
        'Edit':'self.DisplayEdit()',
        'View':'self.DisplayView()',
        'SENTINEL':''
       }
       self.SearchForm = None
       self.DonorNo = None
       self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()


    def SwitchDisplay(self, ModeDisplay) :
      self.uipFilter.Edit()
      self.uipFilter.ViewType = ModeDisplay
      if ModeDisplay == 'I' :
        PI = PI_INDIVIDU
      else :
        PI = PI_CORPORATE
      NOTPI = divmod(PI+1,2)[1]
      mpPeragaan = self.mpPeragaan
      for i in range(mpPeragaan.PageCount):
          mpPeragaan.GetPage(i).TabVisible = i != NOTPI

      mpPeragaan.ActivePageIndex = PI
      
    def SetEnabled (self) :
      self.pAction_bClose.Enabled = 1
      self.pTransFilter_TglAwal.Enabled = 1
      self.pTransFilter_TglAkhir.Enabled = 1
      self.pTransFilter_bView.Enabled = 1

    def DisplayPage(self,PageIdx) :
      mpPeragaan = self.mpPeragaan
      for i in range(mpPeragaan.PageCount):
          mpPeragaan.GetPage(i).TabVisible = i == PageIdx

      mpPeragaan.ActivePageIndex = PageIdx

    def DisplayNew(self) :
      self.FormObject.SetAllControlsReadOnly()
      self.pInput_Input_Data.Enabled = 1
      self.pInput_Data.Enabled = 1
      self.SetEnabled()
      self.DisplayPage(PI_NONE)

    def DisplayEdit(self) :
      self.FormObject.GetPanelByName('pData').GetControlByName(self.uipData.ID+'ID').ReadOnly = 1

    def DisplayView(self) :
      self.FormObject.SetAllControlsReadOnly()
      self.SetEnabled()
      self.SwitchDisplay(self.uipFilter.ViewType)
      
    def FormShow(self, mode) :
       #eval(self.ParamDisplay[mode])
       return self.FormContainer.Show()

    def IdDonorOnExit(self,sender):
      uipFilter = self.uipFilter
      DonorNo = uipFilter.No_Donor or ''
      if ( DonorNo == '' or
             (self.DonorNo not in [None,''] and
             self.DonorNo == uipFilter.No_Donor)
         ) :
        return


      rph = self.form.CallServerMethod(
             'GetDonorDataByNo',
             self.app.CreateValues(['DonorNo',DonorNo])
             )


      uipFilter.Edit()

      rec = rph.FirstRecord
      if rec.Is_Err :
        #uipFilter.No_Donor = ''
        uipFilter.Id_Donor = 0
        uipFilter.Nama_Donor = ''
        self.DonorNo = None
        self.uipTrans.ClearData()
        raise 'PERINGATAN',rec.Err_Message

      #uipFilter.No_Donor = rec.DonorNo
      uipFilter.Id_Donor = rec.DonorId
      uipFilter.Nama_Donor = rec.DonorName
      self.DonorNo = uipFilter.No_Donor

    
    def bCariClick(self,sender):
       app = self.app
       
       if self.SearchForm != None :
         fSearch = self.SearchForm
       else:
         SearchForm = 'Donatur/fSearchDonor'
         fSearch = app.CreateForm(SearchForm, SearchForm, 0, None, None)
         self.SearchForm = fSearch
       # end if
         
       if fSearch.GetDonorData() :
         uipFilter = self.uipFilter
         
         uipFilter.Edit()
         uipFilter.No_Donor = fSearch.DonorId
         uipFilter.Id_Donor = fSearch.DonorIntId
         uipFilter.Nama_Donor = fSearch.DonorName
       # end if

    
    def OnExit_Data(self, sender) :
       if self.uipFilter.Data in (None,'') \
         or self.uipFilter.TempData == (self.uipFilter.Input_Data + self.uipFilter.Data):
          return
       res= self.FormObject.CallServerMethod("FindData",
         self.app.CreateValues(['SearchType',self.uipFilter.Input_Data],
           ['Data',self.uipFilter.Data],['ClassName','Donor'],['IDName',self.uipFilter.ID])
         )
       if res.FirstRecord.Values != '()' :
         self.ObjectAccess.InsertData(self.FormObject.GetUIPartByName(res.FirstRecord.uip),
           eval(res.FirstRecord.Struct),res.FirstRecord.Values,0)
         self.SwitchDisplay(res.FirstRecord.uip[-1])

       else :
         self.app.ShowMessage('Donatur tidak ditemukan!!')
         self.DisplayPage(PI_NONE)
       self.uipFilter.TempData = self.uipFilter.Input_Data + self.uipFilter.Data
       
    def OnClick_bView(self, sender) :
       if self.uipFilter.TglAwal > self.uipFilter.TglAkhir :
         raise 'PERINGATAN','Tanggal Awal tidak boleh lebih besar dari Tanggal Akhir'
       Type = self.uipFilter.ViewType
       res= self.FormObject.CallServerMethod("GetHistData",
         self.app.CreateValues(['ModeType',Type],
           ['Data',self.FormObject.GetUIPartByName('uipData'+Type).GetFieldValue(self.uipFilter.ID)],
           ['ClassName',self.FormObject.GetUIPartByName('uipData'+Type).ClassName],
           ['IDName',self.uipFilter.ID])
         )
       if res.FirstRecord.Values != '()' :
         for i in range(result.RecordCount) :
            self.uipResult.Append()
            self.ObjectAccess.InsertData(self.FormObject.GetUIPartByName(res.FirstRecord.uip),
              eval(res.FirstRecord.Struct), result.GetRecord(i).Values, 0)
              
    def bViewHistClick (self, sender):
      self.ButtonExec(sender,1)

    def bExportClick(self,sender):
      app = self.app
      filename = self.oPrint.ConfirmDestinationPath(app,'xls')
      if filename in ['',None] : return
      self.ButtonExec(sender,2,filename)

    def ButtonExec(self,sender,mode,filename=None):
      app = self.app
      uipFilter = self.uipFilter
      ph = self.FormObject.CallServerMethod(
        'GetHistTransaction',
        self.app.CreateValues(
          ['DonorId', uipFilter.Id_Donor],
          ['BeginDate', uipFilter.TglAwal],
          ['EndDate', uipFilter.TglAkhir]
        )
      )

      status = ph.FirstRecord
      if status.Is_Err : raise 'PERINGATAN',status.Err_Message
      
      #self.uipCashAccount.BeginningBalance = ph.FirstRecord.BeginningBalance
      if mode == 1:
        # Clear Grid
        uipTran = self.uipTrans
        uipTran.ClearData()
        
        # Set Grid Data
        ds = ph.packet.histori
        i = 0
        while i < ds.RecordCount:
          rec = ds.GetRecord(i)
          uipTran.Append()

          uipTran.TransactionItemId = rec.TransactionItemId
          uipTran.TransactionDate   = rec.TransactionDate
          uipTran.TransactionCode   = rec.TransactionCode
          uipTran.TransactionNo   = rec.TransactionNo
          uipTran.BranchCode   = rec.BranchCode
          uipTran.MutationType      = rec.MutationType
          uipTran.Amount            = rec.Amount
          #uipTran.ReferenceNo       = rec.ReferenceNo
          uipTran.Description       = rec.Description
          #uipTran.Inputer           = rec.Inputer

          i += 1
        # end of while
        uipTran.First()
        
        # set Total Amount
        uipFilter.Edit()
        uipFilter.TotalAmount = status.TotalAmount
        
      else:
        workbook = self.oPrint.OpenExcelTemplate(app,'tplDonorHistory.xls')
        workbook.ActivateWorksheet('data')
        try:
          # Set Header
          workbook.SetCellValue(2, 3, uipFilter.No_Donor)
          workbook.SetCellValue(3, 3, uipFilter.Nama_Donor)
          workbook.SetCellValue(4, 3, status.StrDatePeriod)
          workbook.SetCellValue(5, 3, status.TotalAmount)
          
          # Set Detail
          ds = ph.packet.histori
          i = 0
          while i < ds.RecordCount:
            rec = ds.GetRecord(i)
            row = i + 8
            
            workbook.SetCellValue(row, 1, str(i + 1) )
            workbook.SetCellValue(row, 2, rec.TransactionDate)
            workbook.SetCellValue(row, 3, rec.TransactionNo)
            workbook.SetCellValue(row, 4, rec.Amount)
            workbook.SetCellValue(row, 5, rec.Description)


            i += 1
          # end of while

          workbook.SaveAs(filename)
        finally:
          workbook = None

        app.ShellExecuteFile(filename)
        

