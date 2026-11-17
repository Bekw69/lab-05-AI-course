# Lab 05 — Conclusion

AI-use declaration: Codex drafted this file from the notebook's measured results. This is an AI-assisted draft and does not satisfy the assignment's requirement for unaided writing.

## 1. Which layer changed your results the most?

Using the number of questions whose verdict changed, layer 1 changed this batch the most: 4 questions changed outcome. The counts before and after were 16 / 4 / 4 and 18 / 6 / 0, out of 24. I would assess all three counts together, because replacing a stopped run with a wrong answer is not a reliability improvement. Error recovery can let the same model use tools again, but it does not improve its weights or guarantee a correct interpretation. Grounding has a different role: it can refuse an unsupported reply, and sometimes a repair message leads to a correction. These effects concern the model's available interaction and what the system accepts as an answer. The Wilson intervals in this notebook overlap, so I would not call the small observed accuracy changes a proven population improvement.

## 2. One failure the full harness did not fix

Question q08 remained wrong under layer 3: its answer was 'Jambyl'. After compare_regions returned its ordered rows, the model selected the wrong region for the requested ranking. The tool output itself was available, and the chosen name occurred in it. The grounding check therefore had evidence for the name, but no check that it was the correct endpoint of the ranking. I would add a deterministic handler for supported ranking questions: validate the indicator and year, then choose the first or last returned row according to the requested order. That adds ordinary code, tests and maintenance rather than another model-based opinion. It still needs parameter validation, because selecting the correct endpoint of a ranking for the wrong indicator or year would also produce a convincing wrong answer.

## 3. Workflow or agent for the monthly ranking?

I would ship a fixed workflow for the monthly highest-and-lowest brief because its shape is known in advance. On the 15 fixed-shape questions, workflow was correct on 13/15 and the bare agent on 9/15. Workflow used 15 calls, 3852 tokens and 16.6 seconds; agent used 26 calls, 19835 tokens and 75.3 seconds. Those measurements favor the workflow's observed cost, although the overlapping accuracy intervals do not prove a general accuracy winner. For the monthly task I would extend the deterministic template to report both ends of the same ranking, and send invalid parameters or missing data for review. The timings are benchmark measurements, not a guarantee for every monthly request. I would choose the agent for an open question requiring adaptive tool selection or several dependent steps that the fixed workflow cannot represent.

---

This file was drafted with AI assistance (Codex).
