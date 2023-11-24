from thefuzz import fuzz


class Searcher:
	# это весь алгоритм поиска :/
	def search(self, match_ps, match_1win): # сюда кидаем название матча с ps3838 и сам матч с 1win
		ps_home, ps_away = match_ps.split('-vs-') # тут разделяем

		# и тут сравнение, fuzz.ratio() возвращает что-то типо % насколько строки друг на друга похожи
		if fuzz.partial_ratio(ps_home, match_1win['homeTeamName']) <= 80: return False # вот и вся магия -_-
		if fuzz.partial_ratio(ps_away, match_1win['awayTeamName']) <= 80: return False

		return True # тру
