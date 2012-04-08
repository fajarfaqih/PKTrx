insert into transaction.parameterglobal (kode_parameter, deskripsi, nilai_parameter)  
values('DEPR_DAY','Tanggal proses penyusutan tiap bulan',15);
insert into transaction.transactiontype values('DEPR','PENYUSUTAN ASET & BIAYA DIMUKA','GT',null);

alter table transaction.bpscenario alter column bpscenariocode type varchar(15);
insert into transaction.bpscenario values(3,'DEPRECIATION','Proses Depresiasi Aset dan Amortisasi Biaya');
insert into transaction.bpscenariostep values(4,1,1,3,'T');
update transaction.bpscript set bpscriptpath='BatchProcess/Depreciation' where bpscriptid = 1;
update transaction.bpscript set bpscriptpath='BatchProcess/CloseDay' where bpscriptid = 2;
update transaction.bpscript set bpscriptpath='BatchProcess/BackDate' where bpscriptid = 3;

