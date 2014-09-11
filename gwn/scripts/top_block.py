#!/usr/bin/env python
##################################################
# GNU Wireless Network Flow Graph
# Title: Top Block
# Author: ARTES
# Generated: Tue Aug 19 15:28:28 2014
##################################################
import os
os.chdir("../../scripts/")
print os.getcwd()

import sys
sys.path +=['..']
import blocks.mac.ieee80211.ieee80211 as ieee80211
import blocks.simulators.channels.virtualchannel as channel
import blocks.simulators.consumers.eventconsumer as consumer
import blocks.simulators.generators.eventsimulator as simulator
import gwnblocks.gwntopblock as gwnTB

class top_block(gwnTB.GWNTopBlock):


	def __init__(self):
		gwnTB.GWNTopBlock.__init__(self)


		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 32000

		##################################################
		# Blocks
		##################################################
		self.virtualchannel_0 = channel.GWNVirtualChannel(0.01)	
		self.eventsim_2 = simulator.EventSimulator(3, 1, 'DataData', "0003", "0001", "")	
		self.eventsim_1 = simulator.EventSimulator(5, 1, 'DataData', "0002", "0003", "10")	
		self.eventsim_0 = simulator.EventSimulator(10, 5, 'DataData', "0001", "0002", "10000")	
		self.eventconsumer_2 = consumer.EventConsumer("blkname") 	
		self.eventconsumer_1 = consumer.EventConsumer("blkname") 	
		self.eventconsumer_0 = consumer.EventConsumer("blkname") 	
		self.IEEE80211_2 = ieee80211.IEEE80211("0001")	
		self.IEEE80211_1 = ieee80211.IEEE80211("0003")	
		self.IEEE80211_0 = ieee80211.IEEE80211("0002")	




		##################################################
		# Connections
		##################################################
		self.connect((self.eventsim_1, 0), (self.IEEE80211_0, 1))
		self.connect((self.IEEE80211_1, 1), (self.eventconsumer_1, 0))
		self.connect((self.IEEE80211_0, 0), (self.virtualchannel_0, 0))
		self.connect((self.IEEE80211_1, 0), (self.virtualchannel_0, 0))
		self.connect((self.IEEE80211_2, 0), (self.virtualchannel_0, 0))
		self.connect((self.eventsim_0, 0), (self.IEEE80211_2, 1))
		self.connect((self.virtualchannel_0, 0), (self.IEEE80211_2, 0))
		self.connect((self.virtualchannel_0, 0), (self.IEEE80211_1, 0))
		self.connect((self.virtualchannel_0, 0), (self.IEEE80211_0, 0))
		self.connect((self.IEEE80211_2, 1), (self.eventconsumer_0, 0))
		self.connect((self.IEEE80211_0, 1), (self.eventconsumer_2, 0))
		self.connect((self.eventsim_2, 0), (self.IEEE80211_1, 1))


		##################################################
		# Starting Bloks
		##################################################
		self.virtualchannel_0.start()
		self.eventsim_2.start()
		self.eventsim_1.start()
		self.eventsim_0.start()
		self.eventconsumer_2.start()
		self.eventconsumer_1.start()
		self.eventconsumer_0.start()
		self.IEEE80211_2.start()
		self.IEEE80211_1.start()
		self.IEEE80211_0.start()


	def stop(self):

		##################################################
		# Ending Bloks
		##################################################
		self.virtualchannel_0.stop()
		self.eventsim_2.stop()
		self.eventsim_1.stop()
		self.eventsim_0.stop()
		self.eventconsumer_2.stop()
		self.eventconsumer_1.stop()
		self.eventconsumer_0.stop()
		self.IEEE80211_2.stop()
		self.IEEE80211_1.stop()
		self.IEEE80211_0.stop()



if __name__ == '__main__':
	tb = top_block()
	
	c = raw_input('Press #z to end, or #w to test commands :')        
    	while c != "#z":
       		c = raw_input('Press #z to end, or #w to test commands :')    

	    
	tb.stop()           
    	print "Program ends"
    	exit(0)

