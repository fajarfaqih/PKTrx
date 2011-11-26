-- View: accounting.userapp

-- DROP VIEW accounting.userapp;
drop table transaction.userapp ;
drop table transaction.usergroup ;
drop table transaction.usergroupapp ;
grant select on enterprise.userapp to transaction;
CREATE OR REPLACE VIEW transaction.userapp AS 
 SELECT userapp.id_user , userapp.nama_user , userapp.kode_cabang AS branch_code
   FROM enterprise.userapp;

ALTER view transaction.userapp OWNER TO transaction;

