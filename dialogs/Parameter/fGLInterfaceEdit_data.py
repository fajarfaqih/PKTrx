import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist,parameters):
  config = uideflist.config
  oProduct = config.AccessPObject(parameters.FirstRecord.key)
  if oProduct.IsDetail <> 'T':
    raise 'OnSetDataEx', 'Not transaction product!'

  CheckGLInterface(config,oProduct)
  uideflist.SetData('uipProduct',parameters.FirstRecord.key)

def CheckGLInterface(config,oProduct):
  helper = phelper.PObjectHelper(config)
  
  oProduct = helper.GetObjectByInstance(oProduct.classname,oProduct)
  if oProduct.GLInterfaceExist(): return

  config.BeginTransaction()
  try:
    oProduct.GenerateGLInterface()
    config.Commit()
  except:
    config.Rollback()

def Form_OnGeneralProcessData(uideflist,packet):

  config = uideflist.Config
  helper = phelper.PObjectHelper(config)
  

  recProduct = packet.uipProduct.GetRecord(0)

  LsGLInterface = packet.LsGLInterface

  #for i in range(LsGLInterface.RecordCount):
  #  recGLInterface = LsGLInterface.GetRecord(i)
  #  if recGLInterface.__SYSFLAG == 'N' :
  #    raise '',recGLInterface.AccountCode

  #mfas = helper.GetPClass('BaitiJannatiFacility')
  #
  #facilityTypeCode  = rec.GetFieldByName('tipefasilitas.tpfkod')
  #rec.mfnuf = mfas.GetSequenceNo(helper, rec.GetFieldByName('m1hk.nonsbh'), facilityTypeCode)
  #rec.mfkdc = config.securitycontext.GetUserInfo()[4]

  return 1
  
def GLOnSetData(sender):
  rec = sender.ActiveRecord
  rec.SetFieldByName('LAccount.Account_Code',rec.AccountCode)


