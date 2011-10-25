-- DA01 PEMBELIAN AKTIVA
insert into transaction.parameterjournal
select 13, 'DA01', 'PEMBELIAN AKTIVA', 'SQL_21.sql';
commit;

insert into transaction.parameterjournalitem
select 25, null, 'A', 'AKTIVA TETAP', 'P', 'A', 'Amount', 'Rate', parameterjournalid, 'T'
from transaction.parameterjournal where journalcode = 'DA01';

insert into transaction.parameterjournalitem
select 26, '????', 'A', 'HUTANG YAD', 'N', 'A', 'ItemToTransactAmount', 'Rate', parameterjournalid, 'P'
from transaction.parameterjournal where journalcode = 'DA01';

insert into transaction.parameterjournalitem
select 27, 'PDG_INFAQ', 'A', 'PENGELUARAN PROYEK', 'P', 'A', 'TransactAmount', 'Rate', parameterjournalid, 'R'
from transaction.parameterjournal where journalcode = 'DA01';

insert into transaction.parameterjournalitem
select 28, '????', 'A', 'PENERIMAAN DANA TERMANFAATKAN', 'N', 'A', 'TransactAmount', 'Rate', parameterjournalid, 'P'
from transaction.parameterjournal where journalcode = 'DA01';
commit;

-- DA02 REGISTRASI BDD
insert into transaction.parameterjournal
select 14, 'DA02', 'REGISTRASI BDD', 'SQL_1.sql';
commit;

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), null, 'A', 'BDD', 'P', 'A', 'Amount', 'Rate', parameterjournalid, 'T'
from transaction.parameterjournal where journalcode = 'DA02';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), '????', 'A', 'DANA PENGELOLA', 'P', 'A', 'Amount', 'Rate', parameterjournalid, 'P'
from transaction.parameterjournal where journalcode = 'DA02';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), '????', 'A', 'DANA PENGELOLA TERMANFAATKAN', 'N', 'A', 'Amount', 'Rate', parameterjournalid, 'P'
from transaction.parameterjournal where journalcode = 'DA02';
commit;

-- DA03 BAYAR INVOICE 
insert into transaction.parameterjournal
select 15, 'DA03', 'BAYAR INVOICE PEMBELIAN AKTIVA', 'SQL_1.sql';
commit;

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), null, 'A', 'KAS/BANK', 'P', 'A', 'Amount', 'Rate', parameterjournalid, 'T'
from transaction.parameterjournal where journalcode = 'DA03';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), '????', 'A', 'HUTANG', 'N', 'A', 'Amount', 'Rate', parameterjournalid, 'P'
from transaction.parameterjournal where journalcode = 'DA03';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), 'PDG_INFAQ', 'A', 'PENGELUARAN PROYEK', 'N', 'A', 'Amount', 'Rate', parameterjournalid, 'R'
from transaction.parameterjournal where journalcode = 'DA03';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), '????', 'A', 'PENERIMAAN DANA TERMANFAATKAN', 'P', 'A', 'TransactAmount', 'Rate', parameterjournalid, 'P'
from transaction.parameterjournal where journalcode = 'DA03';
commit;

-- DA04 PENYUSUTAN AKTIVA TETAP 
insert into transaction.parameterjournal
select 16, 'DA04', 'PENYUSUTAN AKTIVA TETAP', 'SQL_21.sql';
commit;

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), null, 'A', 'PENYUSUTAN AKTIVA', 'P', 'A', 'Amount', 'Rate', parameterjournalid, 'T'
from transaction.parameterjournal where journalcode = 'DA04';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), 'COST_ACC', 'A', 'BIAYA SUSUT/PENYALURAN DANA MANFAAT', 'N', 'A', 'Amount', 'Rate', parameterjournalid, 'I'
from transaction.parameterjournal where journalcode = 'DA04';
commit;

-- DA05 PENYUSUTAN BDD
insert into transaction.parameterjournal
select 17, 'DA05', 'AMORTISASI BDD', 'SQL_22.sql';
commit;

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), null, 'A', 'BDD', 'P', 'A', 'Amount', 'Rate', parameterjournalid, 'T'
from transaction.parameterjournal where journalcode = 'DA05';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), 'CostAccountNo', 'A', 'BIAYA SUSUT/PENYALURAN DANA MANFAAT', 'N', 'A', 'Amount', 'Rate', parameterjournalid, 'P'
from transaction.parameterjournal where journalcode = 'DA05';
commit;

-- DA06 PENJUALAN AKTIVA UNTUNG
insert into transaction.parameterjournal
select 18, 'DA06', 'PENJUALAN AKTIVA UNTUNG', 'SQL_21.sql';
commit;

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), null, 'A', 'AKTIVA TETAP', 'P', 'A', 'NilaiAwal', 'Rate', parameterjournalid, 'T'
from transaction.parameterjournal where journalcode = 'DA06';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), 'DEPR_ACC', 'A', 'AKUMULASI PENYUSUTAN', 'N', 'A', 'TotalPenyusutan', 'Rate', parameterjournalid, 'I'
from transaction.parameterjournal where journalcode = 'DA06';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), 'LOST_ACC', 'A', 'BEBAN RUGI PENJUALAN', 'N', 'A', 'ItemToTransactAmount', 'Rate', parameterjournalid, 'I'
from transaction.parameterjournal where journalcode = 'DA06';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), 'PDG_INFAQ', 'A', 'PENGELUARAN PROYEK', 'P', 'A', 'TransactAmount', 'Rate', parameterjournalid, 'R'
from transaction.parameterjournal where journalcode = 'DA06';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), '????', 'A', 'PENERIMAAN DANA TERMANFAATKAN', 'N', 'A', 'TransactAmount', 'Rate', parameterjournalid, 'P'
from transaction.parameterjournal where journalcode = 'DA06';
commit;

-- DA07 PENJUALAN AKTIVA RUGI
insert into transaction.parameterjournal
select 19, 'DA07', 'PENJUALAN AKTIVA UNTUNG', 'SQL_21.sql';
commit;

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), null, 'A', 'AKTIVA TETAP', 'P', 'A', 'NilaiAwal', 'Rate', parameterjournalid, 'T'
from transaction.parameterjournal where journalcode = 'DA07';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), 'DEPR_ACC', 'A', 'AKUMULASI PENYUSUTAN', 'N', 'A', 'TotalPenyusutan', 'Rate', parameterjournalid, 'I'
from transaction.parameterjournal where journalcode = 'DA07';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), 'PROFIT_ACC', 'A', 'PENDAPATAN PENJUALAN ASSET', 'P', 'A', 'TransactToItemAmount', 'Rate', parameterjournalid, 'I'
from transaction.parameterjournal where journalcode = 'DA07';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), 'PDG_INFAQ', 'A', 'PENGELUARAN PROYEK', 'P', 'A', 'TransactAmount', 'Rate', parameterjournalid, 'R'
from transaction.parameterjournal where journalcode = 'DA07';

insert into transaction.parameterjournalitem
select nextval('transaction.seq_parameterjournalitem'), '????', 'A', 'PENERIMAAN DANA TERMANFAATKAN', 'N', 'A', 'TransactAmount', 'Rate', parameterjournalid, 'P'
from transaction.parameterjournal where journalcode = 'DA07';
commit;
