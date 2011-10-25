# Batch.py
import simplejson
import com.ihsan.foundation.pobjecthelper as phelper

def Create(config, srequest):
  request = simplejson.loads(srequest)
  helper = phelper.PObjectHelper(config)
  
  config.BeginTransaction()
  try:

    
    #oBatchCheck = helper.GetObjectByNames('TransactionBatch',
    #   { 'Inputer':request[u'Inputer'],
    #     'BatchDate' : request[u'BatchDate'],
    #   }
    #)
    #if not oBatchCheck.isnull :
    #  raise 'PERINGATAN',"Batch dengan keterangan '%s' sudah digunakan.\nSilahkan ganti deskripsi batch" % request[u'Description']
    StrTanggal = config.FormatDateTime('dd/mm/yyyy',request[u'BatchDate'])
    Description = '%s_%s' % (request[u'Inputer'],StrTanggal)
      
    oBatchCheck = helper.GetObjectByNames('TransactionBatch',
       {'Inputer':request[u'Inputer'],
        'Description' : Description,
        'IsPosted' : 'T',
        }
    )
    if not oBatchCheck.isnull :
      #raise 'PERINGATAN',"Batch dengan keterangan '%s' sudah digunakan.\nSilahkan ganti deskripsi batch" % Description
      raise 'PERINGATAN',"Batch untuk tanggal %s telah tersedia.\nSilahkan buat batch untuk tanggal lain" % StrTanggal
      
    oBatch = helper.CreatePObject('TransactionBatch')
    oBatch.BatchDate  = request[u'BatchDate']
    oBatch.BranchCode   = request[u'BranchCode']
    oBatch.Inputer      = request[u'Inputer']
    oBatch.Description  = Description
    oBatch.BatchTag = 'OPR'
    
    config.Commit()
  except:
    config.Rollback()
    raise
  
  config.BeginTransaction()
  try:
    oBatch.PostToAccounting()
    
    config.Commit()
  except:
    config.Rollback()
    raise
  
  response = {}
  response['BatchNo'] = oBatch.BatchNo
  response['Description'] = oBatch.Description
  
  return simplejson.dumps(response)
  