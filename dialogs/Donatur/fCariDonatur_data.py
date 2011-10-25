import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter) :
  rec = uideflist.uipData.Dataset.AddRecord()
  rec.ID = parameter.FirstRecord.ID
  rec.mode = parameter.FirstRecord.mode


def CariData(config, parameter, returnpacket):

  FieldStruc = ('DonorId','DonorType','DonorName','PhoneNumber','Email','AddressStreet','Status')

  helper = phelper.PObjectHelper(config)
  #oParameterGlobal = helper.GetObject('ParameterGlobal', 'FIN_PART')
  oParameterGlobal = config.CreatePObjImplProxy('ParameterGlobal')
  oParameterGlobal.key = 'FIN_PART'
  
  FIN = int(oParameterGlobal.Nilai_Parameter)

  returnpacket.CreateValues(['FIN',FIN],['Struct',str(FieldStruc)])

  returnpacket.AddDataPacketStructureEx('uipResult','Values:string')

  returnpacket.BuildAllStructure()

  dsResult = returnpacket.AddNewDataset('uipResult')

  param = "upper(%s) like '%%%s%%' LIMIT %d" % (
    parameter.FirstRecord.ID, parameter.FirstRecord.Value, FIN)
    
  #loop sql mengisi record
  strSQL = 'select '
  for Field in FieldStruc :
    strSQL += Field + ','
  strSQL = strSQL[:-1] + ' from Donor where %s ' %param

  resSQL = config.CreateSQL(strSQL).RawResult
  resSQL.First()

  while not resSQL.Eof :
    rec = dsResult.AddRecord()
    LsVal = ()
    for field in FieldStruc :
      LsVal += (resSQL.GetFieldValue(field),)
    rec.Values = str(LsVal)
    resSQL.Next()
    
  return 1

