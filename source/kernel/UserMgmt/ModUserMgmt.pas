unit ModUserMgmt;

interface

uses PObjConst, KernelIntf, XVariant, PClasses, SysUtils, Classes,
  PClassIntf;

type

  (* PCLASS: BRANCHLOCATION *)

  TP_BranchLocation = class(TPObjImpl, IP_BranchLocation, IPObjImpl, IUnknown)
  protected
    function GetPClassImpl: IPClassImpl; override;
    procedure SetNewInstanceKey; override;
    procedure InitializeMethodList; override;
  public
    function _Destructor(var Msg: string): boolean; override;
  public
    procedure RegisterData(LMasterBranch: IP_BranchLocation);
    procedure SetMasterBranch(LMasterBranch: IP_BranchLocation);
    procedure ChangeMasterBranch(NewMasterBranch: IP_BranchLocation);
    procedure Modify(NewMasterBranch: IP_BranchLocation);
    procedure DeleteData();
    procedure SendAddRequest(branch_code: string; BranchName: string);
    procedure SendModifyRequest(branch_code: string; BranchName: string);
    procedure SendDeleteRequest(branch_code: string);

    // CANONCIAL METHODS
    procedure _RegisterData(Parameters: IPMethodCallParams);
    procedure _SetMasterBranch(Parameters: IPMethodCallParams);
    procedure _ChangeMasterBranch(Parameters: IPMethodCallParams);
    procedure _Modify(Parameters: IPMethodCallParams);
    procedure _DeleteData(Parameters: IPMethodCallParams);
    procedure _SendAddRequest(Parameters: IPMethodCallParams);
    procedure _SendModifyRequest(Parameters: IPMethodCallParams);
    procedure _SendDeleteRequest(Parameters: IPMethodCallParams);
    // CANONCIAL - ANCESTOR DISPATCHER METHODS
  end;

  TPCls_BranchLocation = class(TPClassImpl, IPClassImpl, IUnknown)
    function CreateInstance(ATransCtl: IPObjTransCtl): IPObjImpl; override;
  end;

  (* PCLASS: USERAPP *)

  TP_UserApp = class(TPObjImpl, IP_UserApp, IPObjImpl, IUnknown)
  protected
    function GetPClassImpl: IPClassImpl; override;
    procedure SetNewInstanceKey; override;
    procedure InitializeMethodList; override;
  public
    function _Destructor(var Msg: string): boolean; override;
  public
    procedure SendAddRequest(AUser_ID: string; AUserName: string; Adesc: string
      ; ADepartmentID: string; APasswd: string);
    procedure SendModifyRequest(AUser_ID: string; AUserName: string
      ; Adesc: string; ADepartmentID: string);
    procedure SendDeleteRequest(AUser_ID: string);
    procedure SendChangePasswordRequest(AUser_ID: string; ANewPassword: string
      ; AConfirmPassword: string);
    procedure RegisterData();
    procedure Modify();
    procedure ChangePassword(ANewPassword: string);
    procedure Validate();
    procedure LogActivity(Description: string);
    function IsLocked(): IE_FTBoolean;
    procedure IncCounter();
    procedure ResetCounter();
    procedure LockLogin();
    procedure UnLockLogin();

    // CANONCIAL METHODS
    procedure _SendAddRequest(Parameters: IPMethodCallParams);
    procedure _SendModifyRequest(Parameters: IPMethodCallParams);
    procedure _SendDeleteRequest(Parameters: IPMethodCallParams);
    procedure _SendChangePasswordRequest(Parameters: IPMethodCallParams);
    procedure _RegisterData(Parameters: IPMethodCallParams);
    procedure _Modify(Parameters: IPMethodCallParams);
    procedure _ChangePassword(Parameters: IPMethodCallParams);
    procedure _Validate(Parameters: IPMethodCallParams);
    procedure _LogActivity(Parameters: IPMethodCallParams);
    procedure _IsLocked(Parameters: IPMethodCallParams);
    procedure _IncCounter(Parameters: IPMethodCallParams);
    procedure _ResetCounter(Parameters: IPMethodCallParams);
    procedure _LockLogin(Parameters: IPMethodCallParams);
    procedure _UnLockLogin(Parameters: IPMethodCallParams);
    // CANONCIAL - ANCESTOR DISPATCHER METHODS
  end;

  TPCls_UserApp = class(TPClassImpl, IPClassImpl, IUnknown)
    function CreateInstance(ATransCtl: IPObjTransCtl): IPObjImpl; override;
  end;

  (* PCLASS: USERGROUP *)

  TP_UserGroup = class(TPObjImpl, IP_UserGroup, IPObjImpl, IUnknown)
  protected
    function GetPClassImpl: IPClassImpl; override;
    procedure SetNewInstanceKey; override;
    procedure InitializeMethodList; override;
  public
    function _Destructor(var Msg: string): boolean; override;
  public
    procedure SendAddRequest(AGroup_ID: string; AGroupName: string
      ; ADesc: string);
    procedure SendModifyRequest(AGroup_ID: string; AGroupName: string
      ; ADesc: string);
    procedure SendDeleteRequest(AGroup_ID: string);
    procedure SendAddUserToGroup(AGroup_ID: string; User_ID: string);
    procedure SendDeleteUserFromGroup(AGroup_ID: string; User_ID: string);
    procedure RegisterData();
    procedure Modify();
    procedure AddUser(UserID: string);
    procedure DeleteUser(UserID: string);

    // CANONCIAL METHODS
    procedure _SendAddRequest(Parameters: IPMethodCallParams);
    procedure _SendModifyRequest(Parameters: IPMethodCallParams);
    procedure _SendDeleteRequest(Parameters: IPMethodCallParams);
    procedure _SendAddUserToGroup(Parameters: IPMethodCallParams);
    procedure _SendDeleteUserFromGroup(Parameters: IPMethodCallParams);
    procedure _RegisterData(Parameters: IPMethodCallParams);
    procedure _Modify(Parameters: IPMethodCallParams);
    procedure _AddUser(Parameters: IPMethodCallParams);
    procedure _DeleteUser(Parameters: IPMethodCallParams);
    // CANONCIAL - ANCESTOR DISPATCHER METHODS
  end;

  TPCls_UserGroup = class(TPClassImpl, IPClassImpl, IUnknown)
    function CreateInstance(ATransCtl: IPObjTransCtl): IPObjImpl; override;
  end;

  (* PCLASS: USERGROUPAPP *)

  TP_UserGroupApp = class(TPObjImpl, IP_UserGroupApp, IPObjImpl, IUnknown)
  protected
    function GetPClassImpl: IPClassImpl; override;
    procedure SetNewInstanceKey; override;
    procedure InitializeMethodList; override;
  public
    function _Destructor(var Msg: string): boolean; override;
  public
    procedure Create(LUser: IP_UserApp; LUserGroup: IP_UserGroup);

    // CANONCIAL METHODS
    procedure _Create(Parameters: IPMethodCallParams);
    // CANONCIAL - ANCESTOR DISPATCHER METHODS
  end;

  TPCls_UserGroupApp = class(TPClassImpl, IPClassImpl, IUnknown)
    function CreateInstance(ATransCtl: IPObjTransCtl): IPObjImpl; override;
  end;

