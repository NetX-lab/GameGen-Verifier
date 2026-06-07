# Run Outputs

Per-game evaluation outputs are written here by the harness drivers:

- `harness/run_normal_eval.py`
  -> `runs/<game>/<run_id>/{summary_report.md, evaluation_report.md, keypoint_<id>/result.json, keypoint_<id>/screenshots/}`
- `harness/run_recheck_eval.py`
  -> `runs/<game>/<run_id>/{recheck_summary.md, recheck_comparison.json, keypoint_<id>/recheck_result.json}`

This directory is ignored by git except for this README.
