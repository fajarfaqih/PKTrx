import com.ihsan.foundation.pobjecthelper as phelper
import time, sys, os

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
    #paramMode = {
    # 'New':'rec',
    # 'Edit':'helper.LoadScript(\'GeneralModule.S_ObjectEditor\').FillDataMode(uideflist,rec, parameter)',
    # 'View':'FillDataView(uideflist,rec, parameter)',
    # 'SENTINEL':''
    #}
    rec = uideflist.uipFilter.Dataset.AddRecord()

    #rec = eval(paramMode[parameter.FirstRecord.mode])
    #ID = parameter.FirstRecord.ID
    #rec.ID = ID
    #rec.mode = parameter.FirstRecord.mode
    #rec.UserPengubah = config.SecurityContext.UserId
    #rec.TglUbah = (config.Now())
    #rec.TerminalUbah = config.SecurityContext.InitIP
    #rec.Input_Data = 'I'
    rec.TglAwal = (config.Now())
    rec.TglAkhir = rec.TglAwal

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

def AsDateTime(config,tdate):
  utils = config.ModLibUtils
  return utils.EncodeDate(tdate[0], tdate[1], tdate[2])

def GetHistTransaction(config, params, returns) :


  helper = phelper.PObjectHelper(config)

  status = returns.CreateValues(
      ['Is_Err',0],['Err_Message','']
  )
  
  rec = params.FirstRecord
  DonorId = rec.DonorId
  BeginDate = int(rec.BeginDate)
  EndDate   = int(rec.EndDate)
  
  dsHist = returns.AddNewDatasetEx(
    'histori',
    ';'.join([
      'TransactionItemId: integer',
      'TransactionDate: datetime',
      'TransactionCode: string',
      'BranchCode: string',
      'MutationType: string',
      'Amount: float',
      'ReferenceNo: string',
      'Description: string',
      'Inputer: string',
      'AccountName: string',
      'InvoiceStatus: string',
      'InvoiceDate: datetime',
      'InvoiceNo: string',
    ])
  )
  
  s = ' \
    SELECT FROM SponsorTransactionProgram \
    [ \
      SponsorId = :DonorId and \
      LTransaction.LTransaction.TransactionDate >= :BeginDate and \
      LTransaction.LTransaction.TransactionDate < :EndDate \
    ] \
    ( \
      TransactionItemId, \
      LTransaction.LTransaction.TransactionDate, \
      LTransaction.LTransaction.TransactionCode, \
      LTransaction.LTransaction.BranchCode, \
      LTransaction.MutationType, \
      LTransaction.Amount, \
      LTransaction.LTransaction.ReferenceNo, \
      LTransaction.LTransaction.Description, \
      LTransaction.LTransaction.Inputer, \
      LTransaction.LFinancialAccount.AccountName, \
      InvoiceStatus, \
      InvoiceDate, \
      InvoiceNo, \
      Self \
    ) \
    THEN ORDER BY ASC TransactionDate, ASC TransactionItemId;'

  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('DonorId', DonorId)
  oql.SetParameterValueByName('BeginDate', BeginDate)
  oql.SetParameterValueByName('EndDate', EndDate + 1)
  oql.ApplyParamValues()

  oql.active = 1
  ds  = oql.rawresult

  while not ds.Eof:
    recHist = dsHist.AddRecord()
    recHist.TransactionItemId = ds.TransactionItemId
    recHist.TransactionDate = AsDateTime(config,ds.TransactionDate)
    recHist.TransactionCode = ds.TransactionCode
    recHist.BranchCode = ds.BranchCode
    recHist.MutationType = ds.MutationType
    recHist.Amount = ds.Amount
    recHist.ReferenceNo = ds.ReferenceNo
    recHist.Description = ds.Description
    recHist.Inputer = ds.Inputer
    recHist.AccountName = ds.AccountName
    recHist.InvoiceStatus = ds.InvoiceStatus
    if ds.InvoiceDate != None : recHist.InvoiceDate = AsDateTime(config,ds.InvoiceDate)
    recHist.InvoiceNo = ds.InvoiceNo

    ds.Next()

  # end while
    
  return 1
  

