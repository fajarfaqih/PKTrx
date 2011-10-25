# Budget.py

import com.ihsan.foundation.pobject as pobject
import simplejson
import sys
import com.ihsan.fileutils as utils
import com.ihsan.net.socketclient as socketclient
import types

# GLOBALS

class Budget(pobject.PObject): 
  # static variable
  pobject_classname = 'Budget'
  pobject_keys = ['BudgetId']

  def CreateRevision(self,Amount):
    oRevision = self.Helper.CreatePObject('BudgetRevision')
    oRevision.BudgetId = self.BudgetId
    oRevision.Amount = Amount
    oRevision.UserId = self.Config.SecurityContext.InitUser
    self.RevisionId = oRevision.RevisionId

  def GetRealization(self):
    strSQL = "select sum(a.Amount) \
              from transactionitem a, transaction b, budgettransaction c\
              where a.transactionid=b.transactionid \
                 and a.transactionitemid=c.transactionitemid \
                 and c.BudgetId = %d " % self.BudgetId
    
    resSQL = self.Config.CreateSQL(strSQL).rawresult    
    return resSQL.GetFieldValueAt(0) or 0.0         

  def OnDelete(self):
    #sDelete = 'delete from budget where parentbudgetid=%d' % (self.BudgetId)
    #self.Config.ExecSQL(sDelete)
    pass
    
  def UpdateRealization(self,Amount):
    self.Realization += Amount
    
class BudgetYear(Budget):
  pobject_classname = 'BudgetYear'
        
class BudgetPeriod(pobject.PObject):  
  # static variable
  pobject_classname = 'BudgetPeriod'
  pobject_keys = ['PeriodId']

class BudgetOwner(pobject.PObject):
  # static variable
  pobject_classname = 'BudgetOwner'
  pobject_keys = ['OwnerId']
   
  def SetHierarchy(self): 
    ParentOwnerId = self.ParentOwnerId or 0
    
    while ParentOwnerId != 0:
      oParent = self.Helper.GetObject('BudgetOwner',ParentOwnerId)
      
      oPHierarchy = self.Helper.CreatePObject('BudgetOwnerHierarchy')
      oPHierarchy.ParentOwnerId = ParentOwnerId
      oPHierarchy.ChildOwnerId = self.OwnerId
      oPHierarchy.Level = self.Level - oParent.Level

      ParentOwnerId = oParent.ParentOwnerId
    
    #-- end while 
    oParent = self.Helper.GetObject('BudgetOwner',ParentOwnerId)      
    oPHierarchy = self.Helper.CreatePObject('BudgetOwnerHierarchy')
    oPHierarchy.ParentOwnerId = self.OwnerId
    oPHierarchy.ChildOwnerId = self.OwnerId
    oPHierarchy.Level = 0

      
class BudgetOwnerHierarchy(pobject.PObject):
  # static variable
  pobject_classname = 'BudgetOwnerHierarchy'
  pobject_keys = ['HierarchyId']

class BudgetRevision(pobject.PObject):
  # static variable
  pobject_classname = 'BudgetRevision'
  pobject_keys = ['RevisionId']

class BudgetTransaction(pobject.PObject):
  # static variable
  pobject_classname = 'BudgetTransaction'
  pobject_keys = ['TransactionItemId']

  def OnDelete(self):
    self.LBudget.UpdateRealization(-1 * (self.LTransaction.Amount))
    
class BudgetItem(pobject.PObject):
  # static variable
  pobject_classname = 'BudgetItem'
  #pobject_keys = ['BudgetItemCode']
  pobject_keys = ['ItemId']

  def SetHierarchy(self): 
    ParentItemId = self.ParentItemId or 0
    
    while ParentItemId != 0:
      oParent = self.Helper.GetObject('BudgetItem',ParentItemId)
      
      oHierarchy = self.Helper.CreatePObject('BudgetItemHierarchy')
      oHierarchy.ParentItemId = ParentItemId
      oHierarchy.ChildItemId = self.ItemId
      oHierarchy.Level = self.Level - oParent.Level

      ParentItemId = oParent.ParentItemId
    
    #-- end while 
    oParent = self.Helper.GetObject('BudgetOwner',ParentItemId)      
    oHierarchy = self.Helper.CreatePObject('BudgetItemHierarchy')
    oHierarchy.ParentItemId = self.ItemId
    oHierarchy.ChildItemId = self.ItemId
    oHierarchy.Level = 0
      
class BudgetItemHierarchy(pobject.PObject):
  # static variable
  pobject_classname = 'BudgetItemHierarchy'
  pobject_keys = ['HierarchyId']
  
