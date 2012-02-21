# corporate.py

import com.ihsan.foundation.mobject as mobject
import com.ihsan.net.socketclient as socket
import os, sys
import ConfigParser
#import rpdb2

# CONSTANTS
CUSTOM_SECTION = 'CUSTOM'
CORPORATE_USER = 'system@corporate'
DEFAULT_CORPORATE_PORT = 2190

class record:
    pass

class BatchProcess(mobject.MObject):

    def mobject_init(self, parameter):
        info = parameter.info.GetRecord(0)

        self.main_pid = info.main_pid
        self.step_id  = info.step_id

        # prepare connection
        destination = info.notify_host, info.notify_port
        self.tcp = socket.TCPClient_STX_ETX(destination)

        self.params = parameter.parameters

    def Notify_OK(self):
        self.Notify(1, "")

    def Notify_Error(self):
        errInfo = str(sys.exc_info()[0]) + "." + str(sys.exc_info()[1])
        self.Notify(2, errInfo)

    def Notify(self, status, errInfo):
        sMessage = "|".join([
            str(self.main_pid),
            str(self.Config.SecurityContext.pid),
            str(self.step_id),
            str(status),
            errInfo
        ])

        tcp = self.tcp
        tcp.Send(sMessage)
        sReply = tcp.Receive()
        replies = sReply.split("|")
        if replies[0] == "0":
            raise "Notify service error", replies[1]
    #--def

