-- Tambah field issendjournaldescription untuk status agar apakah deskripsi jurnal dikirimkan
alter table transaction.parameterjournalitem add issendjournaldescription varchar(1);
alter table accounting.journalitem add additionaldescription varchar(200);

update transaction.parameterjournalitem set issendjournaldescription = 'F';
