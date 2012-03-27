select * from transaction.parameterjournalitem ji
where 
accountcode like '5%' and 
exists(
select 1 from transaction.parameterjournal where journalcode like 'AK%'
and parameterjournalid= ji.parameterjournalid)

-- Update parameter Jurnal Item Penambahan aset kelolaan
update transaction.parameterjournalitem set accountcode='5110102' where parameterjournalitemid in (137);
update transaction.parameterjournalitem set accountcode='5210202' where parameterjournalitemid in (139);
update transaction.parameterjournalitem set accountcode='5310102' where parameterjournalitemid in (143);
update transaction.parameterjournalitem set accountcode='5410102' where parameterjournalitemid in (193);

-- Update parameter Jurnal Item Pengembalian aset kelolaan
update transaction.parameterjournalitem set accountcode='4110103' where parameterjournalitemid in (149,161);
update transaction.parameterjournalitem set accountcode='4220103' where parameterjournalitemid in (152,165);
update transaction.parameterjournalitem set accountcode='4310103' where parameterjournalitemid in (155,169);
update transaction.parameterjournalitem set accountcode='4510702' where parameterjournalitemid in (158,203);
