import com.ihsan.foundation.pobjecthelper as phelper

def CariData(config, parameter, returns):
  
  #FieldStruc = ('DonorId','DonorType','DonorName','PhoneNumber','Email','AddressStreet','Status')
  GridFields = ('DonorId','DonorType','DonorName','PhoneNumber','Email','AddressStreet','Status','DonorIntId','NPWP','NPWZ','MarketerId','MarketerName')

  TableFields = ('donor_no','donor_type_id', 'full_name', 'phone_no', 'email', 'address', 'user_status' ,'a.id','npwp_no','npwz_no','marketer_id')
  TableAliasFields = ('donor_no','donor_type_id', 'full_name', 'phone_no', 'email', 'address', 'user_status' ,'id','npwp_no','npwz_no','marketer_id','marketer_name')
  helper = phelper.PObjectHelper(config)
  oParameterGlobal = config.CreatePObjImplProxy('ParameterGlobal')
  oParameterGlobal.key = 'FIN_PART'

  FIN = int(oParameterGlobal.Nilai_Parameter)

  returns.CreateValues(['FIN',FIN],['Struct',str(GridFields)])
  returns.AddDataPacketStructureEx('uipResult','Values:string')
  returns.BuildAllStructure()

  dsResult = returns.AddNewDataset('uipResult')

  ControlID = parameter.FirstRecord.ID
  FilterValue = parameter.FirstRecord.Value
  addParam = ''
  if parameter.FirstRecord.IsAllCabang == 'F' :
    #corporate = helper.CreateObject('Corporate')
    #login_context = corporate.LoginContext
    #CabangInfo = corporate.GetCabangInfo(login_context.Kode_Cabang)
    UserInfo = config.SecurityContext.GetUserInfo()
    BranchId = int(UserInfo[2])
    #addParam += ' and branch_id=%d' % BranchId
    
    GroupBranchCode = str(UserInfo[3])
    addParam += " and exists( \
                         select 1 from transaction.branch tb \
                         where tb.BranchId=a.branch_id and \
                          GroupBranchCode= '%s' ) "% GroupBranchCode



  FieldFilter = { 'DonorId' : 'donor_no',
                'PhoneNumber' : 'phone_no',
                'DonorName' : 'full_name',
                'DonorEmail' : 'email'}
                
  param1 = " upper(%s) ~ '^%s' %s " % (
    FieldFilter[ControlID], FilterValue ,addParam)

  param2 = " upper(%s) ~ '^.+%s' %s " % (
    FieldFilter[ControlID], FilterValue ,addParam)
    
  #loop sql mengisi record
  strSQL = ''
  strSQL += 'select %s,(select full_name from public.sdm_employee c where a.marketer_id=c.id) as marketer_name,1 as rank from public.php_donor a left outer join public.php_donor_phone b on (a.phone_id=b.id) where %s ' % (
     ','.join(TableFields), param1)
  strSQL += ' union '
  strSQL += 'select %s,(select full_name from public.sdm_employee c where a.marketer_id=c.id) as marketer_name, 2 as rank from public.php_donor a left outer join public.php_donor_phone b on (a.phone_id=b.id) where %s '  % (
     ','.join(TableFields), param2)

  strSQL += 'order by rank, full_name,address LIMIT %d' % (FIN)
  
  resSQL = config.CreateSQL(strSQL).RawResult
  resSQL.First()

  while not resSQL.Eof :
    rec = dsResult.AddRecord()
    LsVal = ()
    for alias in TableAliasFields :
      LsVal += (resSQL.GetFieldValue(alias),)

    rec.Values = str(LsVal)
    resSQL.Next()
  # end while
  
  return 1

