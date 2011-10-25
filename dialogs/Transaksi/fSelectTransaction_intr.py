class fSelectTransaction:

  def __init__(self, formObj, parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.userapp = self.app.UserAppObject
    
    self.tag_batch = None
    self.TransactionId = None

  def SelectTransaction(self):
    self.uipData.Edit()
    self.uipData.BeginNo   = 1
    self.uipData.TransactionNumber = 0

    uipTransaction = self.uipTransaction
    st = self.FormContainer.Show()
    if st == 1:
      self.TransactionId = uipTransaction.TransactionId
      return 1
    return 0

  def bViewClick(self, sender):
    uipData = self.uipData
    uipData.BatchNo = uipData.GetFieldValue('LBatch.BatchNo') or ''
    batchId = uipData.GetFieldValue('LBatch.BatchId') or ''

    beginNo = uipData.BeginNo

    if batchId not in ['',None]:
      ph = self.app.CreateValues(['BatchId', int(batchId)], ['BeginNo', beginNo])
      self.FormObject.SetDataWithParameters(ph)
      self.uipTransaction.First()
    #-- if
