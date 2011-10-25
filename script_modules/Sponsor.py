# Sponsor.py

import com.ihsan.foundation.pobject as pobject

class Sponsor(pobject.PObject):
  # static variable
  pobject_classname = 'Sponsor'
  pobject_keys = ['SponsorId']
  
  def AddTransaction(self, oItem):
    param = [self, oItem]
    oTran = self.Helper.CreatePObject('SponsorTransaction', param)
    return oTran
  
  def CheckForDelete(self):
    sqlCheck = 'select count(sponsorid) from sponsortransaction where sponsorid=%d' % (self.SponsorId)
    
    resSQL = self.Config.CreateSQL(sqlCheck).rawresult
    if resSQL.GetFieldValueAt(0) > 0:
      raise '','Data tidak dapat dihapus karena menjadi referensi oleh data lain'
      
    sqlCheck = 'select count(sponsorid) from projectsponsor where sponsorid=%d' % (self.SponsorId)
    
    resSQL = self.Config.CreateSQL(sqlCheck).rawresult
    if resSQL.GetFieldValueAt(0) > 0:
      raise '','Data tidak dapat dihapus karena menjadi referensi oleh data lain'
      
    return 1
    
class SponsorTransaction(pobject.PObject):
  # static variable
  pobject_classname = 'SponsorTransaction'
  pobject_keys = ['TransactionItemId']

  def OnCreate(self, param):
    #aOwner = param[0]
    aDonorId = param[0]
    oItem  = param[1]
    #self.LSponsor     = aOwner
    self.SponsorId = aDonorId
    self.LTransaction = oItem
    
    #aProductId = oItem.LFinancialAccount.CastToLowestDescendant().ProductId
#     AccountNo = oItem.LFinancialAccount.CastToLowestDescendant().AccountNo
#     oProjectSponsor = self.Helper.GetObjectByNames('ProjectSponsor',
#       {'AccountNo': AccountNo, 'SponsorId': aOwner.SponsorId})
#     
#     if not oProjectSponsor.IsNull:
#       #raise 'OnCreate', 'Proyek sponsor tidak ditemukan!'
#       self.LProjectSponsor = oProjectSponsor
    #--if
    
class ProjectSponsor(pobject.PObject): 
  pobject_classname = 'ProjectSponsor'
  pobject_keys = ['ProjectSponsorId']
  
class SponsorTransactionProgram(SponsorTransaction):
  # static variable
  pobject_classname = 'SponsorTransactionProgram'

class ProjectSponsorDisbursement(pobject.PObject): 
  pobject_classname = 'ProjectSponsorDisbursement'
  pobject_keys = ['DisbId']
  