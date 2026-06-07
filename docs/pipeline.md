# Experiment Pipeline

The full pipeline has five stages:

1. Add task descriptions to `descriptions_example/`.
2. Generate evaluation-enabled games in `games/`.
3. Distill keypoints into `games/<game>/keypoints.md`.
4. Export hook-stripped copies into `games_clean/` (evaluation adapter removed).
5. Run normal evaluation + recheck (Ours) and the parallel-vs-sequential
   ablation.

Useful entrypoints:

```bash
python3 scripts/prepare/generate_games.py --games <game_name>
python3 scripts/prepare/distill_keypoints.py --games <game_name>
python3 scripts/prepare/export_clean_games.py --games <game_name> --force
python3 harness/run_normal_eval.py --workspace "$(pwd)" --game-name <game_name> --run-id <run_id>
python3 harness/run_recheck_eval.py --workspace "$(pwd)" --game-name <game_name> --run-id <run_id>
python3 scripts/ablation/parallel_keypoints.py --games <game_name> --repeats 3
python3 scripts/run_all_experiments.py --games <game_name> [<game_name> ...]
```

For local sanity checks:

```bash
python3 -m unittest discover -s tests
python3 scripts/run_all_experiments.py --smoke
```
