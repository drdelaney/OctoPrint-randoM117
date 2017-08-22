# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import octoprint.events
import octoprint._version
import requests
import random

# TODO:
# - Fix update quote on save
# - impliment use local file
# - detect if url starts with http or not
# - test windows newline formtatted files

# Grab OctoPrint version info
# Please tell me if there is a better or cleaner way to grab the x.y.z version
from octoprint._version import get_versions
versions = get_versions()
octoversion = versions['version']

class randoM117Plugin(octoprint.plugin.StartupPlugin,
                        octoprint.plugin.SettingsPlugin,
                        octoprint.plugin.AssetPlugin,
                        octoprint.plugin.EventHandlerPlugin,
                        octoprint.plugin.TemplatePlugin):

	def get_settings_defaults(self):
		return dict(
                    url="http://dev.loclhst.com/m117otd/test.list",
                    lastquote="",
                    uselocalfile=False,
                    getnewquote=False
		)

	def get_update_information(self):
		return dict(
			randoM117=dict(
				displayName="randoM117 Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="drdelaney",
				repo="OctoPrint-randoM117",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/drdelaney/OctoPrint-randoM117/archive/{target_version}.zip"
			)
		)

        def get_template_configs(self):
            return [
                dict(type="settings", custom_bindings=False)
            ] 

        def on_settings_save(self, data):
            if self._settings.get(['getnewquote']):
                self.getQuote()
                self._settings.set(["getnewquote"], False)

        def on_after_startup(self):
            self.getQuote()

        def on_event(self, event, payload):
            if event == 'Connected':
                # Send the M117 
                self._printer.commands("M117 {}".format(self._settings.get(['lastquote'])))

        def getQuote(self):
	    useragent = 'OctoPrint/'+octoversion+' ('+self._plugin_name+'/'+self._plugin_version+')'

	    headers = requests.utils.default_headers()
	    headers.update( { 'User-Agent': useragent, } )

	    req = requests.get(self._settings.get(['url']), headers=headers)

	    quoteList = req.text.split("\n")

            # There can be only one
            randomQuote = random.choice(quoteList)

            # Log the quote
            self._settings.set(["lastquote"], randomQuote)
            self._logger.info(self._settings.get(['lastquote']))


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "randoM117 Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = randoM117Plugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

