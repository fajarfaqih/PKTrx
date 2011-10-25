# Parameter.py

import com.ihsan.foundation.pobject as pobject

class ParameterGlobal(pobject.PObject):
  # static variable
  pobject_classname = 'ParameterGlobal'
  pobject_keys = ['Kode_Parameter']
  
  def Get(self): return self.Nilai_Parameter_String
  def GetDate(self) : return self.GetAsTDateTime('Nilai_Parameter_Tanggal')    
  def GetInt(self)  : return int(self.Nilai_Parameter)
  def GetFormatted(self, formatStr='yyyymmdd'): 
      return self.Config.FormatDateTime(formatStr, self.GetDate())
  
  def SetDate(self, aDate) : self.Nilai_Parameter_Tanggal = aDate
  def SetVal(self, aVal)   : self.Nilai_Parameter = aVal
  def SetText(self, aText) : self.Nilai_Parameter_String = aText 
          
class ParameterTransaksi(pobject.PObject):
  # static variable
  pobject_classname = 'ParameterTransaksi'
  pobject_keys = ['Id_Parameter_Transaksi']
  
class ParameterJournal(pobject.PObject):
  # static variable
  pobject_classname = 'ParameterJournal'
  pobject_keys = ['ParameterJournalId']
  
  def GetTCodes(self):
    oTCodes = []
    oList = self.Ls_ParameterJournalItem
    while not oList.EndOfList:
      oTCodes.append(oList.GetCurrentObjectElement())
      
      oList.Next()
    #-- while
    
    return oTCodes

class ParameterJournalItem(pobject.PObject):
  # static variable
  pobject_classname = 'ParameterJournalItem'
  pobject_keys = ['ParameterJournalItemId']

class GLInterfaceContainer(pobject.PObject): 
  # static variable
  pobject_classname = 'GLInterfaceContainer'
  pobject_keys = ['GLIContainerId']
  
  def GetAccountInterface(self, aInterfaceCode):
    
    oIntf = self.Helper.GetObjectByNames(
      'GLInterfaceMember',
      {
        'GLIContainerId': self.GLIContainerId,
        'GLIMemberCode': aInterfaceCode
      }
    )
    if oIntf.IsNull:
      raise 'GLContainer', 'GL interface %s cannot be found' % aInterfaceCode
    #-- if
    
    return oIntf

class GLInterfaceMember(pobject.PObject): 
  # static variable
  pobject_classname = 'GLInterfaceMember'
  pobject_keys = ['GLIMemberId']
  