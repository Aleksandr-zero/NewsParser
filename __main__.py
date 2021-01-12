import sys

from scripts.newsParser import RecordSettingsINI_NewsParser
from scripts.newsParser import NewsParserHabr
from scripts.commandApp import cli


if __name__ == '__main__':
    if len(sys.argv) == 1:

        dataSettingsNewsParser = RecordSettingsINI_NewsParser().readSettings_NewsParser()

        if dataSettingsNewsParser["parseMainTapeHabr"] == "yes" or\
            dataSettingsNewsParser["parseHubHabr"] == "yes" or\
            dataSettingsNewsParser["parseNewsHabr"] == "yes" or\
            dataSettingsNewsParser["parseUserHabr"] == "yes":

            _NewsParserHabr = NewsParserHabr()
            _NewsParserHabr.gettingResponseHabr()


    elif len(sys.argv) > 1:
        cli()