def PrintHistTransaction(config, params, returns):
  def AsString(tdate):
    return ('%s-%s-%s' % (str(tdate[2]), str(tdate[1]), str(tdate[0])))

  helper = phelper.PObjectHelper(config)

  status = returns.CreateValues(
      ['Is_Err',0],['Err_Message','']
  )
  
  rec = params.FirstRecord
  DonorId = rec.DonorId
  DonorNo = rec.DonorNo
  DonorName = rec.DonorName
  BeginDate = int(rec.BeginDate)
  EndDate   = int(rec.EndDate)

  s = ' \
    SELECT FROM SponsorTransactionProgram \
    [ \
      SponsorId = :DonorId and \
      LTransaction.LTransaction.TransactionDate >= :BeginDate and \
      LTransaction.LTransaction.TransactionDate < :EndDate \
    ] \
    ( \
      LTransaction.TransactionItemId, \
      LTransaction.LTransaction.TransactionDate, \
      LTransaction.LTransaction.TransactionCode, \
      LTransaction.MutationType, \
      LTransaction.Amount, \
      LTransaction.LTransaction.ReferenceNo, \
      LTransaction.LTransaction.Description, \
      LTransaction.LTransaction.Inputer, \
      LTransaction.LTransaction.TransactionNo, \
      Self \
    ) \
    THEN ORDER BY ASC TransactionDate, ASC TransactionItemId;'

  oql = config.OQLEngine.CreateOQL(s)
  oql.SetParameterValueByName('DonorId', DonorId)
  oql.SetParameterValueByName('BeginDate', BeginDate)
  oql.SetParameterValueByName('EndDate', EndDate + 1)
  oql.ApplyParamValues()
  #raise '',oql.SQLText

  oql.active = 1
  ds  = oql.rawresult

  # Prepare Excel Object
  PrintHelper = helper.CreateObject('PrintHelper')
  workbook = PrintHelper.LoadExcelTemplate('DonorHistory')
  try :
    workbook.ActivateWorksheet('data')

    workbook.SetCellValue(2, 3, DonorNo)
    workbook.SetCellValue(3, 3, DonorName)
    row = 6
    while not ds.Eof:
      workbook.SetCellValue(row, 1, str(row - 5) )
      workbook.SetCellValue(row, 2, AsString(ds.TransactionDate))
      workbook.SetCellValue(row, 3, ds.Amount)
      workbook.SetCellValue(row, 4, ds.Description)
      workbook.SetCellValue(row, 5, ds.TransactionNo)

      row += 1
      ds.Next()
    # end while

    # save report file
    FileName = 'DonorHistory.xls'
    corporate = helper.CreateObject('Corporate')
    FullName = corporate.GetUserHomeDir() + '\\' + FileName
    if os.access(FullName, os.F_OK) == 1:
        os.remove(FullName)
    workbook.SaveAs(FullName)
    

    sw = returns.AddStreamWrapper()
    sw.LoadFromFile(FullName)
    sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(FullName)
    
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
  # try except
  
  workbook = None
  #-- while
  
def GetSponsorDataByNo(config,params,returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
    ['DonorId',0],
    ['DonorName',''],
    ['PhoneNumber',''],
    ['Address',''],
    ['DonorType',0],
    ['DonorNo',''],
  )

  helper = phelper.PObjectHelper(config)
  try:
    DonorNo = params.FirstRecord.SponsorNo

    oDonor = helper.CreateObject('ExtDonor')

    oDonor.GetDataByDonorNo(DonorNo)

    if oDonor.isnull : raise 'PERINGATAN','Data Donor tidak ditemukan'

    status.DonorId = oDonor.id
    status.DonorNo = oDonor.donor_no
    status.DonorName = oDonor.full_name
    status.PhoneNumber = oDonor.phone_no
    status.Address = oDonor.address
    status.DonorType = oDonor.donor_type_id

  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])

def GetDisburseData(config,params,returns):
  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message',''],
  )

  dsDisburse = returns.AddNewDatasetEx(
    'DisburseData',
    ';'.join([
      'DisbNumber: integer',
      'DisbDatePlan: datetime',
      'DisbAmountPlan: float',
      'DisbId:integer',
    ])
  )
  
  helper = phelper.PObjectHelper(config)
  try:
    ProjectSponsorId = params.FirstRecord.ProjectSponsorId

    s = ' \
      SELECT FROM ProjectSponsorDisbursement \
      [ \
        ProjectSponsorId = :ProjectSponsorId \
      ] \
      ( \
        DisbId, \
        DisbNumber, \
        DisbDatePlan, \
        DisbAmountPlan, \
        Self \
      ) \
      THEN ORDER BY ASC DisbNumber;'

    oql = config.OQLEngine.CreateOQL(s)
    oql.SetParameterValueByName('ProjectSponsorId', ProjectSponsorId)
    oql.ApplyParamValues()

    oql.active = 1
    ds  = oql.rawresult
    while not ds.Eof:
      recDisburse = dsDisburse.AddRecord()
      recDisburse.DisbNumber = ds.DisbNumber
      recDisburse.DisbDatePlan = AsDateTime(config,ds.DisbDatePlan)
      recDisburse.DisbAmountPlan = ds.DisbAmountPlan
      recDisburse.DisbId = ds.DisbId
      ds.Next()

  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])

