import com.ihsan.foundation.pobject as pobject
import com.ihsan.foundation.mobject as mobject
import os, sys
import ConfigParser

ObjectList = {
   'Donor' : 
      {'TableName':'public.php_donor' ,
        'Key' : ['id']
      }
}

class ExternalObject(mobject.MObject):

  def GetObject(ObjectName,Key):
    if not ObjectList.has_key(ObjectName):
      raise '','Object Name Not Exist'
    
      
class ExtDonor(mobject.MObject):

  def mobject_init(self):
    self.Fields = ['user_name','email','full_name','user_status','phone_no','address','donor_no','npwp_no','npwz_no','donor_type_id','marketer_id']
    self.isnull = 1

  def SetID(self,ID):
    self.DonorId = ID

  def GetData(self,Key):
    config = self.Config
    KeyField = 'id'

    sDonor = 'select %s from public.php_donor a \
              left outer join public.php_donor_phone b on (a.phone_id=b.id) \
              where a.id=%d' % (','.join(self.Fields),Key)             

    rsDonor = config.CreateSQL(sDonor).RawResult
    
    if rsDonor.Eof: return 0
    
    self.id = Key
    self.SetID(self.id)
    for field in  self.Fields :
      setattr(self,field,rsDonor.GetFieldValue(field))
    
    # replace address dengan full address 
    FullAddress = self.GetFullAddress()
    
    if FullAddress != '' : self.address = FullAddress
     
    self.isnull = 0
    return 1

  def GetFullAddress(self):
    config = self.Config
    
    FullAddress = ''
    sAddress = 'select address_full from public.vw_donor where id=%d' % (self.id)
    rsAddress = config.CreateSQL(sAddress).RawResult
    if not rsAddress.Eof: 
      FullAddress = rsAddress.Address_Full
      
    return FullAddress
    
  def GetDataByDonorNo(self,DonorNo) :
   
    config = self.Config

    sDonor = "select a.id,%s from public.php_donor a \
              left outer join public.php_donor_phone b on (a.phone_id=b.id) \
              where a.donor_no= '%s'" % (','.join(self.Fields),DonorNo)

    rsDonor = config.CreateSQL(sDonor).RawResult

    if rsDonor.Eof: return 0
    
    self.id = rsDonor.id
    self.SetID(self.id)
    for field in  self.Fields :
      setattr(self,field,rsDonor.GetFieldValue(field))

    self.isnull = 0

    return 1

  def GetDataByParam(self,Params):
    config = self.Config 
  
  def AddTransaction(self,oItem):
    #param = [DonorId, oItem]
    param = [self.DonorId, oItem]
    oProductAccount = oItem.LFinancialAccount.CastToLowestDescendant()
    oProduct = oProductAccount.LProduct.CastToLowestDescendant()
    if oProduct.IsA('Program') : 
      oTran = self.Helper.CreatePObject('SponsorTransactionProgram', param)
      oTran.InvoiceStatus = 'F'
    else:
      oTran = self.Helper.CreatePObject('SponsorTransaction', param)
  
  def IsSponsor(self):
    if self.isnull : return 0 
    return self.donor_type_id in [2,3]
  
  def GetMarketerName(self):
    if self.isnull : return '' 
    
    sMarketer = "select id,full_name from public.sdm_employee \
              where id=%d " % (self.marketer_id)

    rsMarketer = self.Config.CreateSQL(sMarketer).RawResult

    if rsMarketer.Eof: return ''
    
    return rsMarketer.full_name
        
class ExtSponsor(ExtDonor):
  def mobject_init(self):
    pass
         
  def AddTransaction(self,oItem):
    #param = [DonorId, oItem]
    param = [self.DonorId, oItem]
    oTran = self.Helper.CreatePObject('SponsorTransaction', param)
        
    return oTran

class Account(pobject.PObject):
  # static variable
  pobject_classname = 'Account'
  pobject_keys = ['Account_Code']
  
class Branch(pobject.PObject):
  # static variable
  pobject_classname = 'Branch'
  pobject_keys = ['BranchCode']
  
class VEmployee(pobject.PObject):
  # static variable
  pobject_classname = 'VEmployee'
  pobject_keys = ['EmployeeId']
  
    
