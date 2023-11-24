# задача 1: сейчас берутся только матчи за сегодня, а надо бы за 24 часа (функция get_prematch)
# задача 2: добавить исчезнование матча, но при этом важно учесть начало матча, чтобы исключить исчезновение по этой причине. А еще наверное бывают просто закрытые кэфы
# задача 3: нужно добавить разницу времени, а не только время появления события

#TODO: different percents for different odds
#TODO: another sports check carefully (why no bets?)
#TODO: add odds after 10, 30 and 120 mins
#TODO: find matches and markets in 1win
#TODO: check odds for Value
#TODO: make bets with check odds in basket

import asyncio
from datetime import datetime
import logging
import time

from ps3838Com import Ps3838Com
from odds_tracker import OddsTracker
from onewin import OneWin
from searcher import Searcher
import nest_asyncio
nest_asyncio.apply()


async def main():
	MAIN_LOOP = 1
	limit_time = 12  # limit time in hours
	mk = 1
	date_ = datetime.today().strftime('%Y-%m-%d')

	searcher = Searcher()

	ps = Ps3838Com()
	win1 = OneWin()
	await ps.setup()  # Инициализируем сессию здесь
	tracker = OddsTracker(significance_percent=5, time_span_minutes=15)

	while True:
		try:
			matches = await ps.get_prematch()
			data = await ps.run(matches)
			tracker.update_data(data)

# =====================================================================================================================================
			for ps_game in tracker.check_for_significant_drops(): # игра с ps3838
				ps_match = ps_game['match'] # название матча (home-vs-away)
				print(f"Матч ps3838 [{ps_game['sport']}]:", ps_match)

				for win_match in win1.get_matches(): # проходим по матчам из 1win prematches
					if not searcher.search(ps_match, win_match): continue # пропускаем которых нету на 1win
					print("Матч '" + ps_match + "' найден на 1win")

					for odd in win1.get_odds(win_match['id']): # .get_odds() возвращает и тоталы, и победы, и форы и всё остальное
						frmd_odd = win1.format_odd(odd) # формартируем odd: (<фора>, <коеф>)
						if not frmd_odd: continue # .format_odd() может вернуть None если это не гандикап (фора)
						if frmd_odd[0] != ps_game['market']: continue # и если это не та фора как на ps3838 то скипает
						print(f"Форы совпали: {ps_game['market']} | {frmd_odd[0]}")

						for drop in ps_game['drops']: # тут проходимся по коефам
							time, old_odds, new_odds = drop # это взято из odds_tracker.py:81
							print(f"Коефы: {new_odds} | {frmd_odd[1]}")

							if new_odds != frmd_odd[1]: continue # если коефы не такие, то скипаем

							# и если всё нормально и с матчем, и с форой, и с коефами то генерит ссылку как и ValueBot
							link = win1.generate_link(win_match, frmd_odd) # https://... —> H1 0.5 (5.3)
							print(link)
# =====================================================================================================================================

			sleep_time = 20
			await asyncio.sleep(sleep_time)
		except Exception as e:
			logging.error(f"{e}")
			await asyncio.sleep(20)
			continue

if __name__ == "__main__":
	logging.basicConfig(
		level=logging.INFO,
		format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
		datefmt='%Y-%m-%d:%H:%M:%S'
	)

	logging.info("Start Pinnacle scraper...")
	asyncio.run(main())
