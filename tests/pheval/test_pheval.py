from mathematics_of_poker.phevaluator import evaluator


def test_royal_flush_beats_pair():
    hero = ["Ah", "Kh"]
    villain = ["As", "Ad"]
    board = ["Qh", "Jh", "Th", "2c", "3d"]

    hero_score = evaluator.evaluate_cards(*(hero + board))
    villain_score = evaluator.evaluate_cards(*(villain + board))

    assert hero_score < villain_score
