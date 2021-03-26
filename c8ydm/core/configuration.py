#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, time
from c8ydm.framework.modulebase import Listener, Initializer
from c8ydm.framework.smartrest import SmartRESTMessage


class ConfigurationManager(Listener, Initializer):

    def __init__(self, serial, agent, configuration):
        self.configuration = configuration
        self.agent = agent
        self.serial = serial

    def group(self, seq, sep):
        result = [[]]
        for e in seq:
          if sep not in e:
            result[-1].append(e)
          else:
            result[-1].append(e[:e.find(sep)])
            result.append([])

        if result[-1] == []:
          result.pop() # thx iBug's comment
        return result

    def handleOperation(self, message):
        try:
            if 's/ds' in message.topic and message.messageId == '513':
                ## When multiple operations received just take the first one for further processing
                logging.info('Configuration Operation received: ' + str(message.values))
                message.values = self.group(message.values, '\n513')[0]
                executing = SmartRESTMessage('s/us', '501', ['c8y_Configuration'])
                self.agent.publishMessage(executing)

                self.configuration.writeConfigString(message.values[1][1:-1])
                success = SmartRESTMessage('s/us', '503', ['c8y_Configuration'])
                configs = self.configuration.getConfigString()
                self.agent.publishMessage(SmartRESTMessage('s/us', '113', ['"' + configs + '"']))
                self.agent.publishMessage(success)

        except Exception as e:
          logging.exception(e)
          failed = SmartRESTMessage('s/us', '502', ['c8y_Configuration', str(e)])
          self.agent.publishMessage(failed)


    def getSupportedOperations(self):
        return ['c8y_Configuration']


    def getSupportedTemplates(self):
        return []


    def getMessages(self):
        configs = self.configuration.getConfigString()
        configMessage = SmartRESTMessage('s/us', '113', ['"' + configs + '"'])
        return [configMessage]