class Corporate(mobject.MObject):

    def mobject_init(self, bNotLogin = 0):
        self.HasLogin = not bNotLogin
        self.AutoResponseError = 0

        host = '127.0.0.1'
        port = (
            int(self.Config.GetGlobalSetting('CORPORATE_PORT')) or
            DEFAULT_CORPORATE_PORT
        )
        self.SetEndPoint(host, port)

        if self.HasLogin:
            self.LoginContext = self.LoadLoginContext()

    def SetAutoResponseError(self):
        self.AutoResponseError = 1

    def SetEndPoint(self, host, port):
        self.host = host
        self.port = port 

        destination = host, port
        self.tcp = socket.TCPClient_STX_ETX(destination)

    def SendRequest(self, request):
        message = str(request.__dict__)

        tcp = self.tcp
        tcp.Send(message)
        r_message = tcp.Receive()
        if not (r_message[0] == '{'):
            raise 'Corporate.SendRequest', 'Received message format is not valid'

        response = record()
        response.__dict__ = eval(r_message)

        if self.AutoResponseError and response.Is_Err:
            raise 'Corporate.Response', response.Err_Message

        return response

    def GetUserHomeDir(self):
        config = self.Config

        user_info = config.SecurityContext.GetUserInfo()
        user_dir = "%s\\%s\\%s" % (
            config.GetGlobalSetting('USERHOMEDIR_ROOT'),
            user_info[4],
            config.SecurityContext.UserID
        )

        return user_dir

    def Login(self, id_user, password, ip_user=''):
        request = record()
        request.Function_Code = 'LOGIN'
        request.Id_User = id_user
        request.Password = password
        request.IP_User = ip_user

        self.LoginContext = self.SendRequest(request)
        self.HasLogin = 1

        self.Corporate_Request = (id_user == CORPORATE_USER)

    def LocalLogin(self, id_user, password, ip_user=''):
        response = record()

        response.Nama_User = 'OP001'
        response.Kode_Cabang = '001'
        response.Nama_Cabang = 'KANTOR PUSAT'
        response.Zona_Waktu = 'WIB'
        response.Level_User = 10
        response.Nomor_Karyawan = None
        response.Kode_Departemen = ''
        response.Nama_Departemen = ''
        response.Kode_Jabatan = ''
        response.Nama_Jabatan = ''
        response.Tipe_User = 'E'
        response.Ls_PeranUser = ['ADM']
        response.Ls_LimitTransaksi = []
        response.Status_Password = 1
        response.EncodedPassword = self.Config.ModLibUtils.EncodeStr(password)
        response.Tanggal_Perbarui = self.Config.Now()
        response.ID_Terminal = 'N/A'

        self.LoginContext = response
        self.HasLogin = 1

        self.Corporate_Request = (id_user == CORPORATE_USER)

    def getSessionFile(self):
        config = self.Config
        session_file = '%s%s_%s' % (
            config.SecurityContext.SessionDirectory,
            config.SecurityContext.UserID,
            config.SecurityContext.SessionID
        )

        return session_file

    def AfterLogin(self):
        self.SaveLoginContext()

        config = self.Config

        user_dir = "%s\\%s\\%s" % (
            config.GetGlobalSetting('USERHOMEDIR_ROOT'),
            self.LoginContext.Kode_Cabang,
            config.SecurityContext.UserID)

        if os.access(user_dir, os.F_OK) != 1:
            os.makedirs(user_dir)

    def SaveLoginContext(self):
        global CUSTOM_SECTION

        config = self.Config
        session_file = self.getSessionFile()

        if os.access(session_file, os.F_OK) != 1:
            raise Exception, 'Session file not found!'

        parser = ConfigParser.ConfigParser()
        parser.read([session_file])
        if not parser.has_section(CUSTOM_SECTION):
            parser.add_section(CUSTOM_SECTION)

        parser.set(CUSTOM_SECTION, 'login_context', str(self.LoginContext.__dict__))
        fp = open(session_file, 'w')
        try:
            parser.write(fp)
        finally:
            fp.close()

    def LoadLoginContext(self):
        global CUSTOM_SECTION

        config = self.Config
        session_file = self.getSessionFile()
        if os.access(session_file, os.F_OK) != 1:
            raise Exception, 'Session file not found!'

        parser = ConfigParser.ConfigParser()
        parser.read([session_file])

        login_context = record()
        login_context.__dict__ = eval(parser.get(CUSTOM_SECTION, 'login_context'))

        return login_context

    def ChangeMyPassword(self, new_password):
        request = record()
        request.Function_Code = 'CHPASS'
        request.Id_User = self.Config.SecurityContext.UserID
        request.New_Password = new_password

        resp = self.SendRequest(request)
        if resp.Is_Err:
            raise 'Corporate', resp.Err_Message

        enc_password = self.Config.ModLibUtils.EncodeStr(new_password)
        self.LoginContext.EncodedPassword = enc_password
        self.SaveLoginContext()

    def ChangePassword(self, userid, new_password):
        request = record()
        request.Function_Code = 'CHPASS'
        request.Id_User = userid
        request.New_Password = new_password

        resp = self.SendRequest(request)
        if resp.Is_Err:
            raise 'Corporate', resp.Err_Message

    def FunctionAccess(self, id_fungsi):
        request = record()
        request.Function_Code = 'AKSES'
        request.Id_User = self.Config.SecurityContext.UserID
        request.Id_Fungsi = id_fungsi

        return self.SendRequest(request)

    def MultiFunctionAccess(self, list_id_fungsi):
        request = record()
        request.Function_Code = 'MULTIAKSES'
        request.Id_User = self.Config.SecurityContext.UserID
        request.List_Id_Fungsi = list_id_fungsi

        return self.SendRequest(request)

    def DualControlCheck(self, userid, password, id_fungsi):
        if self.Config.SecurityContext.UserID == userid:
            resp = record()
            resp.Is_Err = 1
            resp.Err_Message = 'User dual control tidak boleh sama dengan user active!'

            return resp

        request = record()
        request.Function_Code = 'DUALCONTROL'
        request.Id_User = userid
        request.Password = password
        request.Id_Fungsi = id_fungsi

        return self.SendRequest(request)

    def OverrideCheck(self, userid, password, id_fungsi, limit_check=0, limit_value=0.0):
        if self.Config.SecurityContext.UserID == userid:
            raise 'Corporate', 'User override tidak boleh sama dengan user active!'

        request = record()
        request.Function_Code = 'OVERRIDE'
        request.Id_User = userid
        request.Password = password
        request.Id_Fungsi = id_fungsi
        request.Limit_Check = limit_check
        request.Limit_Value = limit_value

        return self.SendRequest(request)

    def GetUserInfo(self, userid):
        request = record()
        request.Function_Code = 'USER'
        request.Id_User = userid

        return self.SendRequest(request)

    def GetCabangInfo(self, kode_cabang):
        request = record()
        request.Function_Code = 'CABANG'
        request.Kode_Cabang = kode_cabang

        return self.SendRequest(request)

    def GetFungsiInfo(self, id_fungsi):
        request = record()
        request.Function_Code = 'FUNGSI'
        request.Id_Fungsi = id_fungsi

        return self.SendRequest(request)

    def GetDepartemenInfo(self, kode_departemen):
        request = record()
        request.Function_Code = 'DEPARTEMEN'
        request.Kode_Departemen = kode_departemen

        return self.SendRequest(request)

    def GetKaryawanInfo(self, nomor_karyawan):
        request = record()
        request.Function_Code = 'KARYAWAN'
        request.Nomor_Karyawan = nomor_karyawan

        return self.SendRequest(request)

    def GetJabatanInfo(self, kode_jabatan):
        request = record()
        request.Function_Code = 'JABATAN'
        request.Kode_Jabatan = kode_jabatan

        return self.SendRequest(request)

    def GetTerminalInfo(self, ip_terminal):
        request = record()
        request.Function_Code = 'TERMINAL'
        request.IP_Terminal = ip_terminal

        return self.SendRequest(request)

    def CheckLimitTransaksi(self, nominal):
        limits = self.LoginContext.Ls_LimitTransaksi
        if not limits.has_key('T'):
            #raise 'Corporate', 'User tidak memiliki limit transaksi'
            limit = 0.0
        else:
            limit = limits['T'][0]
        
        return (nominal <= limit)

    def GetLimitOtorisasi(self):
        limits = self.LoginContext.Ls_LimitTransaksi
        if not limits.has_key('O'):
            return 0.0
        else:
            return limits['O'][0]    
        
        return limit    

    def CheckLimitOtorisasi(self, nominal):
        limits = self.LoginContext.Ls_LimitTransaksi
        if not limits.has_key('O'):
            #raise 'Corporate', 'User tidak memiliki limit otorisasi transaksi'
            limit = 0.0
        else:
            limit = limits['O'][0]    
        return (nominal <= limit)
