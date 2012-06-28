# GLOBALS
AccessList = {}

def GetAccess(app, txCode):
  if not AccessList.has_key(txCode):
    ph = app.ExecuteScript(
      'GeneralModule\S_Form.GetCredentials',
      app.CreateValues(['tx_code', txCode])
    )
    rec = ph.FirstRecord
    if rec.Is_Err:
      AccessList[txCode] = 0, rec.Err_Message
    else:
      if rec.Is_Dual_Control:
        AccessList[txCode] = 2, ''
      else:
        AccessList[txCode] = 1, ''
      #-- if.else
    #-- if.else
  #--
  
  ErrMessages = [
     'Peran atau level akses ditolak',
     'Hari akses ditolak',
     'Waktu akses ditolak'
  ]
  st, msg = AccessList[txCode]
  if st == 0:
    if msg not in ErrMessages :
      AccessList.pop(txCode)
      raise 'Access Error', msg
    else :
      raise 'Access Denied', msg

  #--
  
def ShowQueryClick (menu, app) :
    GetAccess(app, menu.Name)
    app.SetLocalResourceMode(0)
    formname = menu.StringTag
    state = app.FindForm(formname)
    if state != None :
      dlg = state.FormObject.PyFormObject
    else :
      dlg = app.CreateForm(formname,formname,0,None,None)
    dlg.FormContainer.Show()

def ShowQuery2Click(menu,app):
    GetAccess(app, menu.Name)
    app.SetLocalResourceMode(0)
    formname = menu.StringTag
    state = app.FindForm(formname)
    if state != None :
      dlg = state.FormObject.PyFormObject
    else :
      dlg = app.CreateForm(formname,formname,0,None,None)
    dlg.Show()
    
