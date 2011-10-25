import com.ihsan.foundation.pobjecthelper as phelper

def AktifkanData(config, parameter, returnpacket) :
  helper = phelper.PObjectHelper(config)
  Obj = config.AccessPObject(parameter.FirstRecord.key)
  if Obj.IsNull :
    raise 'PERINGATAN','Data tidak ditemukan'
  if Obj.Status == 'A' :
    raise 'PERINGATAN','Data sudah dalam status aktif'
  config.BeginTransaction()
  try :
    Obj.Status = 'A'
    rec = helper.LoadScript('GeneralModule.S_ObjectEditor').\
      NonActivateData(config, Obj)
    config.Commit()
  except :
    config.Rollback()
    raise

def DAFScriptMain(config, parameter, returnpacket):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  AktifkanData(config, parameter, returnpacket)

  return 1