implementation

uses PModClsDecl, Utils2, SecurityUpdate, FileCtrl;

(* -------------------------------------------------------------------------- *)
(* -------------------------------------------------------------------------- *)
(* *****************     CLASS TYPES IMPLEMENTATION        ********************)
(* -------------------------------------------------------------------------- *)
(* -------------------------------------------------------------------------- *)

(* BranchLocation class type *)

function TPCls_BranchLocation.CreateInstance(ATransCtl: IPObjTransCtl): IPObjImpl;
begin
  Result := TP_BranchLocation.CreateInstance(ATransCtl);
end;

(* BranchLocation class - canoncial methods *)

function TP_BranchLocation.GetPClassImpl: IPClassImpl;
begin
  Result := PCls_BranchLocation;
end;

procedure TP_BranchLocation.InitializeMethodList;
begin
  Self.AddMethod(Self._RegisterData);
  Self.AddMethod(Self._SetMasterBranch);
  Self.AddMethod(Self._ChangeMasterBranch);
  Self.AddMethod(Self._Modify);
  Self.AddMethod(Self._DeleteData);
  Self.AddMethod(Self._SendAddRequest);
  Self.AddMethod(Self._SendModifyRequest);
  Self.AddMethod(Self._SendDeleteRequest);
end;

procedure TP_BranchLocation._RegisterData(Parameters: IPMethodCallParams);
  var
    LMasterBranch: IP_BranchLocation;
begin
  LMasterBranch := IP_BranchLocation(Parameters['LMasterBranch'].AsPObj);
  RegisterData(LMasterBranch);
end;

procedure TP_BranchLocation._SetMasterBranch(Parameters: IPMethodCallParams);
  var
    LMasterBranch: IP_BranchLocation;
begin
  LMasterBranch := IP_BranchLocation(Parameters['LMasterBranch'].AsPObj);
  SetMasterBranch(LMasterBranch);
end;

procedure TP_BranchLocation._ChangeMasterBranch(Parameters: IPMethodCallParams);
  var
    NewMasterBranch: IP_BranchLocation;
begin
  NewMasterBranch := IP_BranchLocation(Parameters['NewMasterBranch'].AsPObj);
  ChangeMasterBranch(NewMasterBranch);
end;

procedure TP_BranchLocation._Modify(Parameters: IPMethodCallParams);
  var
    NewMasterBranch: IP_BranchLocation;
begin
  NewMasterBranch := IP_BranchLocation(Parameters['NewMasterBranch'].AsPObj);
  Modify(NewMasterBranch);
end;

procedure TP_BranchLocation._DeleteData(Parameters: IPMethodCallParams);
begin
  DeleteData();
end;

procedure TP_BranchLocation._SendAddRequest(Parameters: IPMethodCallParams);
  var
    branch_code: string;
    BranchName: string;
begin
  branch_code := Parameters['branch_code'].AsString;
  BranchName := Parameters['BranchName'].AsString;
  SendAddRequest(branch_code, BranchName);
end;

procedure TP_BranchLocation._SendModifyRequest(Parameters: IPMethodCallParams);
  var
    branch_code: string;
    BranchName: string;
