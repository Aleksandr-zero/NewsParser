import configparser
import random
import time
import sys
import csv
import os
import re

import requests
from bs4 import BeautifulSoup


PATH_PROJECTS = os.path.abspath(os.path.join(__file__ , "../.."))


class RecordSettingsINI_NewsParser():
	"""
	Класс реализующий методы записи настроек в файл конфигурации на
	путь - /settings/settings.ini
	"""

	def __init__(self):

		self.config = configparser.ConfigParser()


	def writingSettings_NewsParserHabr(self,
									   parseMainTapeHabr = "yes",
									   parseNewsHabr = "no",
									   parseHubHabr = "no",
									   arrayHubsHabr = "no",
									   parseUserHabr = "no",
									   arrayUsersHabr = "no"):
		""" Создаёт секции для класса "NewsParserHabr" в файле конфигурации. """

		self.config.add_section("NewsParserHabr")
		self.config.set("NewsParserHabr", "parse_main_tape_habr", parseMainTapeHabr)
		self.config.set("NewsParserHabr", "parse_news", parseNewsHabr)
		self.config.set("NewsParserHabr", "parse_hub", parseHubHabr)
		self.config.set("NewsParserHabr", "array_hubs", arrayHubsHabr)
		self.config.set("NewsParserHabr", "parse_user", parseUserHabr)
		self.config.set("NewsParserHabr", "array_users", arrayUsersHabr)

		with open(PATH_PROJECTS + "\\settings\\settings.ini", "w") as configFile:
			self.config.write(configFile)


	def readSettings_NewsParser(self):
		""" Считывает файл конфигурации и передаёт словарь классу 'NewsParser'. """

		self.config.read(PATH_PROJECTS + "\\settings\\settings.ini")

		settingsData = {
			"parseMainTapeHabr": self.config["NewsParserHabr"]["parse_main_tape_habr"],
			"parseNewsHabr": self.config["NewsParserHabr"]["parse_news"],
			"parseHubHabr": self.config["NewsParserHabr"]["parse_hub"],
			"arrayHubsHabr": self.config["NewsParserHabr"]["array_hubs"],
			"parseUserHabr": self.config["NewsParserHabr"]["parse_user"],
			"arrayUsersHabr": self.config["NewsParserHabr"]["array_users"]}

		return settingsData


	def chechsForFile_INI(self):
		""" Проверяет наличие файла конфигурации - settings/settings.ini """

		if not os.path.exists(PATH_PROJECTS + "\\settings\\settings.ini"):

			try:
				os.mkdir(PATH_PROJECTS + "\\settings")

			except FileExistsError:    # если не будет только файла
				None

			self.writingSettings_NewsParserHabr()


try:
	ARRAY_HUBS_HABR = RecordSettingsINI_NewsParser().readSettings_NewsParser()["arrayHubsHabr"].split(",")
except configparser.DuplicateOptionError:
	None

try:
	ARRAY_USERS_HABR = RecordSettingsINI_NewsParser().readSettings_NewsParser()["arrayUsersHabr"].split(",")
except configparser.DuplicateOptionError:
	None


class RecordingTitles_RequestsSession():
	"""
	Класс для работы с requests.Session(), включает в себя: запись заголовков;
	проверку на наличие файла и возвращение Session() 
	"""

	def __init__(self):

		self.userAgent = []
		self.acceptLanguage = []

		self.Session = requests.Session()

		self.failHeader = ["user_agent", "accept_language"]

		self.checksFileExistence()


	def writingHeadersUser_agent(self):
		""" Подготовка к запросам. """

		with open(PATH_PROJECTS + "\\dataHeaders\\data.csv", "r", encoding = "utf-8") as failPath:

			data = csv.DictReader(failPath, fieldnames = self.failHeader, delimiter = ",")

			for row in data:
				self.userAgent.append(row["user_agent"])

			del self.userAgent[0]

		return self.userAgent


	def writingHeadersAccept_language(self):
		""" Подготовка к запросам. """

		with open(PATH_PROJECTS + "\\dataHeaders\\data.csv", "r", encoding = "utf-8") as failPath:

			data = csv.DictReader(failPath, fieldnames = self.failHeader, delimiter = ",")

			for row in data:
				self.acceptLanguage.append(row["accept_language"])

			del self.acceptLanguage[0]

		return self.acceptLanguage


	def checksFileExistence(self):
		""" Проверяет наличие файла с данными для requests.Session(). """

		if os.path.isfile(PATH_PROJECTS + "\\dataHeaders\\data.csv") == False:
			sys.exit(1)


	def writingHeaders(self):
		""" Запись заголовков для requests.Session() """

		self.writingHeadersUser_agent()
		self.writingHeadersAccept_language()

		self.Session.headers.update({
					"user-agent": random.choice(self.userAgent),
					"accept-language": random.choice(self.acceptLanguage),
					"accept": "*/*"})

		del self.userAgent
		del self.acceptLanguage


	def returnsSession(self):
		""" возвращение requests.Session() """

		self.writingHeaders()

		return self.Session


