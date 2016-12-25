#!/usr/bin/env python3
# encoding: utf-8

import pprint

import jupyter_client # Install local dependency (and restart ST) when developing

import sublime
import sublime_plugin

import sys
from queue import Empty

class Application(object):
    """docstring for Application"""
    def __init__(self):
        super(Application, self).__init__()


global application
application = Application()

# this is a helper method for turning a fraction of a connection-file name
# into a full path.  If you already know the full path, you can just use that
# cf = find_connection_file('54677')

# kc = BlockingKernelClient(connection_file=cf)
# kc.load_connection_file()
# kc.start_channels()
# kc.get_shell_msg() # pop start message

def start_kernel():
    global application
    kernel_name = 'python3' # ipython3 kernel install # ipython kernel install

    #ksm = jupyter_client.kernelspec.KernelSpecManager()
    #print(ksm.get_all_specs())
    #sys.exit()

    if not hasattr(application, 'kernel'):
        kernel_manager = jupyter_client.KernelManager()
        kernel_manager.kernel_name = kernel_name
        kernel_manager.start_kernel()
        application.kernel_manager = kernel_manager
        application.kernel = kernel_manager.client()
        application.kernel.start_channels()
        kernel = application.kernel
    else:
        kernel_manager.start_kernel()
        kernel.start_channels()

    kernel.get_shell_msg() # pop start message
    # Once you have shutdown a kernel, if you need a kernel again, you should create a new one (i.e. new instances of KernelManager() and KernelClient()). They are not designed to be reused to start multiple kernels.

def plugin_loaded():
    """The ST3 entry point for plugins."""
    start_kernel()

def plugin_unloaded():
    """Called directly from sublime on plugin unload."""
    global application
    if hasattr(application, 'kernel'):
        application.kernel_manager.shutdown_kernel()
        try:
            del application.kernel_manager
        except Exception as e:
            pass
    try:
        del application.kernel
    except Exception as e:
        pass

class ProtiumEvaluateCommand(sublime_plugin.WindowCommand):
    """Eval selection."""

    def run(self):
        """Main function, runs on activation."""
        self.window.run_command(
            'protium_communicate', {}
        )

class ProtiumCommunicateCommand(sublime_plugin.TextCommand):
    """Eval"""
    def run_cell(self, view, code):
        # now we can run code.  This is done on the shell channel
        #print ("running: " + code)

        msg_id = application.kernel.execute(code)
        state='busy'
        data={}
        while state!='idle' and application.kernel.is_alive():
            try:
                msg=application.kernel.get_iopub_msg(timeout=1)
                if not 'content' in msg: continue
                content = msg['content']
                if 'data' in content:
                    data=content['data']
                if 'execution_state' in content:
                    state=content['execution_state']
            except Empty:
                pass

        repl = application.kernel.get_shell_msg()
        status = repl['content']['status']
        if status == 'ok':
            reply = '√'
        elif status == 'error':
            reply = repl['content']['traceback']

        self.view.erase_phantoms("demo")

        try:
            return_value = data['text/plain']
        except Exception as e:
            try:
                return_value = reply
            except Exception as e:
                return_value = None

        if return_value:
            global pSet
            pSet = sublime.PhantomSet(self.view, 'demo')
            phantoms = [sublime.Phantom(self.view.sel()[0], str(return_value), sublime.LAYOUT_BLOCK)]
            pSet.update(phantoms)

        #view.add_phantom("test", view.sel()[0], "Hello, World!", sublime.LAYOUT_BLOCK)
        #view.erase_phantoms("test")

    def run(self, args):
        global application


        # Current selection: self.view.sel()[0].begin(), self.view.sel()[0].end())
        self.run_cell(self, self.view.substr(self.view.line(self.view.sel()[0]))) # view...
