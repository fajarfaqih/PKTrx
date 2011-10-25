
class fSelectInvoiceProduct :
    def __init__(self, formObj, parentForm) :
       self.app = formObj.ClientApplication
       self.form = formObj
       self.SearchForm = None
       self.SponsorNo = None
       self.InvoiceForm = None
       self.fInvoiceProject = None

    def Show(self) :
       #eval(self.ParamDisplay[mode])
       return self.FormContainer.Show()

    def IdSponsorOnExit(self,sender):
      uipFilter = self.uipFilter
      SponsorNo = uipFilter.No_Sponsor or ''
      if ( SponsorNo == '' or
             (self.SponsorNo not in [None,''] and
             self.SponsorNo == uipFilter.No_Sponsor)
         ) :
        return

      rph = self.form.CallServerMethod(
             'GetSponsorDataByNo',
             self.app.CreateValues(['SponsorNo',SponsorNo])
             )

      uipFilter.Edit()

      rec = rph.FirstRecord
      if rec.Is_Err :
        #uipFilter.No_Sponsor = ''
        uipFilter.SponsorId = 0
        uipFilter.Nama_Sponsor = ''
        self.SponsorNo = None
        self.uipTransProgram.ClearData()
        raise 'PERINGATAN',rec.Err_Message

      #uipFilter.No_Sponsor = rec.SponsorNo
      uipFilter.SponsorId = rec.DonorId
      uipFilter.Nama_Sponsor = rec.DonorName
      self.SponsorNo = uipFilter.No_Sponsor

    
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
         uipFilter.No_Sponsor = fSearch.DonorId
         uipFilter.SponsorId = fSearch.DonorIntId
         uipFilter.Nama_Sponsor = fSearch.DonorName
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
              
    def bViewHistClick(self, sender):
      ph = self.FormObject.CallServerMethod(
        'GetHistTransaction',
        self.app.CreateValues(
          ['DonorId', self.uipFilter.SponsorId],
          ['BeginDate', self.uipFilter.TglAwal],
          ['EndDate', self.uipFilter.TglAkhir]
        )
      )

      #self.uipCashAccount.BeginningBalance = ph.FirstRecord.BeginningBalance
      uipTran = self.uipTransProgram
      uipTran.ClearData()

      ds = ph.packet.histori
      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        uipTran.Append()

        uipTran.TransactionItemId = rec.TransactionItemId
        uipTran.TransactionDate   = rec.TransactionDate
        uipTran.TransactionCode   = rec.TransactionCode
        uipTran.BranchCode   = rec.BranchCode
        uipTran.MutationType      = rec.MutationType
        uipTran.Amount            = rec.Amount
        uipTran.AccountName            = rec.AccountName
        #uipTran.ReferenceNo       = rec.ReferenceNo
        uipTran.Description       = rec.Description
        if rec.InvoiceDate != 0.0 : uipTran.InvoiceDate       = rec.InvoiceDate
        uipTran.InvoiceNo       = rec.InvoiceNo
        #uipTran.Inputer           = rec.Inputer

        i += 1
      # end of while

      uipTran.First()

    def CreateInvoiceProgram(self):
       app = self.app
       uipTran = self.uipTransProgram
       TransactionItemId = uipTran.TransactionItemId or 0
       if TransactionItemId == 0 : return
       if self.InvoiceForm != None :
         fInvoice = self.InvoiceForm
       else:
         InvoiceForm = 'Sponsor/fInvoice'
         fInvoice = app.CreateForm(InvoiceForm, InvoiceForm, 0, None, None)
         self.InvoiceForm = fInvoice
       # end if


       if fInvoice.CreateInvoice(TransactionItemId) :
         uipTran.Edit()
         uipTran.InvoiceDate = fInvoice.InvoiceDate
         uipTran.InvoiceNo = fInvoice.InvoiceNo
       # end if

    def CreateInvoiceProject(self):
       app = self.app
       uipDisb = self.uipProjectDisbursement
       DisbId = uipDisb.DisbId or 0
       if DisbId == 0 : return
       
       if self.fInvoiceProject != None :
         fInvoice = self.fInvoiceProject
       else:
         InvoiceForm = 'Sponsor/fInvoiceProject'
         fInvoice = app.CreateForm(InvoiceForm, InvoiceForm, 0, None, None)
         self.fInvoiceProject = fInvoice
       # end if


       if fInvoice.CreateInvoice(DisbId) :
         #uipTran.Edit()
         #uipTran.InvoiceDate = fInvoice.InvoiceDate
         #uipTran.InvoiceNo = fInvoice.InvoiceNo
         pass
       # end if


    def bExportClick(self,sender):
      app = self.app
      
      ph = self.FormObject.CallServerMethod(
        'PrintHistTransaction',
        self.app.CreateValues(
          ['DonorId', self.uipFilter.SponsorId],
          ['DonorNo', self.uipFilter.No_Sponsor],
          ['DonorName', self.uipFilter.Nama_Sponsor],
          ['BeginDate', self.uipFilter.TglAwal],
          ['EndDate', self.uipFilter.TglAkhir]
        )
      )

      rec = ph.FirstRecord
      
      if rec.Is_Err :
         raise 'PERINGATAN',rec.Err_Message
         
      oPrint = app.GetClientClass('PrintLib','PrintLib')()
      oPrint.doProcess(app,ph.packet)

    def bDisburseClick(self,sender):
      app = self.app
      
      ph = self.FormObject.CallServerMethod(
        'GetDisburseData',
        self.app.CreateValues(
          ['ProjectSponsorId', self.uipFilter.GetFieldValue('LProject.ProjectSponsorId') or ''],
        )
      )
      
      status = ph.FirstRecord
      if status.Is_Err : raise 'PERINGATAN',status.Err_Message

      uipDisb = self.uipProjectDisbursement
      uipDisb.ClearData()

      ds = ph.packet.DisburseData
      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        uipDisb.Append()

        uipDisb.DisbNumber = rec.DisbNumber
        uipDisb.DisbDatePlan = rec.DisbDatePlan
        uipDisb.DisbAmountPlan = rec.DisbAmountPlan
        uipDisb.DisbId = rec.DisbId

        i += 1
      # end of while

      uipDisb.First()
      