begin
  branch_code := Parameters['branch_code'].AsString;
  BranchName := Parameters['BranchName'].AsString;
  SendModifyRequest(branch_code, BranchName);
end;

procedure TP_BranchLocation._SendDeleteRequest(Parameters: IPMethodCallParams);
  var
    branch_code: string;
begin
  branch_code := Parameters['branch_code'].AsString;
  SendDeleteRequest(branch_code);
end;

(* UserApp class type *)

function TPCls_UserApp.CreateInstance(ATransCtl: IPObjTransCtl): IPObjImpl;
begin
  Result := TP_UserApp.CreateInstance(ATransCtl);
end;

(* UserApp class - canoncial methods *)

function TP_UserApp.GetPClassImpl: IPClassImpl;
begin
  Result := PCls_UserApp;
end;

procedure TP_UserApp.InitializeMethodList;
begin
  Self.AddMethod(Self._SendAddRequest);
  Self.AddMethod(Self._SendModifyRequest);
  Self.AddMethod(Self._SendDeleteRequest);
  Self.AddMethod(Self._SendChangePasswordRequest);
  Self.AddMethod(Self._RegisterData);
  Self.AddMethod(Self._Modify);
  Self.AddMethod(Self._ChangePassword);
  Self.AddMethod(Self._Validate);
  Self.AddMethod(Self._LogActivity);
  Self.AddMethod(Self._IsLocked);
  Self.AddMethod(Self._IncCounter);
  Self.AddMethod(Self._ResetCounter);
  Self.AddMethod(Self._LockLogin);
  Self.AddMethod(Self._UnLockLogin);
end;

procedure TP_UserApp._SendAddRequest(Parameters: IPMethodCallParams);
  var
    AUser_ID: string;
    AUserName: string;
    Adesc: string;
    ADepartmentID: string;
    APasswd: string;
begin
  AUser_ID := Parameters['AUser_ID'].AsString;
  AUserName := Parameters['AUserName'].AsString;
  Adesc := Parameters['Adesc'].AsString;
  ADepartmentID := Parameters['ADepartmentID'].AsString;
  APasswd := Parameters['APasswd'].AsString;
  SendAddRequest(AUser_ID, AUserName, Adesc, ADepartmentID, 
    APasswd);
end;

procedure TP_UserApp._SendModifyRequest(Parameters: IPMethodCallParams);
  var
    AUser_ID: string;
    AUserName: string;
    Adesc: string;
    ADepartmentID: string;
begin
  AUser_ID := Parameters['AUser_ID'].AsString;
  AUserName := Parameters['AUserName'].AsString;
  Adesc := Parameters['Adesc'].AsString;
  ADepartmentID := Parameters['ADepartmentID'].AsString;
  SendModifyRequest(AUser_ID, AUserName, Adesc, ADepartmentID);
end;

procedure TP_UserApp._SendDeleteRequest(Parameters: IPMethodCallParams);
  var
    AUser_ID: string;
begin
  AUser_ID := Parameters['AUser_ID'].AsString;
  SendDeleteRequest(AUser_ID);
end;

procedure TP_UserApp._SendChangePasswordRequest(Parameters: IPMethodCallParams);
  var
    AUser_ID: string;
    ANewPassword: string;
    AConfirmPassword: string;
begin
  AUser_ID := Parameters['AUser_ID'].AsString;
  ANewPassword := Parameters['ANewPassword'].AsString;
  AConfirmPassword := Parameters['AConfirmPassword'].AsString;
  SendChangePasswordRequest(AUser_ID, ANewPassword, AConfirmPassword);
end;

procedure TP_UserApp._RegisterData(Parameters: IPMethodCallParams);
begin
  RegisterData();
end;

procedure TP_UserApp._Modify(Parameters: IPMethodCallParams);
begin
  Modify();
end;

procedure TP_UserApp._ChangePassword(Parameters: IPMethodCallParams);
  var
    ANewPassword: string;
begin
  ANewPassword := Parameters['ANewPassword'].AsString;
  ChangePassword(ANewPassword);
end;

procedure TP_UserApp._Validate(Parameters: IPMethodCallParams);
begin
  Validate();
end;

procedure TP_UserApp._LogActivity(Parameters: IPMethodCallParams);
  var
    Description: string;
begin
  Description := Parameters['Description'].AsString;
  LogActivity(Description);
end;

procedure TP_UserApp._IsLocked(Parameters: IPMethodCallParams);
  var
    return_value: IE_FTBoolean;
begin
  return_value := IsLocked();
  Parameters.ReturnValue.AsXEnum := return_value;
end;

procedure TP_UserApp._IncCounter(Parameters: IPMethodCallParams);
begin
  IncCounter();
end;

procedure TP_UserApp._ResetCounter(Parameters: IPMethodCallParams);
begin
  ResetCounter();
end;

procedure TP_UserApp._LockLogin(Parameters: IPMethodCallParams);
begin
  LockLogin();
end;

procedure TP_UserApp._UnLockLogin(Parameters: IPMethodCallParams);
begin
  UnLockLogin();
end;

(* UserGroup class type *)

