drop table transaction.subsysteminteraction;
Create Table transaction.subsysteminteraction(
  subsystemcode varchar(20) primary key,
  titleinteraction varchar(50),
  parentssi_id integer,
  isactive varchar(1)
);

alter table transaction.subsysteminteraction owner to transaction;

insert into transaction.subsysteminteraction values('EXTCOLL','Penghimpunan dana eksternal',null,'T');

alter table transaction.transaction add subsystemcode varchar(20);
