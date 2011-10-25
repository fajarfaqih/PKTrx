class fInvoiceProject:
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.form = formObj

  def CreateInvoice(self,DisbId):
    self.uipInvoice.ClearData()

    ph = self.app.CreateValues(
               ['DisbId', DisbId],
    )
    self.form.SetDataWithParameters(ph)

    st = self.FormContainer.Show()
    if st == 1 :
      #uipInvoice = self.uipInvoice
      #self.InvoiceDate = uipInvoice.InvoiceDate
      #self.InvoiceNo = uipInvoice.InvoiceNo
      return 1
    else:
      return 0
      
  def PrintInvoiceClick(self,sender):
    app = self.app
    form = self.form
    
    form.CommitBuffer()
    rph = form.CallServerMethod('PrintInvoice',form.GetDataPacket())
    
    status = rph.FirstRecord
    
    if status.Is_Err : raise 'PERINGATAN',status.Err_Message
    
    oPrint = app.GetClientClass('PrintLib','PrintLib')()
    oPrint.doProcessByStreamName(app,rph.packet,status.StreamName,1)
    
