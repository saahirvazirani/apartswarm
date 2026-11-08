# Recompute every number and figure in the paper from runs/ (CLAUDE.md rule 10).
PY := .venv/bin/python
STAGE1 := $(wildcard runs/stage1_*/scores.jsonl)

.PHONY: recompute cheap3 full budget hashes

recompute: hashes cheap3 full budget

hashes:
	$(PY) -c "import json,hashlib,pathlib; h=json.load(open('prompts/HASHES.json')); \
	bad=[n for n,v in h.items() if hashlib.sha256(pathlib.Path(f'prompts/{n}.txt').read_text(encoding='utf-8').strip().encode()).hexdigest()!=v]; \
	print('prompt hashes OK' if not bad else f'HASH MISMATCH: {bad}')"

cheap3:
	@if [ -f runs/stage1_monA/scores.jsonl ]; then \
	  $(PY) analysis/calibrate.py --scores runs/stage1_monA/scores.jsonl --out analysis/out/cheap3 && \
	  $(PY) analysis/fit.py --scores runs/stage1_monA/scores.jsonl --out analysis/out/cheap3 --perms 2000; fi

full:
	@if [ -n "$(STAGE1)" ]; then \
	  $(PY) analysis/calibrate.py --scores $(STAGE1) --out analysis/out/full && \
	  $(PY) analysis/fit.py --scores $(STAGE1) --out analysis/out/full --perms 2000; fi

budget:
	PYTHONPATH=src $(PY) -m track_a.budget
