import com.ihsan.foundation.pobjecthelper as phelper
import time, sys

def FillDataView(uideflist, rec, parameter) :
    helper = phelper.PObjectHelper(uideflist.config)
    Obj, Field = helper.LoadScript('GeneralModule.S_ObjectEditor').FindObj(uideflist.config, 'Donor',
      ((parameter.FirstRecord.ID,parameter.FirstRecord.key),))
    Obj = Obj.CastToLowestDescendant()
    uideflist.SetData('uipData'+Obj.DonorType,Obj.PObjConst)
    rec.ViewType = Obj.DonorType
    rec.Data = Obj.GetFieldByName(parameter.FirstRecord.ID)
    return rec
    
def FormSetDataEx(uideflist, parameter) :
    config = uideflist.config
    helper = phelper.PObjectHelper(uideflist.config)
    paramMode = {
     'New':'rec',
     'Edit':'helper.LoadScript(\'GeneralModule.S_ObjectEditor\').FillDataMode(uideflist,rec, parameter)',
     'View':'FillDataView(uideflist,rec, parameter)',
     'SENTINEL':''
    }
    rec = uideflist.uipFilter.Dataset.AddRecord()

    rec = eval(paramMode[parameter.FirstRecord.mode])
    ID = parameter.FirstRecord.ID
    rec.ID = ID
    rec.mode = parameter.FirstRecord.mode
    rec.UserPengubah = config.SecurityContext.UserId
    rec.TglUbah = (config.Now())
    rec.TerminalUbah = config.SecurityContext.InitIP
    rec.Input_Data = 'I'
    rec.TglAwal = rec.TglUbah
    rec.TglAkhir = rec.TglUbah

def FindData(config, parameter, returns):
  helper = phelper.PObjectHelper(config)
  FieldStruct = ('DonorId','DonorName','AddressStreet','AddressKelurahan',
          'AddressSubDistrict','AddressCity','AddressProvince','AddressPostalCode',
          'PhoneNumber','MobileNumber','Email','Fax','ReferenceBy')
  ChildFields = {
    'IndividualDonor':('Gender','BirthPlace','BirthDate','IdentityType',
          'IdentityNumber','Religion','NPWP','MaritalState','Language',
          'LastFormalEducation','FieldOfWork','IncomePerMonth','ExpensePerMonth'),
    'CorporateDonor':('Corporation','NPWP','SIUPP',
          'TDP','LocationType','OwnerType','EconomicSector')
  }
  if parameter.FirstRecord.SearchType == 'I' :
    Idx=0
  else :
    Idx=8

  param = '%s = \'%s\' ' % \
    (FieldStruct[Idx],parameter.FirstRecord.Data)

  #loop sql mengisi record
  strSQL = 'select %s from Donor where %s ' %(parameter.FirstRecord.IDName,param)
  
  resSQL = config.CreateSQL(strSQL).RawResult
  resSQL.First()
  LsVal = ()
  Type = ''
  if not resSQL.Eof :
    Obj = config.CreatePObjImplProxy(parameter.FirstRecord.ClassName)
    Obj.Key = resSQL.GetFieldValue(parameter.FirstRecord.IDName)
    Obj = Obj.CastToLowestDescendant()
    FieldStruct += ChildFields[Obj.ClassName]
    Type = Obj.DonorType
    for field in FieldStruct :
      LsVal += (Obj.GetFieldByName(field),)
      
  returns.CreateValues(['uip','uipData'+Type],['Struct',str(FieldStruct)],['Values',str(LsVal)])

  return 1

def GetHistData(config, parameter, returns) :
  FieldStruct = ('TransactionItemId','TransactionDate','TransactionCode','BranchCode',
    'MutationType','Amount','CurrencyCode','Rate','EkuivalenAmount')
  
  helper = phelper.PObjectHelper(config)
  #oParameterGlobal = helper.GetObject('ParameterGlobal', 'FIN_PART')
  oParameterGlobal = config.CreatePObjImplProxy('ParameterGlobal')
  oParameterGlobal.key = 'HIST_COUNT'
  #FIN = int(oParameterGlobal.Nilai_Parameter)
  FIN = 100
  
  returns.CreateValues(['FIN',FIN],['uip','uipTrans'],['Struct',str(FieldStruct)])
  returnpacket.AddDataPacketStructureEx('uipResult','Values:string')
  returnpacket.BuildAllStructure()
  dsResult = returnpacket.AddNewDataset('uipResult')
  
  s = ' \
            SELECT FROM AccountTransactionItem \
            [ \
              Nomor_Rekening = :Nomor_Rekening and \
              Tanggal_Transaksi >= :Tanggal_Awal and \
              Tanggal_Transaksi < :Tanggal_Akhir \
            ] \
            ( \
              Id_Detil_Transaksi, \
              Tanggal_Transaksi, \
              Id_Parameter_Transaksi, \
              Kode_Jurnal, \
              Keterangan, \
              Jenis_Mutasi, \
              Saldo_Awal, \
              Nilai_Mutasi, \
              LHistTransaksi.Nomor_Referensi, \
              LHistTransaksi.LBatchTransaksi.Nomor_Batch,\
              LHistTransaksi.Tanggal_Input,\
              Self \
            ) \
            THEN ORDER BY ASC , ASC Id_Detil_Transaksi;'
            
  strSQL = 'select '
  for Field in FieldStruc :
    strSQL += Field + ','
  strSQL = strSQL[:-1] + ' from TransactionItem where %s ' %param

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
