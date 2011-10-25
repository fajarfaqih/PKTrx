import com.ihsan.foundation.pobjecthelper as phelper
import sys
import os
import shutil
import com.ihsan.fileutils as utils
import string
import com.ihsan.timeutils as timeutils

def FormSetDataEx(uideflist,parameters):
  config = uideflist.Config
  param = parameters.FirstRecord

  #if parameters.DatasetCount == 0 :
  rec = uideflist.uipData.Dataset.AddRecord()



def BSZDelete(config,parameters,returns):
  status = returns.CreateValues(
     ['IsErr',0],
     ['ErrMessage',''],
  )
  
  config.BeginTransaction()
  try:
    BSZId = parameters.FirstRecord.BSZId
    
    helper = phelper.PObjectHelper(config)

    oBSZ = helper.GetObject('BSZ',BSZId)
    oBSZ.Delete()
    
    config.Commit()
  except:
    config.Rollback()
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])

def GenerateBSZ2(helper,oBSZ):
  config = helper.Config
  oDonor = oBSZ.LDonor

def BSZPrint(config,parameters,returns):
  status = returns.CreateValues(
     ['IsErr',0],
     ['ErrMessage',''],
  )

  try:
    BSZId = parameters.FirstRecord.BSZId

    helper = phelper.PObjectHelper(config)

    oBSZ = helper.GetObject('BSZ',BSZId)

    #DataBSZ = GenerateBSZ2(helper,oBSZ)
    DataBSZ = oBSZ.GenerateBSZData()

    PrintHelper = helper.CreateObject('PrintHelper')
    templateBSZ = PrintHelper.LoadRtfTemplate('tplbszbaru')


    BSZ = templateBSZ % DataBSZ

    corporate = helper.CreateObject('Corporate')
    HomeDir = corporate.GetUserHomeDir() + '\\'

    sBaseFileName = "bsz.rtf"

    sFileName = HomeDir + sBaseFileName

    oFile = open(sFileName,'w')

    try:
      oFile.write(BSZ)
    finally:
      oFile.close()

    sw = returns.AddStreamWrapper()
    sw.Name = 'bsz'
    sw.LoadFromFile(sFileName)
    #sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(sFileName)
    sw.MIMEType = 'application/msword'

  except:
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])

  
def GetBSZList(config,parameters,returns):
  status = returns.CreateValues(
     ['IsErr',0],
     ['ErrMessage',''],
  )
  
  dsBSZ = returns.AddNewDatasetEx(
    'bszlist',
    ';'.join([
      'BSZDate : datetime',
      'BSZNumber : string',
      'BSZId : integer',
      'Total : float'
    ])
  )


  helper = phelper.PObjectHelper(config)
  try:
    param = parameters.FirstRecord
    DonorId = param.DonorId

    sOQL = " \
      select from BSZ \
      [ DonorId = :DonorId ] \
      ( BSZNumber, \
        BSZDate, \
        BSZId, \
        self ); \
    "
    
    oql = config.OQLEngine.CreateOQL(sOQL)
    oql.SetParameterValueByName('DonorId', DonorId)
    oql.ApplyParamValues()

    oql.active = 1
    ds  = oql.rawresult

    while not ds.Eof:
      rec = dsBSZ.AddRecord()
      rec.BSZNumber = ds.BSZNumber
      rec.BSZDate = timeutils.AsTDateTime(config, ds.BSZDate)
      rec.BSZId = ds.BSZId
      oBSZ = helper.GetObject('BSZ',ds.BSZId)
      rec.Total = oBSZ.GetTotal()

      ds.Next()
    # end while

    

  except:
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])

  
def CetakBSZ(config,parameters,returns):
  status = returns.CreateValues(
     ['IsErr',0],
     ['ErrMessage',''],
     ['StreamName',''],
  )

  helper = phelper.PObjectHelper(config)
  config.BeginTransaction()
  try:
    DataBSZ = GenerateBSZ(config,helper,parameters)

    PrintHelper = helper.CreateObject('PrintHelper')
    templateBSZ = PrintHelper.LoadRtfTemplate('tplbsz')


    BSZ = templateBSZ % DataBSZ

    corporate = helper.CreateObject('Corporate')
    HomeDir = corporate.GetUserHomeDir() + '\\'

    sBaseFileName = "bsz.rtf"

    sFileName = HomeDir + sBaseFileName

    oFile = open(sFileName,'w')

    try:
      oFile.write(BSZ)
    finally:
      oFile.close()

    sw = returns.AddStreamWrapper()
    sw.Name = 'bsz'
    sw.LoadFromFile(sFileName)
    #sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(sFileName)
    sw.MIMEType = 'application/msword'

    #status.StreamName = sw.Name
    config.Commit()
  except:
    config.Rollback()
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])

