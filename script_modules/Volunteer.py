# Volunteer.py

import com.ihsan.foundation.pobject as pobject

class Volunteer(pobject.PObject):
  # static variable
  pobject_classname = 'Volunteer'
  pobject_keys = ['VolunteerId']

  def AddTransaction(self, oItem):
    param = [self, oItem]
    oTran = self.Helper.CreatePObject('VolunteerTransaction', param)
    return oTran

  def CheckForDelete(self):
    sqlCheck = "select count(volunteerid) from volunteertransaction where volunteerid='%s'" % (self.VolunteerId)
    
    resSQL = self.Config.CreateSQL(sqlCheck).rawresult
    if resSQL.GetFieldValueAt(0) > 0:
      raise '','Data tidak dapat dihapus karena menjadi referensi oleh data lain'
      
    return 1
  
  def GetEntityBalance(self,Entity=0,Date=None):
    strSQL = "select sum(case when a.mutationtype='C' then a.Amount \
                           else -a.Amount \
                      end) \
              from transactionitem a, transaction b, \
                   accounttransactionitem c, volunteertransaction d \
              where a.transactionid=b.transactionid \
                 and a.transactionitemid=c.transactionitemid \
                 and c.transactionitemid=d.transactionitemid \
                 and d.volunteerid = '%s' " % self.VolunteerId

    if Entity != 0 :
      strSQL += ' and c.FundEntity=%d ' % Entity

    if Date != None :
      FormattedDate = self.Config.FormatDateTime('yyyy-mm-dd',int(Date))
      strSQL += " and b.actualdate < '%s' " % FormattedDate

    resSQL = self.Config.CreateSQL(strSQL).rawresult

    return resSQL.GetFieldValueAt(0) or 0.0  
  
  def GetBalanceByDate(self,aDate):
    strSQL = "select sum(case when a.mutationtype='C' then a.Amount \
                           else -a.Amount \
                      end) \
              from transactionitem a, transaction b, volunteertransaction c\
              where a.transactionid=b.transactionid \
                 and a.transactionitemid=c.transactionitemid \
                 and c.volunteerid = '%s' " % self.VolunteerId
    
    if aDate != None :
      FormattedDate = self.Config.FormatDateTime('yyyy-mm-dd',aDate)
      strSQL += " and b.actualdate < '%s' " % FormattedDate

    resSQL = self.Config.CreateSQL(strSQL).rawresult
    
    return resSQL.GetFieldValueAt(0) or 0.0
        
class VolunteerTransaction(pobject.PObject):
  # static variable
  pobject_classname = 'VolunteerTransaction'
  pobject_keys = ['TransactionItemId']

  def OnCreate(self, param):
    aOwner = param[0]
    oItem  = param[1]
    self.LVolunteer   = aOwner    
    self.LTransaction = oItem