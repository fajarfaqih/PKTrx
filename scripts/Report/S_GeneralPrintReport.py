import com.ihsan.foundation.pobjecthelper as phelper

def CenterText(text, wide=100) :
  lt = len(text)
  if wide > lt :
    text = ('').rjust((wide-lt)/2) + text
    text = text.ljust(wide)
  return text
  
def RightText(text, wide =100) :
  lt = len(text)
  if wide > lt :
    text = text.rjust(wide)
  return text

def LineFeed(ofile, wide=100) :
  for i in range(wide) :
      ofile.write('-')
  ofile.write('\n')
    
def ConstructHeader(config, ofile, mode, wide = 100) :
  ContainDate = 1
  ContainBranch = 1
  ModeHeader = {
   'RekapTransKas':('Rekapitulasi Transaksi Kas',not ContainBranch,ContainDate),
   'RekapDonasi':('Rekapitulasi Donasi',not ContainBranch,ContainDate),
   'SENTINEL':''
  }
  ofile.write(CenterText(ModeHeader[mode][0], wide)+'\n')
  ofile.write(CenterText(config.SysVarIntf.GetStringSysVar('COMPANYINFO','Name'),wide)+'\n')
  if ModeHeader[mode][1] :
    pass
  if ModeHeader[mode][2] :
    y,m,d = config.ModDateTime.DecodeDate(config.Now())
    ofile.write(RightText('Tgl Cetak : %d-%d-%d' %(d,m,y),wide)+'\n')
  
  ofile.write('\n')
  ofile.write('\n')
  
def CreateRekapTransKas(helper, rec, ofile, returns) :
  ConstructHeader(helper.Config, ofile, 'RekapTransKas')
  tableftlr = ', AccountTransactionItem a,TransactionItem ti, Transaction t'
  fltrSQL = 'and c.AccountNo = a.AccountNo and a.TransactionItemId = ti.TransactionItemId and ti.TransactionId = t.TransactionId '
  y1,m1,d1 = helper.Config.ModDateTime.DecodeDate(rec.TglAwal)
  y,m,d = helper.Config.ModDateTime.DecodeDate(rec.TglAkhir+1)
  fltrSQL += 'and TransactionDate >= \'%d/%d/%d\' and TransactionDate < \'%d/%d/%d\' ' % (m1,d1,y1,m,d,y)
  strSQL = 'select distinct(c.AccountNo), UserName from  CashAccount  c %s where c.username is not null %s ' % (tableftlr, fltrSQL)
  resSQL = helper.Config.CreateSQL(strSQL).RawResult  
  resSQL.First()
  FieldStruct = 'Tgl Transaksi|Kode Cabang|Kode Transaksi|Keterangan|No Ref|Kode Valuta|Mutasi|Nominal'
  while not resSQL.Eof :
    ofile.write('Nomor Akun : %s, User : %s \n' %(resSQL.AccountNo,resSQL.UserName))
    LineFeed(ofile)
    strSQL = 'select * from AccountTransactionItem where AccountNo = \'%s\' ' \
      % (resSQL.AccountNo)
    oFA = helper.Config.CreatePObjImplProxy('FinancialAccount')
    oFA.key = resSQL.AccountNo
    ritemSQL = helper.Config.CreateSQL(strSQL).RawResult  
    ritemSQL.First()
    ofile.write(FieldStruct+'\n')
    LineFeed(ofile)
    while not ritemSQL.Eof :
      oItem = helper.Config.CreatePObjImplProxy('AccountTransactionItem')
      oItem.Key = ritemSQL.TransactionItemId
      oTran = oItem.LTransaction
      y,m,d = oTran.TransactionDate[:3]
      Date = '%s/%s/%s' % (d,m,y)
      ofile.write('%s|%s|%s|%s|%s|%s|%s|%s\n' % \
          (CenterText(Date,13),
          CenterText(oItem.BranchCode,11),
          CenterText(oTran.TransactionCode,14),
          CenterText(oTran.Description,10),
          CenterText(oTran.ReferenceNo,6),
          CenterText(oItem.CurrencyCode,11),
          CenterText(oItem.MutationType,6),
          CenterText(str(oItem.Amount),7))
      )
      ritemSQL.Next()
    LineFeed(ofile)
    ofile.write(RightText('Saldo : %d\n\n\n' % oFA.Balance)) 
    resSQL.Next()
  
  return ofile