def GenerateBSZ(config,helper,parameters):
    uipData = parameters.uipData.GetRecord(0)

    # Get Tools
    ToolsConvert = helper.LoadScript('Tools.S_Convert')

    # Get Info Donor
    #DonorId = self.GetDonorId()
    #oDonor = helper.CreateObject('ExtDonor')

    #if not oDonor.GetData(DonorId): raise 'PERINGATAN','Data Donor tidak ditemukan'

    Address = ToolsConvert.Divider(uipData.Alamat,50)
    if len(Address) == 1 : Address.append('')

    # Get Total
    #Total = self.GetZakahAmount()
    Total = uipData.Jumlah

    # Set Terbilang
    Terbilang = ToolsConvert.Terbilang(config,Total,
              KodeMataUang = '000',
              NamaMataUang = 'Rupiah')
    #Terbilang = ToolsConvert.Divider(Terbilang,45)
    #if len(Terbilang) == 1 : Terbilang.append('')

    # Get Nama Lembaga
    NamaLembaga = helper.GetObject('ParameterGlobal', 'COMPNAME').Get()

    # Create Data BSZ & BSZTransaction
    oBSZ = helper.CreatePObject('BSZ')
    oBSZ.BSZNumber = uipData.BSZNo
    oBSZ.DonorId = uipData.DonorId

    Transaction = parameters.uipTransaction
    for i in range(Transaction.RecordCount):
       rec = Transaction.GetRecord(i)
       oTran = helper.GetObject('TransactionItem',rec.TransactionItemId)
       oTran.CreateBSZTransaction(oBSZ.BSZId)

    # Prepare Data
    Now = config.Now()
    dataBSZ = {
       'BSZNO' : uipData.BSZNo , #oDonor.full_name,
       'DONOR_NAMA' : uipData.Nama_Muzakki , #oDonor.full_name,
       'NPWP' : uipData.NPWP , #oDonor.npwp_no or '',
       'NPWZ' : uipData.NPWZ , #oDonor.npwz_no or '',
       'DONOR_ALAMAT' : uipData.Alamat,
       'NAMA_LEMBAGA' : NamaLembaga,
       'USER_CETAK' : config.SecurityContext.InitUser,
       'WAKTU_CETAK' : config.FormatDateTime('dd-mm-yyyy hh:nn',Now),
       'TGL_BAYAR' : config.FormatDateTime('dd-mm-yyyy',Now),
       'TOTAL' : config.FormatFloat('#,##0.00',Total),
       'TERBILANG' : Terbilang,
       'CABANG' : NamaLembaga,
       'P1':'','P2':'','P3':'','P4':'','P5':'',
       'P6':'','P7':'','P8':'','P9':'','P10':'',
       'P11':'','P12':'','P13':'','P14':'','P15':'',
       'Z1':'','Z2':'','Z3':'','Z4':'','Z5':'',
       'Z6':'','Z7':'','Z8':'','Z9':'','Z10':'',
       'Z11':'','Z12':'','Z13':'','Z14':'','Z15':'',
        }


    ## PROCESS NPWP_NO
    # get digit no
    npwp = uipData.NPWP or ''
    npwpD = '' #.join(i for i in npwp if i.isdigit())
    for c in npwp:
      if c.isdigit():
        npwpD += c

    # insert to dataBSZ
    idx = 1
    for c in npwpD:
      dataBSZ['P%d'%idx] = c
      idx += 1

    ## PROCESS NPWZ_NO
    # get digit no
    npwz = uipData.NPWZ or ''
    npwzD = '' #''.join(i for i in npwz if i.isdigit())
    for c in npwz:
      if c.isdigit():
        npwzD += c

    # insert to dataBSZ
    idx = 1
    for c in npwzD:
      dataBSZ['Z%d'%idx] = c
      idx += 1

    #raise '',dataBSZ
    #PREFIX = ['EMAS','DAGANG','TANI','TAMBANG','TERNAK','JASA','RIKAZ']
    PREFIX = ['A','B','C','D','E','F','G']

    Detail = parameters.uipDetail

    for i in range(Detail.RecordCount):
      rec = Detail.GetRecord(i)

      TahunPerolehan = ''
      Kadar = ''
      if rec.TahunPerolehan != 0 and rec.Kadar != 0 :
        TahunPerolehan = str(rec.TahunPerolehan)
        Kadar = str(rec.Kadar)
        
      dataBSZ[PREFIX[i]+'_THN'] = TahunPerolehan
      dataBSZ[PREFIX[i]+'_KADAR'] = Kadar

      dataBSZ[PREFIX[i]+'_DASAR'] = config.FormatFloat('#,##0.00',rec.DasarPengenaan)
      dataBSZ[PREFIX[i]+'_ZAKAT'] = config.FormatFloat('#,##0.00',rec.Jumlah)

      # Create BSZDetail
      oBSZDetail = helper.CreatePObject('BSZDetail')
      oBSZDetail.BSZId = oBSZ.BSZId
      oBSZDetail.Item = rec.ItemNo
      oBSZDetail.Percentage = rec.Kadar
      oBSZDetail.Year = rec.TahunPerolehan
      oBSZDetail.BasicValue = rec.DasarPengenaan
      oBSZDetail.ZakahValue = rec.Jumlah


    # end for

    return dataBSZ
    
    PrintHelper = helper.CreateObject('PrintHelper')
    templateBSZ = PrintHelper.LoadHtmTemplate('bsz')
    BSZ = templateBSZ % dataBSZ

    sBaseFileName = "cetakbsz.htm"

    corporate = helper.CreateObject('Corporate')
    sFileName = corporate.GetUserHomeDir() + sBaseFileName
    oFile = open(sFileName,'w')
    try:
      oFile.write(BSZ)
    finally:
      oFile.close()

    return sFileName

