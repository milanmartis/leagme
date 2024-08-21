def generate_bracket(n, round=1, match_id=1, start_id=1):
    if n == 2:
        # Základný prípad: duel medzi dvoma hráčmi
        return [(round, match_id, start_id, start_id + 1)]
    else:
        matches = []
        # Počet hráčov v každej polovici
        half_n = n // 2
        # Generuj zápasy pre ľavú polovicu
        left_bracket = generate_bracket(half_n, round + 1, match_id, start_id)
        matches.extend(left_bracket)
        # Posledné ID použité v ľavej polovici
        last_id = start_id + half_n - 1
        # Generuj zápasy pre pravú polovicu
        right_bracket = generate_bracket(half_n, round + 1, match_id + len(left_bracket), last_id + 1)
        matches.extend(right_bracket)
        # Vytvor zápas medzi víťazmi dvoch polovíc
        matches.append((round, match_id + len(matches), 'Winner Match ' + str(left_bracket[0][1]), 'Winner Match ' + str(right_bracket[0][1])))
        return matches

# Počet hráčov
players = 16
# Generovanie turnajového pavúka
bracket = generate_bracket(players)
for match in bracket:
    print(f"Round: {match[0]}, Match ID: {match[1]}, Player/Match 1: {match[2]}, Player/Match 2: {match[3]}")
