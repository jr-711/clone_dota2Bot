import socketio
import re
import argparse
import json
import Config
import asyncio
from model.plugmanager import PluginManager

sio = socketio.Client()
managers = {}

@sio.event
def connect():
    print('\rConnection established.', flush=True)

@sio.event
def OnGroupMsgs(data):
	message_data = data['CurrentPacket']['Data']
	from_group = message_data['FromGroupId']
	if from_group not in managers:
		return
	manager = managers[from_group]
	manager.handle(message_data)

@sio.event
def OnFriendMsgs(data):
	print('OnFriendMsgs: ', data)

@sio.event
def OnEvents(data):
	print('OnEvents: ', data)

@sio.event
def disconnect():
    print('disconnected from server')

def init():
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--config', default='./config.json')
	args = parser.parse_args()
	Config.Load(args.config)
	for group in Config.groups:
		managers[group] = PluginManager(group)
		managers[group].add_plugin('DOTA2战绩播报')
	print('Pulgin Manager initialized.')

if __name__ == "__main__":
	init()
	print('Connecting to server...', end='', flush=True)
	sio.connect(Config.sio_url, transports=['websocket'])
	try:
		sio.wait()
	except KeyboardInterrupt:
		for group in managers:
			managers[group].shutdown()
		print('Say you next time~')
		exit(0)