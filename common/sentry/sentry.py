import sys
import traceback

import tornado.gen

from common.log import logUtils as log
from objects import glob

def capture():
	"""
	Sentry capture decorator. Use like this to send all unhandled exceptions to Sentry:
	```
	@sentry.capture()
	def blablabla():
		print("a a ben warem a ben ben)
	```
	When running `blablabla()`, the traceback will be print on screen and the
	exception will be sent to Sentry, if enabled.
	Requires tornado app in `glob.application` and sentry client in `glob.application.sentry_client`

	:return:
	"""
	def decorator(func):
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except:
				log.error("Unhandled exception!\n```\n{}\n{}```".format(sys.exc_info(), traceback.format_exc()))
				if glob.sentry:
					glob.application.sentry_client.captureException()
		return wrapper
	return decorator


def captureTornado(func):
	"""
	Capture an exception asynchronously in a tornado handler.
	Use it with asyncGet/asyncPost, like this:

	```
	@tornado.web.asynchronous
	@tornado.gen.engine
	@sentry.captureTornado
	def asyncGet(self):
		...
	```

	:param func:
	:return:
	"""
	def wrapper(self, *args, **kwargs):
		try:
			return func(self, *args, **kwargs)
		except:
			log.error("Unhandled exception!\n```\n{}\n{}```".format(sys.exc_info(), traceback.format_exc()))
			if glob.sentry:
				yield tornado.gen.Task(self.captureException, exc_info=True)
	return wrapper


def captureMessage(message, data=None, extra=None):
	"""
	Sends an arbitrary message to sentry. Does nothing if sentry is disabled.

	:param message: the message
	:param data: the data base, useful for specifying structured data
					interfaces. Any key which contains a '.' will be
					assumed to be a data interface.
	:param extra: a dictionary of additional standard metadata
	:return:
	"""
	if not glob.sentry:
		return
	glob.application.sentry_client.capture("raven.events.Message", message=message, data=data, extra=extra)
