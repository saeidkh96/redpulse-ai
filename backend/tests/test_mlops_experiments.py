from app.mlops.experiments import ExperimentRun, ExperimentTracker


def test_experiment_tracker_persists_runs(tmp_path):
    tracker = ExperimentTracker(tmp_path / "experiments.json")
    run = tracker.log_run(ExperimentRun("failure-model", metrics={"f1": 0.88}))
    assert tracker.list_runs("failure-model")[0].run_id == run.run_id
