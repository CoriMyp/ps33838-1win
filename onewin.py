import requests
from fake_useragent import UserAgent
import json


# ссылка одна и та же, для получения всех матчей prematch и всех odds матча
URL = "https://1win.direct/microservice/ask"

# это payload для всех матчей prematch
PAYLOAD1 = {
	"name": "MATCH-STORAGE-PARSED:matches-hot",
	"payload": {
		"service": "prematch",
		"lang": "en",
		"localeId": 11
	}
}

# а это payload для odds одного матча 
PAYLOAD2 = lambda id: {# 'id' - айди матча (PAYLOAD2 ламбда-функция которая берёт id матча и возвращает payload с этим значением)
	"name": "MATCH-STORAGE-PARSED:odds-list",
	"payload": {
		"lang": "en",
		"localeId": 11,
		"service": "prematch",
		"matchId": str(id) # требует строкой, а не числом
	}
}


class OneWin:
	def __init__(self):
		# будет даже лучше через aiohttp
		self.session = requests.Session()
		self.session.headers = { 'user-agent': UserAgent().random }


	def get_matches(self):
		with self.session.post(URL, json=PAYLOAD1) as responce: # ставим payload1 для подгрузки всех матчей
			for match in json.loads(responce.text)['matches']: # переводим json в python обьект
				yield match # можно и все матчи сразу возвращать


	def get_odds(self, match_id):
		# тут подгружаем все odds из этого матча
		with self.session.post(URL, json=PAYLOAD2(match_id)) as responce: # в payload2 сразу передаётся айди матча и возвращается payload уже с ним
			# with open('odds.json', "w", encoding='utf=8') as f:
			# 	f.write(responce.text)

			for odd in json.loads(responce.text)['odds']: # с json в python обьект..
				yield odd # можно и сразу все odds'ы возвращать..


	def format_odd(self, odd):
		# этот if отпределяет фору (для тотала там по другому немного)
		if "hcp=" not in odd['id']: return None

		# это смотрит чтобы фора была не ничьей (не шарю в этом, но там такое есть)
		if odd['outCome'] not in ['1', '2']: return None

		# а это чтобы фора нормальной.. а не 0:3 или 1:2
		if ':' in odd['specialValue']: return None

		# и тут возвращается чистенькая фора и её коеф заодно
		return f"H{odd['outCome']} {float(odd['specialValue'])}", odd['coefficient']


	def generate_link(self, match, frmd_odd): # https://1weiuf.top/bets/prematch/35/348/1704/15532816 - пример ссылки
		# берётся с match и подставляется в ссылку.. всё просто..
		url = f"https://1weiuf.top/bets/prematch/{match['sportId']}/{match['categoryId']}/{match['tournamentId']}/{match['id']}"

		#        ссылка       фора      (   её коеф   )
		return f"{url} —> {frmd_odd[0]} ({frmd_odd[1]})"