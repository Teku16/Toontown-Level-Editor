"""Undocumented Module"""

__all__ = ['DirectObject']


from direct.directnotify.DirectNotifyGlobal import directNotify
from MessengerGlobal import messenger
from direct.showbase.PythonUtil import ClassTree

class DirectObject:
    """
    This is the class that all Direct/SAL classes should inherit from
    """
    def __init__(self):
        pass

    #def __del__(self):
        # This next line is useful for debugging leaks
        #print "Destructing: ", self.__class__.__name__

    # Wrapper functions to have a cleaner, more object oriented approach to
    # the messenger functionality.

    def accept(self, event, method, extraArgs=[]):
        return messenger.accept(event, self, method, extraArgs, 1)

    def acceptOnce(self, event, method, extraArgs=[]):
        return messenger.accept(event, self, method, extraArgs, 0)

    def ignore(self, event):
        return messenger.ignore(event, self)

    def ignoreAll(self):
        return messenger.ignoreAll(self)

    def isAccepting(self, event):
        return messenger.isAccepting(event, self)

    def getAllAccepting(self):
        return messenger.getAllAccepting(self)

    def isIgnoring(self, event):
        return messenger.isIgnoring(event, self)

    def classTree(self):
        return ClassTree(self)

    #This function must be used if you want a managed task
    def addTask(self, *args, **kwargs):
        if(not hasattr(self,"_taskList")):
            self._taskList = {}
        kwargs['owner']=self
        task = taskMgr.add(*args, **kwargs)
        return task

    def doMethodLater(self, *args, **kwargs):
        if(not hasattr(self,"_taskList")):
            self._taskList ={}
        kwargs['owner']=self
        task = taskMgr.doMethodLater(*args, **kwargs)
        return task

    def removeTask(self, taskOrName):
        if type(taskOrName) == type(''):
            # we must use a copy, since task.remove will modify self._taskList
            if hasattr(self, '_taskList'):
                taskListValues = self._taskList.values()
                for task in taskListValues:
                    if task.name == taskOrName:
                        task.remove()
        else:
            taskOrName.remove()

    def removeAllTasks(self):
        if hasattr(self,'_taskList'):
            for task in self._taskList.values():
                task.remove()

    def _addTask(self, task):
        self._taskList[task.id] = task

    def _clearTask(self, task):
        del self._taskList[task.id]

    def detectLeaks(self):
        if not __dev__:
            return

        # call this after the DirectObject instance has been destroyed
        # if it's leaking, will notify user

        # make sure we're not still listening for messenger events
        events = messenger.getAllAccepting(self)
        # make sure we're not leaking tasks
        # TODO: include tasks that were added directly to the taskMgr
        tasks = []
        if hasattr(self, '_taskList'):
            tasks = [task.name for task in self._taskList.values()]
        if len(events) or len(tasks):
            estr = choice(len(events), 'listening to events: %s' % events, '')
            andStr = choice(len(events) and len(tasks), ' and ', '')
            tstr = choice(len(tasks), '%srunning tasks: %s' % (andStr, tasks), '')
            notify = directNotify.newCategory('LeakDetect')
            func = choice(getRepository()._crashOnProactiveLeakDetect,
                          self.notify.error, self.notify.warning)
            func('destroyed %s instance is still %s%s' % (self.__class__.__name__, estr, tstr))
