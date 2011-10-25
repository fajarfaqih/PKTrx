create table transaction.assetcategory (
  assetcategoryid integer,
  parentassetcategoryid integer,
  assetcategoryname varchar(50),
  assetcategorycode varchar(20),
  thresholdvalue double precision,
  defaultlifetime integer,
  inputer varchar(50),
  inputdate timestamp(6),
  inputtime timestamp(6),
  glicontainerid integer,
  constraint pk_assetcategory   primary key(assetcategoryid) 
);
alter table transaction.assetcategory owner to transaction;

create table transaction.glinterfacecontainer(
  glicontainerid integer,
  glicontainercode varchar(20),
  glicontainername varchar(50),
  constraint pk_glinterfacecontaider primary key (glicontainerid)
);
alter table transaction.glinterfacecontainer owner to transaction;

create table transaction.glinterfacemember(
  glimemberid integer,
  glimembercode varchar(20),
  accountcode varchar(20),
  accountname varchar(100),
  description varchar(100),  
  glicontainerid integer,
  constraint pk_glinterfacemember primary key (glimemberid)
);
alter table transaction.glinterfacemember owner to transaction;

create table transaction.inventorycategory(
  inventorycategoryid integer,
  parentinventorycategoryid integer,
  inventorycategorycode varchar(20),
  inventorycategoryname varchar(100),
  glicontainerid integer,
  constraint  pk_inventorycategory primary key (inventorycategoryid)  
);
alter table transaction.inventorycategory owner to transaction;

create table transaction.inventory(
  accountno varchar(30),
  nilaiawal double precision,
  nilaisisa double precision,
  qtysisa double precision,
  qtytotal double precision,
  inventorycategoryid integer,
  constraint pk_inventory primary key (accountno)
);
alter table transaction.inventory owner to transaction;

create table transaction.depreciableasset(
  accountno varchar(30),
  accountnoproduct varchar(30),
  depreciableassettype varchar(1),
  lifetime integer,
  nilaiawal double precision,
  nilaisisa double precision,
  penyusutanke integer,
  tanggalakhirpenyusutan timestamp(6),
  tanggalperolehan timestamp(6),
  tanggalprosesberikut timestamp(6),
  tanggalprosesterakhir timestamp(6),
  totalpenyusutan double precision,
  nominalpenyusutan  double precision,
  deprstate varchar(1),
  constraint pk_depreciableasset primary key (accountno)
);
alter table transaction.depreciableasset owner to transaction;

create table transaction.fixedasset(
  accountno varchar(30),
  totaldibayar double precision,
  qty integer,
  assetcategoryid integer,
  uangmuka double precision,
  constraint pk_fixedasset primary key (accountno)
);
alter table transaction.fixedasset owner to transaction;

create table transaction.amortizedcost(
  accountno varchar(30),
  amortizedcosttype varchar(1),
  description varchar(150),
  costaccountno varchar(30),
  constraint pk_amortizedcost primary key (accountno)
);
alter table transaction.amortizedcost owner to transaction;

create table transaction.costpaidinadvance(
  accountno varchar(30),
  hascontract varchar(1),
  contractbegindate timestamp(6),
  contractduration integer,
  contractenddate timestamp(6),
  contractno varchar(50),
  constraint pk_costpaidinadvance primary key (accountno)
);
alter table transaction.costpaidinadvance owner to transaction;

create table transaction.invoice(
  invoiceid integer,
  invoicedate timestamp(6),
  invoiceno varchar(30),
  invoicetype varchar(1),
  invoicepaymentstatus varchar(1),
  invoiceamount double precision,
  transactionid integer,
  paymenttransactionid integer,
  branchcode varchar(10),
  constraint pk_invoiceid primary key (invoiceid) 
);
alter table transaction.invoice owner to transaction;

create table transaction.fixedassettransactinfo(
  transactionitemid integer,
  accountno varchar(30),
  cashadvance double precision,
  sellamount double precision,  
  constraint pk_fixedassettransactinfo primary key (transactionitemid)
);
alter table transaction.fixedassettransactinfo owner to transaction;

create table transaction.invoicefa(
  invoiceid integer,
  accountno varchar(30),
  constraint pk_invoicefa primary key (invoiceid) 
); 
alter table transaction.invoicefa owner to transaction;

CREATE TABLE "transaction".invoiceproduct
(
  invoiceid integer NOT NULL,
  invoiceaddress character varying(250),
  invoicebankname character varying(100),
  invoicebankaccountname character varying(100),
  invoicebankaccountnumber character varying(30),
  invoiceofficername character varying(100),
  invoiceofficerposition character varying(100),
  invoicetermdate timestamp(6) without time zone,
  productaccountno character varying(30),
  sponsorid integer,
  CONSTRAINT invoice_pkey PRIMARY KEY (invoiceid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "transaction".invoiceproduct OWNER TO "transaction";

insert into transaction.transactiontype (TransactionCode,Description) values('FA','Pembelian Aktiva Tetap')

CREATE OR REPLACE VIEW "transaction".account AS 
 SELECT account.account_code, account.account_name, account.account_level,account.is_detail
   FROM accounting.account;

ALTER TABLE "transaction".account OWNER TO "transaction";

create sequence transaction.seq_deprassetid;
ALTER TABLE "transaction".seq_deprassetid OWNER TO "transaction";

insert into transaction.transactiontype values('INVP','INVOICE PAYMENT');
insert into transaction.transactiontype values('INVC','INVOICE CREATE');

create or view transaction.vdonor as select id,user_name,email,full_name,user_status,address,donor_no,npwp_no,npwz_no,
donor_type_id,marketer_id from public.php_donor

alter view transaction.vdonor owner to transaction;

INSERT INTO "transaction"."parameterglobal" VALUES ('GLIPROG13', null, null, 'Account Penerimaan Dana Termanfaatkan Dari Infaq', null, null, '4610201', 'GLI_PROGRAM', 'PHP_MANF_INFAQ');
INSERT INTO "transaction"."parameterglobal" VALUES ('GLIPROG14', null, null, 'Account Pengurang Dana Termanfaatkan Dari Infaq', null, null, '5610102', 'GLI_PROGRAM', 'PDG_MANF_INFAQ');
INSERT INTO "transaction"."parameterglobal" VALUES ('GLIPROJ13', null, null, 'Account Penerimaan Dana Termanfaatkan Dari Infaq', null, null, '4610201', 'GLI_PROJECT', 'PHP_MANF_INFAQ');
INSERT INTO "transaction"."parameterglobal" VALUES ('GLIPROJ14', null, null, 'Account Pengurang Dana Termanfaatkan Dari Infaq', null, null, '5610102', 'GLI_PROJECT', 'PDG_MANF_INFAQ');