function TPCls_UserGroup.CreateInstance(ATransCtl: IPObjTransCtl): IPObjImpl;
begin
  Result := TP_UserGroup.CreateInstance(ATransCtl);
end;

(* UserGroup class - canoncial methods *)

function TP_UserGroup.GetPClassImpl: IPClassImpl;
begin
  Result := PCls_UserGroup;
end;

procedure TP_UserGroup.InitializeMethodList;
begin
  Self.AddMethod(Self._SendAddRequest);
  Self.AddMethod(Self._SendModifyRequest);
  Self.AddMethod(Self._SendDeleteRequest);
  Self.AddMethod(Self._SendAddUserToGroup);
  Self.AddMethod(Self._SendDeleteUserFromGroup);
  Self.AddMethod(Self._RegisterData);
  Self.AddMethod(Self._Modify);
  Self.AddMethod(Self._AddUser);
  Self.AddMethod(Self._DeleteUser);
end;

procedure TP_UserGroup._SendAddRequest(Parameters: IPMethodCallParams);
  var
    AGroup_ID: string;
    AGroupName: string;
    ADesc: string;
begin
  AGroup_ID := Parameters['AGroup_ID'].AsString;
  AGroupName := Parameters['AGroupName'].AsString;
  ADesc := Parameters['ADesc'].AsString;
  SendAddRequest(AGroup_ID, AGroupName, ADesc);
end;

procedure TP_UserGroup._SendModifyRequest(Parameters: IPMethodCallParams);
  var
    AGroup_ID: string;
    AGroupName: string;
    ADesc: string;
begin
  AGroup_ID := Parameters['AGroup_ID'].AsString;
  AGroupName := Parameters['AGroupName'].AsString;
  ADesc := Parameters['ADesc'].AsString;
  SendModifyRequest(AGroup_ID, AGroupName, ADesc);
end;

procedure TP_UserGroup._SendDeleteRequest(Parameters: IPMethodCallParams);
  var
    AGroup_ID: string;
begin
  AGroup_ID := Parameters['AGroup_ID'].AsString;
  SendDeleteRequest(AGroup_ID);
end;

procedure TP_UserGroup._SendAddUserToGroup(Parameters: IPMethodCallParams);
  var
    AGroup_ID: string;
    User_ID: string;
begin
  AGroup_ID := Parameters['AGroup_ID'].AsString;
  User_ID := Parameters['User_ID'].AsString;
  SendAddUserToGroup(AGroup_ID, User_ID);
end;

procedure TP_UserGroup._SendDeleteUserFromGroup(Parameters: IPMethodCallParams);
  var
    AGroup_ID: string;
    User_ID: string;
begin
  AGroup_ID := Parameters['AGroup_ID'].AsString;
  User_ID := Parameters['User_ID'].AsString;
  SendDeleteUserFromGroup(AGroup_ID, User_ID);
end;

procedure TP_UserGroup._RegisterData(Parameters: IPMethodCallParams);
begin
  RegisterData();
end;

procedure TP_UserGroup._Modify(Parameters: IPMethodCallParams);
begin
  Modify();
end;

procedure TP_UserGroup._AddUser(Parameters: IPMethodCallParams);
  var
    UserID: string;
begin
  UserID := Parameters['UserID'].AsString;
  AddUser(UserID);
end;

procedure TP_UserGroup._DeleteUser(Parameters: IPMethodCallParams);
  var
    UserID: string;
begin
  UserID := Parameters['UserID'].AsString;
  DeleteUser(UserID);
end;

(* UserGroupApp class type *)

function TPCls_UserGroupApp.CreateInstance(ATransCtl: IPObjTransCtl): IPObjImpl;
begin
  Result := TP_UserGroupApp.CreateInstance(ATransCtl);
end;

(* UserGroupApp class - canoncial methods *)

function TP_UserGroupApp.GetPClassImpl: IPClassImpl;
begin
  Result := PCls_UserGroupApp;
end;

procedure TP_UserGroupApp.InitializeMethodList;
begin
  Self.AddMethod(Self._Create);
end;

procedure TP_UserGroupApp._Create(Parameters: IPMethodCallParams);
  var
    LUser: IP_UserApp;
    LUserGroup: IP_UserGroup;
begin
  LUser := IP_UserApp(Parameters['LUser'].AsPObj);
  LUserGroup := IP_UserGroup(Parameters['LUserGroup'].AsPObj);
  Create(LUser, LUserGroup);
end;

(* -------------------------------------------------------------------------- *)
(* -------------------------------------------------------------------------- *)
(* *****************    PERSISTENT OBJECT IMPLEMENTATION   ********************)
(* -------------------------------------------------------------------------- *)
(* -------------------------------------------------------------------------- *)

(* BranchLocation class *)

procedure TP_BranchLocation.SetNewInstanceKey;
begin
  (* Insert code to set primary key here. If inherited action is used,  auto *)
  (* primary key is automatically set from IDGen Server                      *)
  inherited SetNewInstanceKey;
end;

function TP_BranchLocation._Destructor(var Msg: string): boolean;
begin
  (* Insert before deletion actions here. Remove the inherited part below if *)
  (* no referential integrity check / actions is required                    *)
  DeleteData;
  
  Result := inherited _Destructor(Msg);
end;