def ParameterJournalClick (menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fParam = app.CreateForm('Parameter/fKodeJurnal', 'Parameter/fKodeJurnal', 0, ph, None)
  fParam.Show()

def ShowClick (menu, app) :
    GetAccess(app, menu.Name)
    FormParam = {
     'Donatur/fDonaturIndividu':('New','DonorId'),
     'Donatur/fDonaturKorporat':('New','DonorId'),
     'fPeragaanDonatur':('fPeragaanDonatur','DonorId'),
     'Donatur/fPeragaanDonatur':('New','DonorId'),
     'Donatur/fDonaturTransHistory':('New','DonorId'),
     'Report/fGeneralFilterReport':(menu.Name,'report'),
     'SENTINEL':''
    }

    app.SetLocalResourceMode(1)

    formname = menu.StringTag
    if formname == 'Donatur/fCariDonatur' :
      mode, ID = FormParam[menu.Name]
    else :
      mode, ID = FormParam[formname]
    #dlg = app.CreateForm(formname,formname,0,None,None)
    ph = app.CreateValues(['key',''],['mode',mode],['ID',ID])
    dlg = app.CreateForm(formname,formname,0,ph,[mode])
    
    #dlg.FormContainer.Show()
    dlg.FormShow(mode)

def ShowReportClick (menu, app):
  GetAccess(app, menu.Name)
  formName = menu.StringTag
  ph = app.CreateValues()
  fReport = app.CreateForm('Report/'+formName, formName, 0, ph, None)
  fReport.Show()
  
def FundCollectionClick (menu, app):
  GetAccess(app, menu.Name)

#  dSearch = app.CreateForm('Donatur/fSearchDonor', 'Donatur/fSearchDonor', 0, None, None)
#  donorID = dSearch.GetDonorID()

#  if donorID != None:
  ph = app.CreateValues(['x', 0])
  fTran= app.CreateForm('Transaksi/fFundCollection', 'Transaksi/fFundCollection', 0, ph, None)
  fTran.Show()
    
def FundDistributionClick (menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fTran= app.CreateForm('Transaksi/fFundDistribution', 'Transaksi/fFundDistribution', 0, ph, None)
  fTran.Show()

def InterFundTransferClick (menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fTran= app.CreateForm('Transaksi/fInterFundTransfer', 'Transaksi/fInterFundTransfer', 0, ph, None)
  fTran.Show()

def TransferInternalClick (menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fTran= app.CreateForm('Transaksi/fInternalTransfer', 'Transaksi/fInternalTransfer', 0, ph, None)
  fTran.Show()
  
def TransferRAKClick(menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fTran= app.CreateForm('Transaksi/fTransferRAK', 'Transaksi/fTransferRAK', 0, ph, None)
  fTran.Show()

def AccountReceivableClick (menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fTran= app.CreateForm('Transaksi/fEmployeeAR', 'Transaksi/fEmployeeAR', 0, ph, None)
  fTran.Show()

def CashAdvanceClick(menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fTran= app.CreateForm('Transaksi/fCashAdvance', 'Transaksi/fCashAdvance', 0, ph, None)
  fTran.Show()
  
def CashAdvanceReturnClick(menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fTran= app.CreateForm('Transaksi/fCashAdvanceReturn', 'Transaksi/fCashAdvanceReturn', 0, ph, None)
  fTran.Show()
  
def InvestmentClick(menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fTran= app.CreateForm('Transaksi/fInvestment', 'Transaksi/fInvestment', 0, ph, None)
  fTran.Show()

def InvestmentReturnClick(menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fTran= app.CreateForm('Transaksi/fInvestmentReturn', 'Transaksi/fInvestmentReturn', 0, ph, None)
  fTran.Show()
  
def InvestmentTransListClick(menu, app):
  GetAccess(app, menu.Name)
  fTran= app.CreateForm('Transaksi/fInvestmentTransList', 'Transaksi/fInvestmentTransList', 0, None, None)
  fTran.Show()
  
def CashAdvanceReturnRAKClick(menu,app) :
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fTran= app.CreateForm('Transaksi/fCashAdvanceReturnRAK', 'Transaksi/fCashAdvanceReturnRAK', 0, ph, None)
  fTran.Show()
  
def GeneralTransactionClick (menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fTran = app.CreateForm('Transaksi/fGeneralTransaction', 'Transaksi/fGeneralTransaction', 0, ph, None)
  fTran.Show()

def NewBatchClick (menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fBatch = app.CreateForm('Transaksi/fTransactionBatch', 'Transaksi/fTransactionBatch', 0, ph, None)
  fBatch.Show()

def SponsorViewClick(menu,app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fSponsor = app.CreateForm('Rekening/fSponsor', 'Rekening/fSponsor', 0, ph, None)
  fSponsor.Show()
  
def cashAccountClick (menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fCash = app.CreateForm('Rekening/fCashAccount', 'Rekening/fCashAccount', 0, ph, None)
  fCash.Show()
  
def productAccountClick (menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fProduct = app.CreateForm('Rekening/fProductAccount', 'Rekening/fProductAccount', 0, ph, None)
  fProduct.Show()

def GLHistoriClick(menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fBatch = app.CreateForm('rekening/fGLAccount', 'rekening/fGLAccount', 0, ph, None)
  fBatch.Show()
  
def productZakatClick (menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fProduct = app.CreateForm('Rekening/fZakahProduct', 'Rekening/fZakahProduct', 0, ph, None)
  fProduct.Show()

def showHistoriTransaksi (menu, app):
  GetAccess(app, menu.Name)
  app.SetLocalResourceMode(0)
  fHist = app.CreateForm('Transaksi/fTransactionHistory', 'Transaksi/fTransactionHistory', 0, None, None)
  fHist.Show()


def showHistoriTransaksi2(menu, app):
  GetAccess(app, menu.Name)
  #fTransHist = app.CreateForm('Transaksi/QryTransactionHistory', 'Transaksi/QryTransactionHistory', 0, None, None)
  fTransHist = app.CreateForm('Transaksi/fTransactionHistory', 'Transaksi/fTransactionHistory', 0, None, None)
  fTransHist.Show()
  
def showHistoriTransaksi3(menu, app):
  GetAccess(app, menu.Name)
  #fTransHist = app.CreateForm('Transaksi/QryTransactionHistorySpv', 'Transaksi/QryTransactionHistorySpv', 0, None, None)
  fTransHist = app.CreateForm('Transaksi/fTransactionHistory', 'Transaksi/fTransactionHistory', 0, None, None)
  fTransHist.Show(SPVMode=1)
  
def OtorisasiClick(menu, app):
  GetAccess(app, menu.Name)
  fAuth = app.CreateForm('Transaksi/fOtorisasi', 'Transaksi/fOtorisasi', 0, None, None)
  fAuth.Show()

def showRekening (menu, app) :
  app.ShowMessage(":) belum jadi")

def CloseDayClick(menu,app) :
  GetAccess(app, menu.Name)
  fAuth = app.CreateForm('tools/fCloseDay', 'tools/fCloseDay', 0, None, None)
  fAuth.Show()

def DepreciationClick(menu,app) :
  GetAccess(app, menu.Name)
  fTools = app.CreateForm('tools/fDepreciation', 'tools/fDepreciation', 0, None, None)
  fTools.Show()
  
def BackDateClick(menu,app) :
  #GetAccess(app, menu.Name)
  fBackDate = app.CreateForm('tools/fBackDate', 'tools/fBackDate', 0, None, None)
  fBackDate.Show()

def NewBudgetClick(menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  #dlg= app.CreateForm('Budget/fBudgetNew', 'fBudgetNew', 0, None, None)
  dlg= app.CreateForm('Budget/fBudgetImport', 'Budget/fBudgetImport', 0, None, None)
  dlg.Show()

def BudgetRevisionClick(menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  dlg = app.CreateForm('Budget/fBudgetEditList', 'fBudgetEditList', 0, None, None)
  dlg.Show()

def BudgetViewClick(menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  dlg = app.CreateForm('Budget/fBudgetViewList', 'fBudgetViewList', 0, None, None)
  dlg.Show()

def ProgramSponsorClick(menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  #dlg = app.CreateForm('Sponsor/fSponsorProgram', 'Sponsor/fSponsorProgram', 0, None, None)
  dlg = app.CreateForm('Transaksi/fInvoiceList', 'Transaksi/fInvoiceList', 0, None, None)
  dlg.Show()
  
def BranchDistributionClick(menu,app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  dlg = app.CreateForm('Transaksi/fBranchDistribution', 'Transaksi/fBranchDistribution', 0, None, None)
  dlg.Show()

def BranchDistributionReturnClick(menu,app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  dlg = app.CreateForm('Transaksi/fBranchDistributionReturn', 'Transaksi/fBranchDistributionReturn', 0, None, None)
  dlg.Show()

def BranchDistListClick(menu,app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  dlg = app.CreateForm('Transaksi/fBranchDistributionList', 'Transaksi/fBranchDistributionList', 0, None, None)
  dlg.Show()
  
def CetakBSZClick(menu, app):
  GetAccess(app, menu.Name)
  formname = 'Transaksi/fBSZList'
  SimpleShow(app,formname)

def OtorisasiNotaDinasClick(menu,app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  dlg = app.CreateForm('Transaksi/fNotaDinasOtorisasi', 'Transaksi/fNotaDinasOtorisasi', 0, None, None)
  dlg.Show()
  
def NotaDinasClick(menu,app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  dlg = app.CreateForm('Transaksi/fNotaDinas', 'Transaksi/fNotaDinas', 0, None, None)
  dlg.Show()
  
def InvoicePaymentClick(menu,app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  dlg = app.CreateForm('Transaksi/fInvoicePayment', 'Transaksi/fInvoicePayment', 0, None, None)
  dlg.Show()

def PrintVoucherClick(menu, app):
  #GetAccess(app, menu.Name)
  form = app.CreateForm('Transaksi/fPrintVoucherDonation', 'Transaksi/fPrintVoucherDonation', 0, None, None)
  form.Show()

def FixedAssetClick(menu, app):
  #GetAccess(app, menu.Name)
  form = app.CreateForm('Transaksi/fFixedAssetNew', 'Transaksi/fFixedAssetNew', 0, None, None)
  form.Show()

def FAInvoiceClick(menu, app):
  #GetAccess(app, menu.Name)
  form = app.CreateForm('Transaksi/fFixedAssetInvoice', 'Transaksi/fFixedAssetInvoice', 0, None, None)
  form.Show()

def FAInvoicePaymentClick(menu, app):
  #GetAccess(app, menu.Name)
  form = app.CreateForm('Transaksi/fFixedAssetInvoicePayment', 'Transaksi/fFixedAssetInvoicePayment', 0, None, None)
  form.Show()

def FADisposalClick(menu, app):
  #GetAccess(app, menu.Name)
  form = app.CreateForm('Transaksi/fFixedAssetDisposal', 'Transaksi/fFixedAssetDisposal', 0, None, None)
  form.Show()
  
def SimpleShowClick(menu,app):
  GetAccess(app, menu.Name)
  SimpleShow(app,menu.StringTag)

def SimpleShow(app,formname):
  form = app.CreateForm(formname, formname, 0, None, None)
  form.Show()

def TesClick(menu,app):
  formname = menu.StringTag
  form = app.CreateForm(formname, formname, 0, None, None)
  form.Show()

def ScriptTestClick(menu,app):
  formname = 'Tools/fScriptTest'
  form = app.CreateForm(formname, formname, 0, None, None)
  form.FormContainer.Show()
  
def LongScriptTestClick(menu,app):
  formname = 'Tools/fLongScriptTest'
  form = app.CreateForm(formname, formname, 0, None, None)
  form.FormContainer.Show()
  
def ListFaultTransClick(menu,app):
  oPrint = app.GetClientClass('PrintLib','PrintLib')()

  response = app.ExecuteScript('Tools/S_ListFaultTrans',app.CreateValues())

  resp = response.FirstRecord

  if resp.Is_Error :
     raise 'ERROR',resp.Error_Message

  if response.packet.StreamWrapperCount > 0:
    oPrint.doProcess(app,response.packet,1)
          
def OnBatchCabang(sender, app):
  ph  = app.CreatePacket()
  res = app.ExecuteScript("Tools/S_KontrolBatch.KontrolCabang", ph)

  status = res.FirstRecord
  if status.Is_Err: raise 'PERINGATAN', status.Err_Message

  oPrint = app.GetClientClass('PrintLib','PrintLib')()
  oPrint.doProcess(app, res.packet, 1)
  
def GenerateJournalClick(sender,app):
  ph  = app.CreatePacket()
  res = app.ExecuteScript("Tools/S_Journal.GenerateAll", ph)

  status = res.FirstRecord
  if status.Is_Err: raise 'PERINGATAN', status.Err_Message

  oPrint = app.GetClientClass('PrintLib','PrintLib')()
  oPrint.doProcess(app, res.packet, 1)
  

def SaldoAwalClick(menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  dlg = app.CreateForm('Tools/fSaldoAwal', 'Tools/fSaldoAwal', 0, None, None)
  dlg.Show()

def PrintSaldoAwalClick(menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  dlg = app.CreateForm('Tools/fPrintSaldoAwal', 'Tools/fPrintSaldoAwal', 0, None, None)
  dlg.Show()
  
def KontroloSaldoAwalClick(menu, app):
  #GetAccess(app, menu.Name)
  ph = app.CreateValues()
  dlg = app.CreateForm('Tools/fKontrolSaldoAwal', 'Tools/fKontrolSaldoAwal', 0, None, None)
  dlg.Show()
  
def MergeCashAdvanceClick(menu,app):
  dlg = app.CreateForm('Tools/fMergeEmployeeCA', 'Tools/fMergeEmployeeCA', 0, None, None)
  dlg.Show()

def MergeAccountReceivableClick(menu,app):
  dlg = app.CreateForm('Tools/fMergeAccountReceivable', 'Tools/fMergeAccountReceivable', 0, None, None)
  dlg.Show()

def OnDepreciationClick(menuitem, app):
  #GetAccess(app, menu.Name)
  #if app.ConfirmDialog("Yakin proses penyusutan (Y/N) ?"):
    # open log viewer
    #app.ExecuteAsyncScript('logManagement/logViewer',
    #  app.CreateValues(['logChannelName', 'dafapp'], ['logServerPort', 2423]), 1)
    # Proses penyusutan
    #pid = app.ExecuteScriptTrackable("BatchProcess/L_TestScript", None)
    #app.ExecuteScript("BatchProcess/L_Depreciation",app.CreateValues())

  fDepr= app.CreateForm('Transaksi/fDepreciation', 'Transaksi/fDepreciation', 0, None, None)
  fDepr.Show()
  
def registerBDDClick(menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fTran= app.CreateForm('Transaksi/fRegisterBDD', 'Transaksi/fRegisterBDD', 0, ph, None)
  fTran.Show()


def FAViewClick(menu, app):
  GetAccess(app, menu.Name)
  fTran= app.CreateForm('DepreciableAsset/fFixedAssetList', 'DepreciableAsset/fFixedAssetList', 0, None, None)
  fTran.Show()

def CPIAListClick(menu, app):
  GetAccess(app, menu.Name)
  fTran= app.CreateForm('DepreciableAsset/fCPIAList', 'DepreciableAsset/fCPIAList', 0, None, None)
  fTran.Show()

def InvestmentListClick(menu, app):
  GetAccess(app, menu.Name)
  fTran= app.CreateForm('rekening/fInvestment', 'rekening/fInvestment', 0, None, None)
  fTran.Show()
  
def SettingParameterClick(menu, app):
  GetAccess(app, menu.Name)
  ph = app.CreateValues()
  fSetting = app.CreateForm('Tools/fBranchParameterSetting', 'Tools/fBranchParameterSetting', 0, ph, None)
  fSetting.Show()
