#!/usr/bin/env python
##################################################
# GNU Wireless Network Flow Graph
# Title: Top Block1
# Generated: Wed Aug 13 13:21:19 2014
##################################################
import os
os.chdir("../../scripts/")
print os.getcwd()

import sys
sys.path +=['..']
import blocks.framers.ieee80211.deframer as deframer
import blocks.framers.ieee80211.framer as framer
import blocks.simulators.channels.virtualchannel as channel
import blocks.simulators.consumers.eventconsumer as consumer
import blocks.simulators.generators.eventsimulator as simulator
import gwnblocks.gwntopblock as gwnTB

class top_block1(gwnTB.GWNTopBlock):


	def __init__(self, queues_size=12):
		gwnTB.GWNTopBlock.__init__(self, queues_size=12)


		##################################################
		# Parameters
		##################################################
		self.queues_size = queues_size

		##################################################
		# Variables
		##################################################
		self.var_0 = var_0 = 1

		##################################################
		# Blocks
		##################################################
		self.virtualchannel_0 = channel.GWNVirtualChannel(0.01)	
		self.framer80211_0 = framer.Framer()	
		self.eventsim_0 = simulator.EventSimulator(1, 3, 'DataData', "10:10:10:10:10:10", "11:11:11:11:11:11", "5")	
		self.eventconsumer_1 = consumer.EventConsumer("blkname") 	
		self.eventconsumer_0 = consumer.EventConsumer("blkname") 	
		self.deframer80211_0 = deframer.Deframer()	




		##################################################
		# Connections
		##################################################
		self.connect((self.eventsim_0, 0), (self.framer80211_0, 0))
		self.connect((self.framer80211_0, 0), (self.eventconsumer_0, 0))
		self.connect((self.deframer80211_0, 0), (self.eventconsumer_1, 0))
		self.connect((self.framer80211_0, 0), (self.virtualchannel_0, 0))
		self.connect((self.virtualchannel_0, 0), (self.deframer80211_0, 0))


		##################################################
		# Starting Bloks
		##################################################
		self.virtualchannel_0.start()
		self.framer80211_0.start()
		self.eventsim_0.start()
		self.eventconsumer_1.start()
		self.eventconsumer_0.start()
		self.deframer80211_0.start()


	def stop(self):

		##################################################
		# Ending Bloks
		##################################################
		self.virtualchannel_0.stop()
		self.framer80211_0.stop()
		self.eventsim_0.stop()
		self.eventconsumer_1.stop()
		self.eventconsumer_0.stop()
		self.deframer80211_0.stop()



if __name__ == '__main__':
	tb = top_block1()
	
	c = raw_input('Press #z to end, or #w to test commands :')        
    	while c != "#z":
       		c = raw_input('Press #z to end, or #w to test commands :')    

	    
	tb.stop()           
    	print "Program ends"
    	exit(0)