procedure TP_BranchLocation.RegisterData(LMasterBranch: IP_BranchLocation);
begin
  if Self['BranchStatus'] = eBranchStatus_Sub_branch then
    SetMasterBranch(LMasterBranch)
  else
    Links['LMasterBranch'] := nil;

  SendAddRequest(Self['branch_code'], Self['BranchName']);
end;

procedure TP_BranchLocation.SetMasterBranch(LMasterBranch: IP_BranchLocation);
begin
  if LMasterBranch.IsNull then
    raise Exception.Create('Cabang induk kosong');

  Links['LMasterBranch'] := LMasterBranch;
end;

procedure TP_BranchLocation.ChangeMasterBranch(
  NewMasterBranch: IP_BranchLocation);
//var
//  MasterBranch: IP_BranchLocation;
//  MasterDetail: IP_MasterDetailBranch;
begin
(*  MasterBranch := IP_BranchLocation(Links['LMasterBranch']);
  if not MasterBranch.IsNull then
  begin
    MasterDetail := IP_MasterDetailBranch(Config.CreatePObjImpl('MasterDetailBranch', TransCtl));
    MasterDetail.Keys['masterbranch_code'] := MasterBranch['branch_code'];
    MasterDetail.Keys['detailbranch_code'] := Self['branch_code'];

    MasterDetail.Delete;
  end;

  SetMasterBranch(NewMasterBranch);*)
end;

procedure TP_BranchLocation.Modify(NewMasterBranch: IP_BranchLocation);
begin
  if Self['BranchStatus'] = eBranchStatus_Sub_branch then
    SetMasterBranch(NewMasterBranch)
  else
    Links['LMasterBranch'] := nil;

  //ChangeMasterBranch(NewMasterBranch);

  SendModifyRequest(Self['branch_code'], Self['BranchName']);
end;

procedure TP_BranchLocation.DeleteData();
begin
  //Lists['Ls_MasterDetailBranch'].DeleteAllPObjs;

  SendDeleteRequest(Self['branch_code']);
end;

procedure TP_BranchLocation.SendAddRequest(branch_code: string
  ; BranchName: string);
var
  SecUpdate: ISecurityUpdate;
  SecContext: ISecurityContext;
  SessInfo: PSessionInfo;
  SessionID: string;
  IPAddr: integer;
begin
  SecContext := Config.SecurityContext;
  SecUpdate := Config.SecurityContext as ISecurityUpdate;
  SessionID := SecContext.GetSessionID;
  SecContext.GetSessionInfo(SessInfo);
  IPAddr := SessInfo^.ip_address;

  if not SecUpdate.AddDepartment(SessionID, branch_code, BranchName, IPAddr) then
    raise Exception.Create('Update error: ' + SecContext.GetLastErrorInfo);
end;

procedure TP_BranchLocation.SendModifyRequest(branch_code: string
  ; BranchName: string);
var
  SecUpdate: ISecurityUpdate;
  SecContext: ISecurityContext;
  SessInfo: PSessionInfo;
  SessionID: string;
  IPAddr: integer;
begin
  SecContext := Config.SecurityContext;
  SecUpdate := Config.SecurityContext as ISecurityUpdate;
  SessionID := SecContext.GetSessionID;
  SecContext.GetSessionInfo(SessInfo);
  IPAddr := SessInfo^.ip_address;

  if not SecUpdate.ModifyDepartment(SessionID, branch_code, BranchName, IPAddr) then
    raise Exception.Create('Update error: ' + SecContext.GetLastErrorInfo);
end;

procedure TP_BranchLocation.SendDeleteRequest(branch_code: string);
var
  SecUpdate: ISecurityUpdate;
  SecContext: ISecurityContext;
  SessInfo: PSessionInfo;
  SessionID: string;
  IPAddr: integer;
begin
  SecContext := Config.SecurityContext;
  SecUpdate := Config.SecurityContext as ISecurityUpdate;
  SessionID := SecContext.GetSessionID;
  SecContext.GetSessionInfo(SessInfo);
  IPAddr := SessInfo^.ip_address;

  if not SecUpdate.DeleteDepartment(SessionID, branch_code, IPAddr) then
    raise Exception.Create('Update error: ' + SecContext.GetLastErrorInfo);
end;

(* UserApp class *)

procedure TP_UserApp.SetNewInstanceKey;
begin
  (* Insert code to set primary key here. If inherited action is used,  auto *)
  (* primary key is automatically set from IDGen Server                      *)
  inherited SetNewInstanceKey;
end;

function TP_UserApp._Destructor(var Msg: string): boolean;
var
  Dir: string;
begin
  (* Insert before deletion actions here. Remove the inherited part below if *)
  (* no referential integrity check / actions is required                    *)
  Lists['Ls_UserGroupApp'].DeleteAllPObjs;
  SendDeleteRequest(Self['user_id']);

  Dir := IncludeTrailingBackslash(Config.GetGlobalSetting('USERHOMEDIR_ROOT')) + Self['user_id'];
  if DirectoryExists(Dir) then Utils2.ForceDeleteDirectory(Dir);

  Result := inherited _Destructor(Msg);
end;

