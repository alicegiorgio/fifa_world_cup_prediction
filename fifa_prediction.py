import csv


def get_data(file_name):
    with open(file_name, 'r') as raw_matches_file:
        next(raw_matches_file)
        return list(csv.reader(raw_matches_file, delimiter=','))


def data_preprocess(raw_matches_list):
    # Match dictionary: key: 'team1_name:team2_name'; Value: {'win':, 'lose':, 'draw':} of team1
    match_dict = dict()
    # Team dictionary: key: 'team'; Value: {'win':, 'lose':, 'draw':}
    team_dict = dict()

    for row in raw_matches_list[:-10]:
        if ('West' in row[2]) or ('East' in row[2]) or ('West' in row[5]) or ('East' in row[5]):
            continue

        team_1 = {'name': row[2], 'goal': int(row[3])}
        team_2 = {'name': row[5], 'goal': int(row[4])}

        if team_1['name'] not in team_dict:
            team_dict[team_1['name']] = {'win': 0, 'lose': 0, 'draw': 0}

        if team_2['name'] not in team_dict:
            team_dict[team_2['name']] = {'win': 0, 'lose': 0, 'draw': 0}

        if team_1['goal'] > team_2['goal']:
            team_dict[team_1['name']]['win'] += 1
            team_dict[team_2['name']]['lose'] += 1
        elif team_1['goal'] < team_2['goal']:
            team_dict[team_1['name']]['lose'] += 1
            team_dict[team_2['name']]['win'] += 1
        else:
            team_dict[team_1['name']]['draw'] += 1
            team_dict[team_2['name']]['draw'] += 1

        if team_1['name'] > team_2['goal']:
            teams_key = team_1['name'] + ':' + team_2['name']
            if teams_key not in match_dict:
                match_dict[teams_key] = {'win': 0, 'lose': 0, 'draw': 0}

            if team_1['goal'] > team_2['goal']:
                # team 1 wins
                match_dict[teams_key]['win'] += 1
            elif team_1['goal'] < team_2['goal']:
                # team 1 loses
                match_dict[teams_key]['lose'] += 1
            else:
                match_dict[teams_key]['draw'] += 1
        else:
            teams_key = team_2['name'] + ':' + team_1['name']
            if teams_key not in match_dict:
                match_dict[teams_key] = {'win': 0, 'lose': 0, 'draw': 0}

            if team_1['goal'] > team_2['goal']:
                # team 2 loses
                match_dict[teams_key]['loses'] += 1
            elif team_2['goal'] < team_2['goal']:
                # team 2 wins
                match_dict[teams_key]['win'] += 1
            else:
                match_dict[teams_key]['draw'] += 1

    return match_dict, team_dict


def predict(team_a, team_b, match_dict, team_dict):
    if (team_a not in team_dict) or (team_b not in team_dict):
        print("Error: wrong team names.")
        return None, None

    # Let team_a be A, team_b be B. Laplace smoothing is applied.
    # P(A=1) denotes probability of team a not losing
    team_a_total = sum(team_dict[team_a].values())
    team_a_not_lose = team_dict[team_a]['win'] + team_dict[team_a]['draw']
    p_a = float(team_a_not_lose + 1) / float(team_a_total + 2)

    # P(B=1) denotes probability of team b not losing
    team_b_total = sum(team_dict[team_b].values())
    team_b_not_lose = team_dict[team_b]['win'] + team_dict[team_b]['draw']
    p_b = float(team_b_not_lose + 1) / float(team_b_total + 2)

    match_name = ':'.join(sorted([team_a, team_b]))
    if match_name in match_dict:
        # P(A=1 | A,B), P(B=1 | A,B)
        if match_name.startswith(team_a):
            team_a_not_lose_in_a_b = match_dict[match_name]['win'] + match_dict[match_name]['draw'] + 3
            team_b_not_lose_in_a_b = match_dict[match_name]['lose'] + match_dict[match_name]['draw'] + 3
        else:
            team_a_not_lose_in_a_b = match_dict[match_name]['lose'] + match_dict[match_name]['draw'] + 3
            team_b_not_lose_in_a_b = match_dict[match_name]['win'] + match_dict[match_name]['draw'] + 3

        # P(A=1 | A,B) / P(B=1 | A,B)
        prob = team_a_not_lose_in_a_b * p_b / (team_b_not_lose_in_a_b * p_a)
    else:
        # Assume P(A,B | A=1) = P(A,B | B=1)
        prob = p_a / p_b

    # print(prob)

    if prob <= 1.0:
        return 'l', prob
    else:
        return 'w', prob


def test():
    test_size = 10
    raw_match_data = get_data('raw_matches.csv')
    match_dictionary, team_dictionary = data_preprocess(raw_match_data)
    correct = 0
    for row in raw_match_data[-10:]:
        team_1 = row[2]
        team_2 = row[5]
        team_1_goal = int(row[3])
        team_2_goal = int(row[4])

        if team_1_goal > team_2_goal:
            result = 'w'
        elif team_1_goal < team_2_goal:
            result = 'l'
        else:
            result = 'd'

        prediction, prob = predict(team_1, team_2, match_dictionary, team_dictionary)

        if not prediction:
            test_size -= 1
        elif result == prediction:
            correct += 1
        else:
            print('Prediction: {0}, Prob: {1}, Team 1: {2}, Team 2: {3}, Goal: {4}:{5}.'.format(prediction, prob, team_1,
                                                                                                team_2, team_1_goal, team_2_goal))

    print("Accuracy: {0}".format(float(correct) / float(test_size)))


def predict_two_team(team_1, team_2):
    raw_match_data = get_data('raw_matches.csv')
    match_dictionary, team_dictionary = data_preprocess(raw_match_data)
    prediction, prob = predict(team_1, team_2, match_dictionary, team_dictionary)
    print(prediction)


if __name__ == '__main__':
    test()
    predict_two_team('United States', 'Portugal')