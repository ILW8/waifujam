from collections import defaultdict

last_link = ["appropriate especially", "distance fellow", "regular flower", "summer fifteen", "round cloud",
             "quiet forest", "tear rainbow", "busy continued", "to mathematics", "bent does", "grandmother fighting",
             "star hamster", "clear watercress", "pressure hurt", "century medicine", "yellow jacket", "time article",
             "enjoy notice", "ordinary vote", "faster equator", "station affect", "car speed", "charge camp",
             "art leaf", "below element", "pine touch", "open have", "connected paper", "been acres", "those guide",
             "piece nervous", "trace clear", "front doing", "up chemical", "planned split", "solid explore",
             "unusual noun", "under balloon", "sleep bean", "arrange principal", "lock heaven", "graph rabbit",
             "tried cost", "poem compound", "equally stairs", "save drop", "population jar", "judge principal",
             "where begun", "search shelter", "curious cat", "faster largest", "fearful dragon", "stove hope",
             "desert rabbit", "mountain slope", "tell night", "putting central", "freeze banner", "like automobile",
             "selection noted", "softly popular"]
dio = ["appropriate especially", "time article", "pine touch", "regular flower", "connected paper", "summer fifteen",
       "bent does", "faster equator", "star hamster", "pressure hurt", "round cloud", "busy continued",
       "distance fellow", "open have", "station affect", "tear rainbow", "grandmother fighting", "planned split",
       "ordinary vote", "those guide", "quiet forest", "piece nervous", "art leaf", "clear watercress", "yellow jacket",
       "lock heaven", "been acres", "enjoy notice", "sleep bean", "to mathematics", "equally stairs", "below element",
       "car speed", "trace clear", "up chemical", "under ballon", "poem compound", "save drop", "unusual noun",
       "tried cost", "charge camp", "search shelter", "tell night", "judge principal", "arrange principal",
       "like automobile", "graph rabbit", "front doing", "curious cat", "freeze banner", "stove hope", "mountain slope",
       "where begun", "fearful dragon", "century medicine", "solid explore", "putting central", "population jar",
       "desert rabbit", "faster largest", "selection noted", "softly popular"]
weeh = ["tear rainbow", "appropriate especially", "busy continued", "regular flower", "distance fellow", "enjoy notice",
        "pressure hurt", "clear watercress", "quiet forest", "grandmother fighting", "faster equator",
        "connected paper", "round cloud", "sleep bean", "bent does", "pine touch", "star hamster", "time article",
        "station affect", "open have", "summer fifteen", "planned split", "ordinary vote", "to mathematics",
        "equally stairs", "car speed", "below element", "yellow jacket", "piece nervous", "been acres", "art leaf",
        "unusual noun", "up chemical", "mountain slope", "those guide", "century medicine", "charge camp", "tell night",
        "where begun", "curious cat", "solid explore", "fearful dragon", "poem compound", "population jar",
        "desert rabbit", "under balloon", "search shelter", "lock heaven", "graph rabbit", "save drop",
        "judge principal", "trace clear", "front doing", "arrange principal", "tried cost", "putting central",
        "freeze banner", "faster largest", "stove hope", "selection noted", "like automobile", "softly popular"]
note_txt = ["appropriate especially", "regular flower", "distance fellow", "summer fifteen", "round cloud",
            "to mathematics", "bent does", "grandmother fighting", "busy continued", "century medicine",
            "below element", "station affect", "enjoy notice", "pine touch", "ordinary vote", "charge camp",
            "car speed", "art leaf", "faster equator", "time article", "pressure hurt", "piece nervous", "sleep bean",
            "softly popular", "mountain slope", "like automobile", "unusual noun", "stove hope", "arrange principal",
            "equally stairs", "front doing", "connected paper", "where begun", "judge principal", "population jar",
            "graph rabbit", "been acres", "those guide", "up chemical", "under balloon", "faster largest",
            "planned split", "tell night", "open have", "trace clear", "solid explore", "tried cost", "search shelter",
            "putting central", "selection noted", "poem compound", "save drop"]
waifu_jam_screening_txt = ["busy continued", "round cloud", "summer fifteen", "distance fellow", "star hamster",
                           "connected paper", "appropriate especially", "regular flower", "pine touch", "tear rainbow",
                           "grandmother fighting", "open have", "time article", "faster equator", "bent does",
                           "planned split", "enjoy notice", "to mathematics", "pressure hurt", "lock heaven",
                           "clear watercress", "quiet forest", "sleep bean", "trace clear", "piece nervous", "art leaf",
                           "yellow jacket", "ordinary vote", "save drop", "below element", "been acres", "car speed",
                           "up chemical", "equally stairs", "front doing", "station affect", "under balloon",
                           "those guide", "poem compound", "tell night", "search shelter", "solid explore",
                           "unusual noun", "putting central", "mountain slope", "graph rabbit", "where begun",
                           "century medicine", "arrange principal", "stove hope", "judge principal", "tried cost",
                           "population jar", "charge camp", "like automobile", "desert rabbit", "faster largest",
                           "curious cat", "selection noted", "freeze banner", "fearful dragon", "softly popular"]

judges_lists = (last_link, dio, weeh, note_txt, waifu_jam_screening_txt)
judges_lists_excl = (last_link, dio, weeh, waifu_jam_screening_txt)

if __name__ == "__main__":

    def print_avg_rank(list_of_judges):
        rank_sum = defaultdict(int)
        for ranking in list_of_judges:
            for index, diff_name in enumerate(ranking):
                rank_sum[diff_name] += (index + 1) / float(len(list_of_judges))
        print("| rank | Diff name               | avg rank   |")
        print("+------+-------------------------+------------+")
        rank = 1
        for key, value in {k: v for k, v in sorted(rank_sum.items(), key=lambda item: item[1])}.items():
            print(f"|  {rank:2d}  | {key.ljust(24)}| {value:4.1f}       |")
            rank += 1


    for j_list in (judges_lists, judges_lists_excl):
        print()
        print_avg_rank(j_list)