class NewsParserHabr():
	"""
	Класс реализующий набор парсеров сайта "https://habr.com/ru" для просмотра
	новых добавленных статей, и также запись данных в файлы.
	"""

	def __init__(self):

		self.urlHABR = "https://habr.com/ru"

		self.Session = RecordingTitles_RequestsSession().returnsSession()

		RecordSettingsINI_NewsParser().chechsForFile_INI()
		self.dataSettingsNewsParser = RecordSettingsINI_NewsParser().readSettings_NewsParser()

		self.prepareDictForWork()


	def checksInternetAccess(func):
		""" Проверяет наличие выхода в Интернет """

		def checks(self):

			try:
				func(self)
			except requests.exceptions.ConnectionError:
				try:
					time.sleep(6)
					func(self)
				except requests.exceptions.ConnectionError:
					sys.exit(1)

		return checks


	def gettingResponseHabr(self):
		""" Посылает запросы на сайт "Habr" на разные категории """

		if self.dataSettingsNewsParser["parseMainTapeHabr"] == "yes":
			self.gettingResponseHabrMainTape()

		# посылает запросы на категорию "Хабы" сайта
		if ARRAY_HUBS_HABR[0] != "no" and self.dataSettingsNewsParser["parseHubHabr"] == "yes":
			self.gettingResponseHabrHubs()

		if self.dataSettingsNewsParser["parseNewsHabr"] == "yes":
			self.gettingResponseHabrNews()

		# посылает запросы на категорию "Авторы" сайта
		if ARRAY_USERS_HABR[0] != "no" and self.dataSettingsNewsParser["parseUserHabr"] == "yes":
			self.gettingResponseHabrUsers()


		self.checksArticles_For_Plagiarism()
		self.writingArticles_TxtFile()

		self.writesFirstArticles_File()


	@checksInternetAccess
	def gettingResponseHabrMainTape(self):
		""" Получение ответа с сайта - https://habr.com/ru - с главной ленты. """

		for indexPage in range(1, 4):
			responseHabr = self.Session.get(url = f"{self.urlHABR}/page{indexPage}")

			self.parseHtmlHabr(htmlHabr = BeautifulSoup(responseHabr.text, "lxml"),
							   pointerParser = "habrMainTape")


	@checksInternetAccess
	def gettingResponseHabrHubs(self):
		"""
		Получение ответа с сайта - https://habr.com/ru - от категории "hub" """

		for hub in ARRAY_HUBS_HABR:
			responseHabrHub = self.Session.get(url = f"{self.urlHABR}/hub/{hub}/")

			self.parseHtmlHabr(htmlHabr = BeautifulSoup(responseHabrHub.text, "lxml"), 
							   pointerParser = "habrHubs",
							   hubHabr = hub)


	@checksInternetAccess
	def gettingResponseHabrUsers(self):
		"""
		Получение ответа с сайта - https://habr.com/ru - от категории "автора" """

		for user in ARRAY_USERS_HABR:
			responseHabrUser = self.Session.get(url = f"{self.urlHABR}/users/{user}/posts/")

			self.parseHtmlHabr(htmlHabr = BeautifulSoup(responseHabrUser.text, "lxml"), 
							   pointerParser = "habrUsers",
							   userHabr = user)


	@checksInternetAccess
	def gettingResponseHabrNews(self):
		"""
		Получение ответа с сайта - https://habr.com/ru - от категории "news"  (https://habr.com/ru/news/)
		"""

		for indexPage in range(1, 3):
			responseHabr = self.Session.get(url = f"{self.urlHABR}/news/page{indexPage}")

			self.parseHtmlHabr(htmlHabr = BeautifulSoup(responseHabr.text, "lxml"),
							   pointerParser = "habrNews")


	def parseHtmlHabr(self, htmlHabr, pointerParser, hubHabr = "no", userHabr = "no"):
		""" Парсер html-страницы "Habr" """

		mainBlockCards_Habr = htmlHabr.select_one("div.posts_list")

		if not mainBlockCards_Habr:
			os.execv(sys.executable, [sys.executable] + sys.argv)

		for articleHabr in mainBlockCards_Habr.select("article.post.post_preview"):
			self.parserArticleHabr(articleHabr = articleHabr,
								   pointerParser = pointerParser,
								   hubHabr = hubHabr,
								   userHabr = userHabr)


	def parserArticleHabr(self, articleHabr, pointerParser, hubHabr, userHabr):
		""" Собирает информацию о статье на "Habr" и записывает в словарь """

		publicationTimeCard = articleHabr.select_one("span.post__time").text
		authorCard = articleHabr.select_one("span.user-info__nickname.user-info__nickname_small").text

		titleCard = articleHabr.select_one("a.post__title_link").text
		linkCard = articleHabr.select_one("a.post__title_link").get("href")

		if pointerParser == "habrMainTape":
			self.resultArticlesHabrMainType["title"].append(titleCard)
			self.resultArticlesHabrMainType["link"].append(linkCard)
			self.resultArticlesHabrMainType["time"].append(publicationTimeCard)
			self.resultArticlesHabrMainType["author"].append(authorCard)

		elif pointerParser == "habrHubs":
			self.resultArticlesHabrHubs[hubHabr]["title"].append(titleCard)
			self.resultArticlesHabrHubs[hubHabr]["link"].append(linkCard)
			self.resultArticlesHabrHubs[hubHabr]["time"].append(publicationTimeCard)
			self.resultArticlesHabrHubs[hubHabr]["author"].append(authorCard)

		elif pointerParser == "habrUsers":
			self.resultArticlesHabrUsers[userHabr]["title"].append(titleCard)
			self.resultArticlesHabrUsers[userHabr]["link"].append(linkCard)
			self.resultArticlesHabrUsers[userHabr]["time"].append(publicationTimeCard)
			self.resultArticlesHabrUsers[userHabr]["author"].append(authorCard)

		elif pointerParser == "habrNews":
			self.resultArticlesHabrNews["title"].append(titleCard)
			self.resultArticlesHabrNews["link"].append(linkCard)
			self.resultArticlesHabrNews["time"].append(publicationTimeCard)
			self.resultArticlesHabrNews["author"].append(authorCard)


	def prepareDictForWork(self):
		""" Готовит словарь "resultArticlesHabrHubs", "resultArticlesHabrNews",
		"resultArticlesHabrMainType"и "resultArticlesHabrUsers" к работе с данными """

		if self.dataSettingsNewsParser["parseMainTapeHabr"] == "yes":
			self.resultArticlesHabrMainType = {
				"title": [], "link": [],
				"time": [], "author": [],}

		if ARRAY_HUBS_HABR[0] != "no" and self.dataSettingsNewsParser["parseHubHabr"] == "yes":
			self.resultArticlesHabrHubs = {}

			for hub in ARRAY_HUBS_HABR:
				self.resultArticlesHabrHubs[hub] = {
							"title": [], "link": [],
							"time": [], "author": [],}

		if ARRAY_USERS_HABR[0] != "no" and self.dataSettingsNewsParser["parseUserHabr"] == "yes":
			self.resultArticlesHabrUsers = {}

			for user in ARRAY_USERS_HABR:
				self.resultArticlesHabrUsers[user] = {
							"title": [], "link": [],
							"time": [], "author": [],}

		if self.dataSettingsNewsParser["parseNewsHabr"] == "yes":
			self.resultArticlesHabrNews = {
					"title": [], "link": [],
					"time": [], "author": [],}


	def checksArticles_For_Plagiarism(self):
		"""
		Проверяет статьи до той статьи (в файле dataArticles/dataArcicleHabr.txt)
		на плагиат (вышла ли новая статья)
		"""

		if not os.path.isfile(PATH_PROJECTS + "\\dataArticles\\dataArticleHabr.txt"):
			return None

		with open(PATH_PROJECTS + "\\dataArticles\\dataArticleHabr.txt", "r",
				  encoding = "utf-8") as fileArticlesHabr:

			dataFile = fileArticlesHabr.readlines()

		if self.dataSettingsNewsParser["parseMainTapeHabr"] == "yes":

			for article in dataFile:
				if "Habr Main Type" in article:

					for titleNewArticle in self.resultArticlesHabrMainType["title"]:
						if titleNewArticle == re.sub("Habr Main Type --> ", "", article.strip()):
							self.removesUnwantedArticles_From_Array(
								indexArticle = self.resultArticlesHabrMainType["title"].index(titleNewArticle),
								lenArray = len(self.resultArticlesHabrMainType["title"]),
								dictArticles = self.resultArticlesHabrMainType)


		if self.dataSettingsNewsParser["parseNewsHabr"] == "yes":

			for article in dataFile:
				if "Habr News" in article:

					for titleNewArticle in self.resultArticlesHabrNews["title"]:
						if titleNewArticle == re.sub("Habr News --> ", "", article.pop(0).strip()):
							self.removesUnwantedArticles_From_Array(
								indexArticle = self.resultArticlesHabrNews["title"].index(titleNewArticle),
								lenArray = len(self.resultArticlesHabrNews["title"]),
								dictArticles = self.resultArticlesHabrNews)


		if self.dataSettingsNewsParser["parseHubHabr"] == "yes" and ARRAY_HUBS_HABR[0] != "no":

			pastArticlesHabrHub = {}

			for article in dataFile:
				if "Habr hub" in article:
					pastArticlesHabrHub[re.sub("Habr hub: ", "", article.split(" --> ")[0])] =\
												article.split(" --> ")[1].strip()

			for hub, titlePastArticle in pastArticlesHabrHub.items():
				for titleNewArticle in self.resultArticlesHabrHubs[hub]["title"]:
					if titlePastArticle == titleNewArticle:
	
						self.removesUnwantedArticles_From_Array(
								indexArticle = self.resultArticlesHabrHubs[hub]["title"].index(titleNewArticle),
								lenArray = len(self.resultArticlesHabrHubs[hub]["title"]),
								dictArticles = self.resultArticlesHabrHubs[hub])


		if self.dataSettingsNewsParser["parseUserHabr"] == "yes" and ARRAY_HUBS_HABR[0] != "no":

			pastArticlesHabrUser = {}

			for article in dataFile:
				if "Habr user" in article:
					pastArticlesHabrUser[re.sub("Habr user: ", "", article.split(" --> ")[0])] =\
												article.split(" --> ")[1].strip()

			for user, titlePastArticle in pastArticlesHabrUser.items():
				for titleNewArticle in self.resultArticlesHabrUsers[user]["title"]:
					if titlePastArticle == titleNewArticle:
	
						self.removesUnwantedArticles_From_Array(
								indexArticle = self.resultArticlesHabrUsers[user]["title"].index(titleNewArticle),
								lenArray = len(self.resultArticlesHabrUsers[user]["title"]),
								dictArticles = self.resultArticlesHabrUsers[user])


	def removesUnwantedArticles_From_Array(self, indexArticle, lenArray, dictArticles):
		""" Чистит словарь результатов от ненужных статей """

		for index in range(indexArticle, lenArray - 1):
			del dictArticles["title"][indexArticle + 1]
			del dictArticles["link"][indexArticle + 1]
			del dictArticles["time"][indexArticle + 1]
			del dictArticles["author"][indexArticle + 1]


	def writingArticles_TxtFile(self):
		""" Записывает новые добавленные статьи в txt-файлы расположенный на рабочем столе """

		with open("C:\\Users\\Aleksandr\\Desktop\\FreshArticles.txt", "w", encoding = "utf-8") as txtFile:

			txtFile.write("[HABR]\n")

			if self.dataSettingsNewsParser["parseMainTapeHabr"] == "yes":

				txtFile.write("\n[PARSE MAIN TAPE HABR]\n")

				for index in range(0, len(self.resultArticlesHabrMainType["title"])):
					txtFile.write(f'{self.resultArticlesHabrMainType["title"][index]} - '\
								+ f'{self.resultArticlesHabrMainType["link"][index]} - '\
								+ f'{self.resultArticlesHabrMainType["time"][index]} - '\
								+ f'author: {self.resultArticlesHabrMainType["author"][index]}\n')


			if self.dataSettingsNewsParser["parseNewsHabr"] == "yes":

				txtFile.write("\n[PARSE NEWS HABR]\n")

				for index in range(0, len(self.resultArticlesHabrNews["title"])):
					txtFile.write(f'{self.resultArticlesHabrNews["title"][index]} - '\
								+ f'{self.resultArticlesHabrNews["link"][index]} - '\
								+ f'{self.resultArticlesHabrNews["time"][index]} - '\
								+ f'author: {self.resultArticlesHabrNews["author"][index]}\n')


			if ARRAY_HUBS_HABR[0] != "no" and self.dataSettingsNewsParser["parseHubHabr"] == "yes":

				for hub, aricles in self.resultArticlesHabrHubs.items():

					txtFile.write(f"\n[HABR HUB --> {hub}]\n")

					for index in range(0, len(self.resultArticlesHabrHubs[hub]["title"])):
						txtFile.write(f'{self.resultArticlesHabrHubs[hub]["title"][index]} - '\
									+ f'{self.resultArticlesHabrHubs[hub]["link"][index]} - '\
									+ f'{self.resultArticlesHabrHubs[hub]["time"][index]} - '\
									+ f'author: {self.resultArticlesHabrHubs[hub]["author"][index]}\n')


			if ARRAY_USERS_HABR[0] != "no" and self.dataSettingsNewsParser["parseUserHabr"] == "yes":

				for user, aricles in self.resultArticlesHabrUsers.items():

					txtFile.write(f"\n[HABR USER --> {user}]\n")

					for index in range(0, len(self.resultArticlesHabrUsers[user]["title"])):
						txtFile.write(f'{self.resultArticlesHabrUsers[user]["title"][index]} - '\
									+ f'{self.resultArticlesHabrUsers[user]["link"][index]} - '\
									+ f'{self.resultArticlesHabrUsers[user]["time"][index]} - '\
									+ f'author: {self.resultArticlesHabrUsers[user]["author"][index]}\n')


	def writesFirstArticles_File(self):
		""" Записывает 1-ые статься в txt-файл на путь dataArticles//dataArticleHabr.txt """

		if not os.path.exists(PATH_PROJECTS + "\\dataArticles\\dataArticleHabr.txt"):
			os.mkdir(PATH_PROJECTS + "\\dataArticles")

		with open(PATH_PROJECTS + "\\dataArticles\\dataArticleHabr.txt",
				"w", encoding = "utf-8") as fileArticleHabrMainType:

			if self.dataSettingsNewsParser["parseMainTapeHabr"] == "yes":
				fileArticleHabrMainType.write(f"Habr Main Type --> {self.resultArticlesHabrMainType['title'][0]}\n")

			if self.dataSettingsNewsParser["parseNewsHabr"] == "yes":
				fileArticleHabrMainType.write(f"Habr News --> {self.resultArticlesHabrNews['title'][0]}\n")

			if self.dataSettingsNewsParser["parseHubHabr"] == "yes" and ARRAY_HUBS_HABR[0] != "no":
				for hub in ARRAY_HUBS_HABR:
					fileArticleHabrMainType.write(f"Habr hub: {hub} --> "\
												+ f'{self.resultArticlesHabrHubs[hub]["title"][0]}' + "\n")

			if self.dataSettingsNewsParser["parseUserHabr"] == "yes" and ARRAY_USERS_HABR[0] != "no":
				for user in ARRAY_USERS_HABR:
					fileArticleHabrMainType.write(f"Habr user: {user} --> "\
												+ f'{self.resultArticlesHabrUsers[user]["title"][0]}' + "\n")