procedure TP_UserApp.SendAddRequest(AUser_ID: string; AUserName: string
  ; Adesc: string; ADepartmentID: string; APasswd: string);
var
  SecUpdate: ISecurityUpdate;
  SecContext: ISecurityContext;
  SessInfo: PSessionInfo;
  SessionID: string;
  IPAddr: integer;
begin
  SecContext := Config.SecurityContext;
  SecUpdate := SecContext as ISecurityUpdate;
  SessionID := SecContext.GetSessionID;
  SecContext.GetSessionInfo(SessInfo);
  IPAddr := SessInfo^.ip_address;

  if not SecUpdate.AddUser(SessionID, AUser_ID, AUserName, Adesc, ADepartmentID, APasswd, APasswd, IPAddr) then
    raise Exception.Create('Update error: ' + SecContext.GetLastErrorInfo);
end;

procedure TP_UserApp.SendModifyRequest(AUser_ID: string; AUserName: string
  ; Adesc: string; ADepartmentID: string);
var
  SecUpdate: ISecurityUpdate;
  SecContext: ISecurityContext;
  SessInfo: PSessionInfo;
  SessionID: string;
  IPAddr: integer;
begin
  SecContext := Config.SecurityContext;
  SecUpdate := Config.SecurityContext as ISecurityUpdate;
  SessionID := SecContext.GetSessionID;
  SecContext.GetSessionInfo(SessInfo);
  IPAddr := SessInfo^.ip_address;

  if not SecUpdate.ModifyUser(SessionID, AUser_ID, AUserName, Adesc, ADepartmentId, IPAddr) then
    raise Exception.Create('Update error: ' + SecContext.GetLastErrorInfo);
end;

procedure TP_UserApp.SendDeleteRequest(AUser_ID: string);
var
  SecUpdate: ISecurityUpdate;
  SecContext: ISecurityContext;
  SessInfo: PSessionInfo;
  SessionID: string;
  IPAddr: integer;
begin
  SecContext := Config.SecurityContext;
  SecUpdate := Config.SecurityContext as ISecurityUpdate;
  SessionID := SecContext.GetSessionID;
  SecContext.GetSessionInfo(SessInfo);
  IPAddr := SessInfo^.ip_address;

  if not SecUpdate.DeleteUser(SessionID, AUser_ID, IPAddr) then
    raise Exception.Create('Update error: ' + SecContext.GetLastErrorInfo);
end;

procedure TP_UserApp.SendChangePasswordRequest(AUser_ID: string
  ; ANewPassword: string; AConfirmPassword: string);
var
  SecUpdate: ISecurityUpdate;
  SecContext: ISecurityContext;
  SessInfo: PSessionInfo;
  SessionID: string;
  IPAddr: integer;
begin
  SecContext := Config.SecurityContext;
  SecUpdate := Config.SecurityContext as ISecurityUpdate;
  SessionID := SecContext.GetSessionID;
  SecContext.GetSessionInfo(SessInfo);
  IPAddr := SessInfo^.ip_address;

  if not SecUpdate.ChangeUserPassword(SessionID, AUser_ID, ANewPassword,
    AConfirmPassword, IPAddr) then
    raise Exception.Create('Update error: ' + SecContext.GetLastErrorInfo);
end;

procedure TP_UserApp.RegisterData();
var
  Dir: string;
  defpasswd: string;
begin
  defpasswd := Config.GetSysVarIntf.GetStringSysVar('AUTHORITY', 'DEFPASSWD');
  SendAddRequest(Self['user_id'], Self['UserName'], Self['Description'],
    Links['LBranchLocation']['branch_code'], defpasswd);

  Dir := IncludeTrailingBackslash(Config.GetGlobalSetting('USERHOMEDIR_ROOT')) + Self['user_id'];
  if not DirectoryExists(Dir) then
    if not CreateDir(Dir) then
    raise Exception.Create('Cannot create ' + Dir);
end;

procedure TP_UserApp.Modify();
begin
  SendModifyRequest(Self['user_id'], Self['UserName'], Self['Description'],
    Links['LBranchLocation']['branch_code']);
end;

procedure TP_UserApp.ChangePassword(ANewPassword: string);
begin
  SendChangePasswordRequest(Self['user_id'], ANewPassword, ANewPassword);
end;

procedure TP_UserApp.Validate();
var
  OQLText: string;
  AOQL: IOQL;
  Branch: IP_BranchLocation;
  Group: IP_UserGroup;
  User: IP_UserApp;
  Passwd: string;
  user_id: string;
  root_dir, user_dir: string;

  SecUpdate: ISecurityUpdate;
  SecContext: ISecurityContext;
  SessInfo: PSessionInfo;
  SessionID: string;
  IPAddr: integer;
