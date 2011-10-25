import com.ihsan.foundation.pobjecthelper as phelper
import sys
import os
import shutil
import com.ihsan.fileutils as utils
import string

def FormSetDataEx(uideflist,parameters):
  config = uideflist.Config
  param = parameters.FirstRecord

  if parameters.DatasetCount == 0 : return
  
  DonorId = parameters.FirstRecord.DonorId
  helper = phelper.PObjectHelper(config)

#  TransactionId = param.TransactionID

#  oTransaction = helper.GetObject('Transaction',TransactionId)
#  if oTransaction.TransactionCode not in ['SD001'] :
#    raise 'PERINGATAN','Trasaksi bukan merupakan penghimpunan dana'

#  DonorId = oTransaction.GetDonorId()

  oDonor = helper.CreateObject('ExtDonor')

  oDonor.GetData(DonorId)

  uipData = uideflist.uipData.Dataset
  if uipData.RecordCount == 0 : rec = uideflist.uipData.Dataset.AddRecord()
  else : rec = uideflist.uipData.Dataset.GetRecord(0)
#  rec.TransactionId = TransactionId
  rec.Nama_Muzakki = oDonor.full_name
  rec.Alamat = oDonor.address
  rec.NPWP = oDonor.npwp_no
  rec.NPWZ = oDonor.npwz_no
  rec.BSZNo = GenerateBSZNo(config)
  rec.DonorId = DonorId
  rec.BSZDate = config.Now()
  #rec.Jumlah = oTransaction.GetZakahAmount()
  rec.Jumlah = 0.0
  rec.JumlahDetail = 0.0


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

def BSZNew(config,parameters,returns):
  status = returns.CreateValues(
     ['IsErr',0],
     ['ErrMessage',''],
     ['BSZId',0],
  )

  helper = phelper.PObjectHelper(config)
  config.BeginTransaction()
  try:

    uipData = parameters.uipData.GetRecord(0)

    # Create Data BSZ & BSZTransaction
    oBSZ = helper.CreatePObject('BSZ')
    oBSZ.BSZNumber = uipData.BSZNo
    oBSZ.DonorId = uipData.DonorId
    oBSZ.BSZDate = config.Now()

    Transaction = parameters.uipTransaction
    for i in range(Transaction.RecordCount):
       rec = Transaction.GetRecord(i)
       oTran = helper.GetObject('TransactionItem',rec.TransactionItemId)
       oTran.CreateBSZTransaction(oBSZ.BSZId)


    Detail = parameters.uipDetail

    for i in range(Detail.RecordCount):
      rec = Detail.GetRecord(i)

      # Create BSZDetail
      oBSZDetail = helper.CreatePObject('BSZDetail')
      oBSZDetail.BSZId = oBSZ.BSZId
      oBSZDetail.Item = rec.ItemNo
      oBSZDetail.Percentage = rec.Kadar
      oBSZDetail.Year = rec.TahunPerolehan
      oBSZDetail.BasicValue = rec.DasarPengenaan
      oBSZDetail.ZakahValue = rec.Jumlah
    # end for

    status.BSZId = oBSZ.BSZId
    
    config.Commit()
  except:
    config.Rollback()
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])