def CreateRekapDonasi(helper, rec, ofile, returns) :
  ConstructHeader(helper.Config, ofile, 'RekapDonasi')
  fltrSQL = ', AccountTransactionItem a,TransactionItem ti, Transaction t \
    where d.AccountNo = a.DonorAccount and a.TransactionItemId = ti.TransactionItemId \
      and ti.TransactionId = t.TransactionId '
  y1,m1,d1 = helper.Config.ModDateTime.DecodeDate(rec.TglAwal)
  y,m,d = helper.Config.ModDateTime.DecodeDate(rec.TglAkhir+1)
  fltrSQL += ' and TransactionDate >= \'%d/%d/%d\' and TransactionDate < \'%d/%d/%d\' ' % (m1,d1,y1,m,d,y)

  strSQL = 'select distinct(d.AccountNo),DonorId from DonorAccount d %s' % fltrSQL
  resSQL = helper.Config.CreateSQL(strSQL).RawResult  
  resSQL.First()
  FieldStruct = 'Tgl Transaksi|Kode Cabang|Kode Transaksi|Keterangan|No Ref|Kode Valuta|Mutasi|Nominal'
  while not resSQL.Eof :
    Amt = 0
    oDonor = helper.Config.CreatePObjImplProxy('Donor')
    oDonor.key = resSQL.DonorId
    ofile.write('Nomor Id : %s, Nama Donatur : %s \n' %(resSQL.DonorId,oDonor.DonorName))
    LineFeed(ofile)
    strSQL = 'select * from AccountTransactionItem where DonorAccount = \'%s\' ' \
      % (resSQL.AccountNo)
    ritemSQL = helper.Config.CreateSQL(strSQL).RawResult
    ritemSQL.First()
    ofile.write(FieldStruct+'\n')
    LineFeed(ofile)
    while not ritemSQL.Eof :
      oItem = helper.Config.CreatePObjImplProxy('AccountTransactionItem')
      oItem.Key = ritemSQL.TransactionItemId
      Amt += oItem.Amount
      oTran = oItem.LTransaction
      y,m,d = oTran.TransactionDate[:3]
      Date = '%s/%s/%s' % (d,m,y)
      ofile.write('%s|%s|%s|%s|%s|%s|%s|%s\n' % \
          (CenterText(Date,13),
          CenterText(oItem.BranchCode,11),
          CenterText(oTran.TransactionCode,14),
          CenterText(oTran.Description,10),
          CenterText(oTran.ReferenceNo,6),
          CenterText(oItem.CurrencyCode,11),
          CenterText(oItem.MutationType,6),
          CenterText(str(oItem.Amount),7))
      )
      ritemSQL.Next()
    LineFeed(ofile)
    ofile.write(RightText('Saldo : %d\n\n\n' % Amt))
    resSQL.Next()
  
  return ofile
  
def DAFScriptMain(config, parameter, returns):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  helper = phelper.PObjectHelper(config)
  
  fltr = parameter.FirstRecord
  
  rec = returns.AddNewDatasetEx('Value','ExF:string').AddRecord()
  sw = returns.AddStreamWrapper() 
  folder = config.GetHomeDir() + 'userhome/'
  filename = folder + config.SecurityContext.UserId + str(config.Now()) 
  ofile = file(filename, 'w')
  ParamValue = {
   'RekapDonasi':'CreateRekapDonasi(helper, fltr, ofile,returns)',
   'RekapTransKas':'CreateRekapTransKas(helper, fltr, ofile, returns)',
   'SENTINEL':'NULL'
  }
  ofile = eval(ParamValue[parameter.FirstRecord.mode])
  ofile.close()
  sw.LoadFromFile(ofile.name)
  sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(ofile.name)
  rec.ExF = '.txt'

  return 1
