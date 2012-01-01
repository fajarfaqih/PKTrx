import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist,parameters):
  config = uideflist.config
  helper = phelper.PObjectHelper(config)
  
  #ContainerId = parameters.FirstRecord.ContainerId
  oParameter = config.AccessPObject(parameters.FirstRecord.key)

  CheckGLInterface(config,oParameter)
  key = 'PObj:GLInterfaceContainer#GLIContainerId=%d' % oParameter.GLIContainerId
  uideflist.SetData('uipGLIContainer', key)

def CheckGLInterface(config,oParameter):
  helper = phelper.PObjectHelper(config)
  
  oParameter = helper.GetObjectByInstance(oParameter.classname,oParameter)
  #if oParameter.GLInterfaceExist(): return

  config.BeginTransaction()
  try:
    oParameter.GenerateGLInterface()
    config.Commit()
  except:
    config.Rollback()
    raise

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


