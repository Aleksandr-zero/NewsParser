import getpass
import sys
import os
import re

import requests
import click
from bs4 import BeautifulSoup

from .newsParser import RecordSettingsINI_NewsParser


infoWritingHabr = "Settings Habr\n"\
			+ f"  [1] Checking articles on the main feed --> (no/yes)\n"\
			+ f"  [2] Checking articles on the news --> (no/yes)\n"\
			+ f"  [3] Checking articles for hubs --> (no/yes)"\
			+ f"  [4] List of hubs to check --> (hubs)\n"\
			+ f"  [5] Check articles from users --> (no/yes)\n"\
			+ f"  [6] List of users to check --> (users)"


@click.group(chain = True)
def cli():
	pass


@cli.command("write")
@click.option("--settings", "-s", help = infoWritingHabr, nargs = 0)
@click.argument("settings", nargs = -1)
@click.option("--settings_none", "-sn")
def writingSettingsHabr(settings, settings_none):
	""" Запись настроек для класса "NewsParserHabr",  в файл - //settings//settings.ini """

	settings = list(settings)

	if len(settings) > 6:
		return print("Maximum number of arguments --> 6!")

	elif len(settings) == 0:
		return None

	if re.search(r"\d=[a-zA-Z0-9]{1,60}", " ".join(settings)):

		dataSettings = RecordSettingsINI_NewsParser().readSettings_NewsParser()
		argumentsFunctions = [[key, value] for key, value in dataSettings.items()]

		for item in settings:
			item = item.split("=")

			argumentsFunctions[int(item[0]) - 1][1] = item[1]

		RecordSettingsINI_NewsParser().writingSettings_NewsParserHabr(
								parseMainTapeHabr = argumentsFunctions[0][1],
								parseNewsHabr = argumentsFunctions[1][1],
								parseHubHabr = argumentsFunctions[2][1],
								arrayHubsHabr = argumentsFunctions[3][1],
								parseUserHabr = argumentsFunctions[4][1],
								arrayUsersHabr = argumentsFunctions[5][1])
		return None

	RecordSettingsINI_NewsParser().writingSettings_NewsParserHabr(
								parseMainTapeHabr = settings[0],
								parseNewsHabr = settings[1],
								parseHubHabr = settings[2],
								arrayHubsHabr = settings[3],
								parseUserHabr = settings[4],
								arrayUsersHabr = settings[5])


@cli.command("addBatFile")
def addBatFileToStartup(file_path = ""):
	""" Добавление bat-файла в start menu для запуска скрипта newsParser.py"""

	USER_NAME = getpass.getuser()

	if file_path == "":
		file_path = os.path.abspath(os.path.join(__file__ , "../.."))

		bat_path = f'C:\\Users\\{USER_NAME}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'

		with open(bat_path + '\\' + "runNewsParser.bat", "w") as bat_file:
			bat_file.write('@echo OFF\n'\
						+ r'if "%~1"=="" (set "x=%~f0"& start "" /min "%comspec%" /v/c "!x!" any_word & exit /b)'\
						+ f'\npython "{file_path}"')

	print("Bat file added.")


@cli.command("delBatFile")
def removeBatFileToStartup(file_path = ""):
	""" Удаление bat-файла из start meню для запуска скрипта newsParser.py"""

	USER_NAME = getpass.getuser()

	bat_path = f'C:\\Users\\{USER_NAME}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'

	try:
		os.remove(bat_path + "\\runNewsParser.bat")
	except FileNotFoundError:
		return print("Bat file is already deleted") 

	print("Bat file deleted.")


@cli.command("writeDefault")
def writingSettingsDefault():
	""" Запись настроек к дефолтным """

	RecordSettingsINI_NewsParser().writingSettings_NewsParserHabr()


@cli.command("data")
def outputSettings():
	""" Вывод настроек для класса - NewsParserHabr, из файла - /settings/settings.ini """

	dataSettings = RecordSettingsINI_NewsParser().readSettings_NewsParser()

	return print("Settings Habr\n"\
				+ f"  [1] Checking articles on the main feed --> {dataSettings['parseMainTapeHabr']}\n"\
				+ f"  [2] Checking articles on the news --> {dataSettings['parseNewsHabr']}\n"\
				+ f"  [3] Checking articles for hubs --> {dataSettings['parseHubHabr']}\n"\
				+ f"  [4] List of hubs to check --> {dataSettings['arrayHubsHabr']}\n"
				+ f"  [5] Check articles from users --> {dataSettings['parseUserHabr']}\n"\
				+ f"  [6] List of users to check --> {dataSettings['arrayUsersHabr']}\n")


@cli.command("update")
def updatesPopularHubs_Authors():
	"""
	Обновление пользователей и хабов, и запись в файлы "docx/dataHabrHubs.txt"
	и "docx/dataHabrUsers.txt"
	"""

	htmlUsers = BeautifulSoup(requests.get("https://habr.com/ru/users/").text, "lxml")
	htmlHubs = BeautifulSoup(requests.get("https://habr.com/ru/hubs/").text, "lxml")

	mainBlockUsers = htmlUsers.select_one("div.page__body.page__body_users-list")
	mainBlockHubs = htmlHubs.select_one("div.page__body.page__body_hubs-list")

	scoreUser = 1
	scoreHubs = 1

	with open(f"{os.path.abspath(os.path.join(__file__ , '../..'))}\\docx/dataHabrUsers.txt", "w", encoding = "utf-8") as dataFile:

		for blockUser in mainBlockUsers.select("div.table-grid__item.table-grid__item_left"):

			nameUser = blockUser.select_one("a.list-snippet__fullname").text
			nicknameUser = blockUser.select_one("a.list-snippet__nickname").text

			dataFile.write(f"{str(scoreUser)}) {nicknameUser} --> {nameUser}\n")

			scoreUser += 1

	with open(f"{os.path.abspath(os.path.join(__file__ , '../..'))}\\docx/dataHabrHubs.txt", "w", encoding = "utf-8") as dataFile:

		for blockHub in mainBlockHubs.select("div.table-grid__item.table-grid__item_left"):

			nameHub = blockHub.select_one("a.list-snippet__title-link").text
			nicknameHub = blockHub.select_one("a.list-snippet__title-link").get("href")

			dataFile.write(f"{str(scoreHubs)}) {nicknameHub.split('/')[-2]} --> {nameHub}\n")

			scoreHubs += 1