begin
  SecContext := Config.SecurityContext;
  SecUpdate := SecContext as ISecurityUpdate;
  SessionID := SecContext.GetSessionID;
  SecContext.GetSessionInfo(SessInfo);
  IPAddr := SessInfo^.ip_address;

  if not SecUpdate.ResetData(SessionID, IPAddr) then
    raise Exception.Create('Update error: ' + SecContext.GetLastErrorInfo);

  // VALIDASI CABANG
  OQLText := 'SELECT FROM BranchLocation (branch_code, BranchName, self);';
  AOQL := TransCtl.CreateOQL(OQLText);
  AOQL.Active := true;

  Branch := IP_BranchLocation(Config.CreatePObjImpl('BranchLocation', TransCtl));
  while not AOQL.Result.RQ_IsEof do
  begin
    Branch.SendAddRequest(VarToStr(AOQL.ColumnValue['branch_code']),
      VarToStr(AOQL.ColumnValue['BranchName']));

    AOQL.Result.RQ_Next;
  end;

  AOQL := nil;
  root_dir := IncludeTrailingBackslash(Config.GetGlobalSetting('USERHOMEDIR_ROOT'));
  
  // VALIDASI USER APP
  OQLText := 'SELECT FROM UserApp (user_id, UserName, Description, branch_code, self);';
  AOQL := TransCtl.CreateOQL(OQLText);
  AOQL.Active := true;

  User := IP_UserApp(Config.CreatePObjImpl('UserApp', TransCtl));
  Passwd := Config.GetSysVarIntf.GetStringSysVar('AUTHORITY', 'DEFPASSWD');
  while not AOQL.Result.RQ_IsEof do
  begin
    user_id := VarToStr(AOQL.ColumnValue['user_id']);
    User.SendAddRequest(user_id,
      VarToStr(AOQL.ColumnValue['UserName']),
      VarToStr(AOQL.ColumnValue['Description']),
      VarToStr(AOQL.ColumnValue['branch_code']),
      Passwd);

    user_dir := root_dir + user_id;
    if not DirectoryExists(user_dir) then
    begin
      CreateDir(user_dir);
    end;

    AOQL.Result.RQ_Next;
  end;

  AOQL := nil;
  // VALIDASI GROUP
  OQLText := 'SELECT FROM UserGroup (group_id, GroupName, Description, self);';
  AOQL := TransCtl.CreateOQL(OQLText);
  AOQL.Active := true;

  Group := IP_UserGroup(Config.CreatePObjImpl('UserGroup', TransCtl));
  while not AOQL.Result.RQ_IsEof do
  begin
    Group.SendAddRequest(VarToStr(AOQL.ColumnValue['group_id']),
      VarToStr(AOQL.ColumnValue['GroupName']),
      VarToStr(AOQL.ColumnValue['Description']));

    AOQL.Result.RQ_Next;
  end;

  AOQL := nil;
  // VALIDASI USER GROUP APP
  OQLText := 'SELECT FROM UserGroupApp (user_id, group_id, self);';
  AOQL := TransCtl.CreateOQL(OQLText);
  AOQL.Active := true;

  Group := IP_UserGroup(Config.CreatePObjImpl('UserGroup', TransCtl));
  while not AOQL.Result.RQ_IsEof do
  begin
    Group.SendAddUserToGroup(VarToStr(AOQL.ColumnValue['group_id']),
      VarToStr(AOQL.ColumnValue['user_id']));

    AOQL.Result.RQ_Next;
  end;
end;

procedure TP_UserApp.LogActivity(Description: string);
begin
  (* WRITE METHOD CODE HERE *)
end;

function TP_UserApp.IsLocked(): IE_FTBoolean;
var
  log_limit: integer;
begin
  log_limit := 3;
  //if SafeVariantToInt(Self['login_count']) >= log_limit then
  if Self['login_count'] >= log_limit then
    Result := TE_FTBoolean.Create(TransCtl, FTBoolean_true)
  else
    Result := TE_FTBoolean.Create(TransCtl, FTBoolean_false);
end;

procedure TP_UserApp.IncCounter();
begin
  //Self['login_count'] := SafeVariantToInt(Self['login_count']) + 1;
  Self['login_count'] := Self['login_count'] + 1;
end;

procedure TP_UserApp.ResetCounter();
begin
  Self['login_count'] := 0;
end;

procedure TP_UserApp.LockLogin();
var
  log_limit: integer;
begin
  log_limit := 3;
  Self['login_count'] := log_limit;
end;

procedure TP_UserApp.UnLockLogin();
begin
  ResetCounter;
end;

(* UserGroup class *)

procedure TP_UserGroup.SetNewInstanceKey;
begin
  (* Insert code to set primary key here. If inherited action is used,  auto *)
  (* primary key is automatically set from IDGen Server                      *)
  inherited SetNewInstanceKey;
end;

function TP_UserGroup._Destructor(var Msg: string): boolean;
var
  LsUser: IXList;
begin
  (* Insert before deletion actions here. Remove the inherited part below if *)
  (* no referential integrity check / actions is required                    *)
  LsUser := Lists['Ls_UserGroupApp'];
  LsUser.First;
  if not LsUser.EndOfList then
    raise Exception.Create('Group still reference by user. Cannot deleted!');
    
  SendDeleteRequest(Self['group_id']);
  
  Result := inherited _Destructor(Msg);
end;

procedure TP_UserGroup.SendAddRequest(AGroup_ID: string; AGroupName: string
  ; ADesc: string);
var
  SecUpdate: ISecurityUpdate;
  SecContext: ISecurityContext;
  SessInfo: PSessionInfo;
  SessionID: string;
  IPAddr: integer;
