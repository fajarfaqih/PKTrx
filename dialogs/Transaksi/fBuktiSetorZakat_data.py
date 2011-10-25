import com.ihsan.foundation.pobjecthelper as phelper
import sys
import os
import shutil
import com.ihsan.fileutils as utils
import string

def FormSetDataEx(uideflist,parameters):
  config = uideflist.Config
  param = parameters.FirstRecord

  #if parameters.DatasetCount == 0 :
  rec = uideflist.uipData.Dataset.AddRecord()

  rec.BSZNo = GenerateBSZNo(config)

  return
#  helper = phelper.PObjectHelper(uideflist.config)

#  TransactionId = param.TransactionID

#  oTransaction = helper.GetObject('Transaction',TransactionId)
#  if oTransaction.TransactionCode not in ['SD001'] :
#    raise 'PERINGATAN','Trasaksi bukan merupakan penghimpunan dana'

#  DonorId = oTransaction.GetDonorId()

#  oDonor = helper.CreateObject('ExtDonor')

#  oDonor.GetData(DonorId)

#  uipData = uideflist.uipData.Dataset
#  if uipData.RecordCount == 0 : rec = uideflist.uipData.Dataset.AddRecord()
#  else : rec = uideflist.uipData.Dataset.GetRecord(0)
#  rec.TransactionId = TransactionId
#  rec.Nama_Muzakki = oDonor.full_name
#  rec.Alamat = oDonor.address
#  rec.NPWP = oDonor.npwp_no
#  rec.NPWZ = oDonor.npwz_no
#  rec.Jumlah = oTransaction.GetZakahAmount()
#  rec.JumlahDetail = 0.0


def GenerateBSZNo(config):
  y,m,d = config.ModLibUtils.DecodeDate(config.Now())

  BranchCode = config.SecurityContext.GetUserInfo()[4]
  strY = str(y)
  strM = str(m).zfill(2)

  rsSeq = config.CreateSQL("select nextval('seq_bsznumber')").RawResult
  strSequence = str(rsSeq.GetFieldValueAt(0)).zfill(7)

  return  "PKPU-%s/BSZ/%s%s%s" % (
       BranchCode,
       strY,strM,
       strSequence)

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

