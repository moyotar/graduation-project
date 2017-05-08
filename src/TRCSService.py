# -*- coding: utf-8 -*-

import win32serviceutil
import win32service
import win32event
import servicemanager
import Mylex
import Myyacc
import MyInterpreter

class TRCSService(win32serviceutil.ServiceFramework):
    '''TRCS: The Remote Control Software'''
    _svc_name_ = "TRCSService"  #服务名
    _svc_display_name_ = "TRCSService"  #服务在windows系统中显示的名称
    _svc_description_ = "The Remote Control Software Service"  #服务的描述
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.run = True

    def SvcDoRun(self):
        pass

    def SvcStop(self):
        pass


if __name__=='__main__':
    if len(sys.argv) == 1:
        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(TRCSService)
            servicemanager.Initialize('TRCSService', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error, details:
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        win32serviceutil.HandleCommandLine(PythonService)    
