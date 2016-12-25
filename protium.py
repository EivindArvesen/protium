#!/usr/bin/env python3

import pprint

import jupyter_client # Install local dependency (and restart ST) when developing

import sublime
import sublime_plugin

import sys

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

        # execution is immediate and async, returning a UUID
        msg_id = application.kernel.execute(code)
        # get_msg can block for a reply
        reply = application.kernel.get_shell_msg() #timeout=5
        status = reply['content']['status']

        2+2

        if status == 'ok':
            return_content = reply
        elif status == 'error':
            return_content = reply['content']['traceback']

        #return_content = application.kernel.get_iopub_msg()

        global pSet
        self.view.erase_phantoms("demo")
        pSet = sublime.PhantomSet(self.view, 'demo')
        phantoms = [sublime.Phantom(self.view.sel()[0], "<h1>"+str(return_content)+"</h1>", sublime.LAYOUT_BELOW)]
        pSet.update(phantoms)

        #view.add_phantom("test", view.sel()[0], "Hello, World!", sublime.LAYOUT_BLOCK)
        #view.erase_phantoms("test")

    def run(self, args):
        global application

        # Current selection: self.view.sel()[0].begin(), self.view.sel()[0].end())
        self.run_cell(self, self.view.substr(self.view.line(self.view.sel()[0]))) # view...
