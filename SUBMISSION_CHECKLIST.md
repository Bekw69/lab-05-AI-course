# Lab 05 submission checks

The submitted measurements use the original `Qwen/Qwen2.5-3B-Instruct` on a Colab Tesla T4, float16, greedy decoding. The original toolbox is unchanged. Earlier local CPU trials are excluded from the submitted results.

- [x] Forecasts retained from before the corresponding experiments; prior exposure to the README reference run and AI assistance disclosed.
- [x] All 29 code cells executed, outputs saved, no unhandled error outputs.
- [x] All eight pencil answers filled at their original locations, with readable Markdown copies beside them.
- [x] Three loop TODOs implemented; real-model `check_loop` reports all three matches.
- [x] The bare loop's alias error demonstrated and explained.
- [x] Workflow and agent compared on the same 15 fixed-shape questions, including accuracy, calls, tokens, time, disagreements and the open-question limitation.
- [x] Layers compared using all three outcomes, Wilson intervals and actual traces; overlapping intervals do not establish an accuracy winner.
- [x] Procedural notes pass the leak check; measured gains, regressions and costs explained.
- [x] All four extension experiments have saved outputs and written interpretations next to them.
- [x] Raw results, exact model revision and runtime versions saved in `results/runs.json`. Budget 5 explicitly reuses the identical Part 3 layer-2 run.
- [x] Nine unit tests pass; 255 question/configuration records checked against the dataset, tool outputs and scoring.
- [x] Conclusion uses measured values and keeps the three question headings; each answer has 80-200 words.
- [ ] **Unaided conclusion requirement:** the user requested an AI-written draft. `CONCLUSION.md` explicitly declares Codex assistance, so it does not satisfy the assignment's no-AI rule. No unaided-authorship declaration is made. This can affect the six points assigned to that file.
- [x] Template discrepancy handled: the actual dataset has 24 questions, although the conclusion template mentions 20.

`python verify_submission.py` reports the unaided-writing requirement as pending. `python verify_submission.py --require-complete` deliberately fails while that requirement remains unmet. Passing technical checks is not a guarantee of a particular grade.
