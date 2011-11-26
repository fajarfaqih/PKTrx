Create Table transaction.subsysteminteraction(
  subsysteminteraction_id integer primary key,
  titleinteraction varchar(50),
  subsystemcode varchar(50),
  parentssi_id integer,
  isactive varchar(1)
);

alter table transaction.subsysteminteraction owner to transaction;

insert into transaction.subsysteminteraction values(1,'Penghimpunan dana eksternal','EXTCOLL',null,'T');