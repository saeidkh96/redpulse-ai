from app.mlops.champion import ChampionChallengerEngine, ModelEvaluation


def test_challenger_can_win():
    engine = ChampionChallengerEngine()
    champion = ModelEvaluation("1", 0.8, 0.8, 0.2, 0.7, 0.7)
    challenger = ModelEvaluation("2", 0.9, 0.9, 0.1, 0.8, 0.8)
    result = engine.compare(champion, challenger)
    assert result.challenger_won is True
    assert result.winner_version == "2"