begin
  SecContext := Config.SecurityContext;
  SecUpdate := SecContext as ISecurityUpdate;
  SessionID := SecContext.GetSessionID;
  SecContext.GetSessionInfo(SessInfo);
  IPAddr := SessInfo^.ip_address;

  if not SecUpdate.AddGroup(SessionID, AGroup_ID, AGroupName, ADesc, IPAddr) then
    raise Exception.Create('Update error: ' + SecContext.GetLastErrorInfo);
end;

procedure TP_UserGroup.SendModifyRequest(AGroup_ID: string; AGroupName: string
  ; ADesc: string);
var
  SecUpdate: ISecurityUpdate;
  SecContext: ISecurityContext;
  SessInfo: PSessionInfo;
  SessionID: string;
  IPAddr: integer;
begin
  SecContext := Config.SecurityContext;
  SecUpdate := Config.SecurityContext as ISecurityUpdate;
  SessionID := SecContext.GetSessionID;
  SecContext.GetSessionInfo(SessInfo);
  IPAddr := SessInfo^.ip_address;

  if not SecUpdate.ModifyGroup(SessionID, AGroup_ID, AGroupName, ADesc, IPAddr) then
    raise Exception.Create('Update error: ' + SecContext.GetLastErrorInfo);
end;

procedure TP_UserGroup.SendDeleteRequest(AGroup_ID: string);
var
  SecUpdate: ISecurityUpdate;
  SecContext: ISecurityContext;
  SessInfo: PSessionInfo;
  SessionID: string;
  IPAddr: integer;
begin
  SecContext := Config.SecurityContext;
  SecUpdate := Config.SecurityContext as ISecurityUpdate;
  SessionID := SecContext.GetSessionID;
  SecContext.GetSessionInfo(SessInfo);
  IPAddr := SessInfo^.ip_address;

  if not SecUpdate.DeleteGroup(SessionID, AGroup_ID, IPAddr) then
    raise Exception.Create('Update error: ' + SecContext.GetLastErrorInfo);
end;

procedure TP_UserGroup.SendAddUserToGroup(AGroup_ID: string; User_ID: string);
var
  SecUpdate: ISecurityUpdate;
  SecContext: ISecurityContext;
  SessInfo: PSessionInfo;
  SessionID: string;
  IPAddr: integer;
begin
  SecContext := Config.SecurityContext;
  SecUpdate := Config.SecurityContext as ISecurityUpdate;
  SessionID := SecContext.GetSessionID;
  SecContext.GetSessionInfo(SessInfo);
  IPAddr := SessInfo^.ip_address;

  if not SecUpdate.IncludeUserInGroup(SessionID, User_ID, AGroup_ID, IPAddr) then
    raise Exception.Create('Update error: ' + SecContext.GetLastErrorInfo);
end;

procedure TP_UserGroup.SendDeleteUserFromGroup(AGroup_ID: string
  ; User_ID: string);
var
  SecUpdate: ISecurityUpdate;
  SecContext: ISecurityContext;
  SessInfo: PSessionInfo;
  SessionID: string;
  IPAddr: integer;
begin
  SecContext := Config.SecurityContext;
  SecUpdate := Config.SecurityContext as ISecurityUpdate;
  SessionID := SecContext.GetSessionID;
  SecContext.GetSessionInfo(SessInfo);
  IPAddr := SessInfo^.ip_address;

  if not SecUpdate.ExcludeUserFromGroup(SessionID, User_ID, AGroup_ID, IPAddr) then
    raise Exception.Create('Update error: ' + SecContext.GetLastErrorInfo);
end;

procedure TP_UserGroup.RegisterData();
begin
  SendAddRequest(Self['group_id'], Self['GroupName'], Self['Description']);
end;

procedure TP_UserGroup.Modify();
begin
  SendModifyRequest(Self['group_id'], Self['GroupName'], Self['Description']);
end;

procedure TP_UserGroup.AddUser(UserID: string);
begin
  SendAddUserToGroup(Self['group_id'], UserID);
end;

procedure TP_UserGroup.DeleteUser(UserID: string);
begin
  SendDeleteUserFromGroup(Self['group_id'], UserID);
end;

(* UserGroupApp class *)

procedure TP_UserGroupApp.SetNewInstanceKey;
begin
  (* Insert code to set primary key here. If inherited action is used,  auto *)
  (* primary key is automatically set from IDGen Server                      *)
  inherited SetNewInstanceKey;
end;

function TP_UserGroupApp._Destructor(var Msg: string): boolean;
var
  LUser: IP_UserApp;
  LUserGroup: IP_UserGroup;
begin
  (* Insert before deletion actions here. Remove the inherited part below if *)
  (* no referential integrity check / actions is required                    *)
  LUser := IP_UserApp(Links['LUser']);
  LUserGroup := IP_UserGroup(Links['LUserGroup']);
  LUserGroup.DeleteUser(LUser['user_id']);
  
  Result := inherited _Destructor(Msg);
end;

procedure TP_UserGroupApp.Create(LUser: IP_UserApp; LUserGroup: IP_UserGroup);
begin
  Links['LUser'] := LUser;
  Links['LUserGroup'] := LUserGroup;

  LUserGroup.AddUser(LUser['user_id']);
end;

end.
