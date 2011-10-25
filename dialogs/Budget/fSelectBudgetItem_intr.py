class fSelectBudgetItem:
  def __init__(self,formObj,parentForm):
    self.app = formObj.ClientApplication
    self.Kode_Rincian = None

  def GetItem(self):
    query = self.qBudgetItem

    query.OQLText = "\
            select from BudgetItem \
            [ Is_Detail='T' ] \
            ( LParent.BudgetItemCode as Kode_Kegiatan, \
              LParent.BudgetItemDescription as Nama_Kegiatan, \
              BudgetItemCode as Kode_Rincian, \
              BudgetItemDescription as Nama_Rincian, \
              self);"

    self.qBudgetItem.DisplayData()
    st = self.FormContainer.Show()
    if (st == 1) and query.HasData:
      self.Kode_Kegiatan = query.GetFieldValue("BudgetItem.Kode_Kegiatan")
      self.Nama_Kegiatan = query.GetFieldValue("BudgetItem.Nama_Kegiatan")
      self.Kode_Rincian = query.GetFieldValue("BudgetItem.Kode_Rincian")
      self.Nama_Rincian = query.GetFieldValue("BudgetItem.Nama_Rincian")
      if self.Kode_Rincian in ['',None]:
         raise "PERINGATAN","Tidak ada periode yang dipilih"
      return 1
    else:
      return 0

    
