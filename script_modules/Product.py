# Product.py

import com.ihsan.foundation.pobject as pobject
import simplejson
import sys
import com.ihsan.fileutils as utils
import com.ihsan.net.socketclient as socketclient
import types

# GLOBALS
class Product(pobject.PObject): 
  # static variable
  pobject_classname = 'Product'
  pobject_keys = ['ProductId']
  
  def pobject_init(self):
    # code : description
    self.defaultGLInt = {
      'PHP_ZAKAT' : 'Account Penerimaan Zakat',
      'AMIL_ZAKAT' : 'Account Penerimaan Pengelola dari Zakat',
      'PDG_ZAKAT' : 'Account Penyaluran Zakat',
      'PHP_INFAQ' : 'Account Penerimaan Infaq',
      'AMIL_INFAQ' : 'Account Penerimaan Pengelola dari Infaq',
      'PDG_INFAQ' : 'Account Penyaluran Infaq',
      'PHP_WAKAF' : 'Account Penerimaan Wakaf',
      'AMIL_WAKAF' : 'Account Penerimaan Pengelola dari Wakaf',
      'PDG_WAKAF' : 'Account Penyaluran Wakaf',
      'PDG_AMIL' : 'Biaya Operasional Cabang',
      'PHP_NONHALAL' : 'Infaq Dana Fasilitas Umum',
      'PDG_NONHALAL' : 'Penyaluran Dana Fasilitas Umum',   
    }
    self.gltag='PRODUCT'
    
  def SetHierarchy(self): 
    ParentProductId = self.ParentProductId or 0
    while ParentProductId != 0:
      oParent = self.Helper.GetObject('Product',ParentProductId)
      
      oPHierarchy = self.Helper.CreatePObject('ProductHierarchy')
      oPHierarchy.ParentProductId = ParentProductId
      oPHierarchy.ChildProductId = self.ProductId
      oPHierarchy.Level = self.Level - oParent.Level

      ParentProductId = oParent.ParentProductId
    #--end while
  
  def GetAccountInterface(self, aInterfaceCode):
    oIntf = self.Helper.GetObjectByNames(
      'GLInterface',
      {
        'ProductId': self.ProductId,
        'InterfaceCode': aInterfaceCode
      }
    )
    
    if oIntf.IsNull:
      raise 'Product', 'GL interface %s cannot be found' % aInterfaceCode
    #-- if
    
    return oIntf
  
  def CheckForDelete(self):
    sqlCheck = 'select count(productid) from product where parentproductid=%d' % (self.ProductId)
    
    resSQL = self.Config.CreateSQL(sqlCheck).rawresult
    if resSQL.GetFieldValueAt(0) > 0:
      raise '','Data tidak dapat dihapus karena menjadi referensi oleh data lain'
      
    sqlCheck = 'select count(productid) from productaccount where productid=%d' % (self.ProductId)
    
    resSQL = self.Config.CreateSQL(sqlCheck).rawresult
    if resSQL.GetFieldValueAt(0) > 0:
      raise '','Data tidak dapat dihapus karena menjadi referensi oleh data lain'
      
    return 1

  def GLInterfaceExist(self):
    sql = "select count(*) from GLInterface where productid=%d" % self.ProductId    
    resSQL = self.Config.CreateSQL(sql).rawresult     
    return resSQL.GetFieldValueAt(0) or 0
    
  def GenerateGLInterface(self):
    sql = "select * from parameterglobal where tag='%s' " % self.gltag      
    
    resParamGlobal = self.Config.CreateSQL(sql).rawresult
    
    #for code,description in self.defaultGLInt.items():
    while not resParamGlobal.Eof:
      oGLInt = self.Helper.GetObjectByNames('GLInterface',
         { 'ProductId' : self.ProductId, 
           'InterfaceCode' : resParamGlobal.default_code 
         }
      )
      if oGLInt.isnull:
        oGLInt = self.Helper.CreatePObject('GLInterface')
        oGLInt.ProductId = self.ProductId
        oGLInt.InterfaceCode = resParamGlobal.default_code
        oGLInt.Description = resParamGlobal.deskripsi
        oGLInt.AccountCode = resParamGlobal.nilai_parameter_string
        oAccount = self.Helper.GetObject('Account',oGLInt.AccountCode)
        if oAccount.isnull : '','Account Code %s Tidak Ditemukan' % oGLInt.AccountCode
        oGLInt.AccountName = oAccount.Account_Name      

      resParamGlobal.Next()          
    # end while
        
class ZakahProduct(Product):  
  # static variable
  pobject_classname = 'ZakahProduct'
  
  def pobject_init(self):
    # code : description
    self.defaultGLInt = {
      'PHP_ZAKAT' : 'Account Penerimaan Zakat',
      'AMIL_ZAKAT' : 'Account Penerimaan Pengelola dari Zakat',
      'PDG_ZAKAT' : 'Account Penyaluran Zakat',   
    }
    self.gltag='GLI_ZAKAT'
  
class Program(Product):
  # static variable
  pobject_classname = 'Program'

  def pobject_init(self):
    # code : description
    self.gltag='GLI_PROGRAM'

class Project(Product):
  # static variable
  pobject_classname = 'Project'

  def pobject_init(self):
    # code : description
    self.gltag='GLI_PROJECT'

class ProductHierarchy(pobject.PObject):
  # static variable
  pobject_classname = 'ProductHierarchy'
  pobject_keys = ['HierarchyId']
                
class GLInterface(pobject.PObject):
  # static variable
  pobject_classname = 'GLInterface'
  pobject_keys = ['InterfaceId']
                
