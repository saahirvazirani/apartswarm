# Recompute every number and figure in the paper from runs/ (CLAUDE.md rule 10).
PY := .venv/bin/python
STAGE1 := $(wildcard runs/stage1_*/scores.jsonl)
STAGE1B := $(wildcard runs/stage1b_*/scores.jsonl)
STAGE1C := $(wildcard runs/stage1c_*/scores.jsonl)
RAW := $(wildcard runs/stage1raw_*/scores.jsonl)
BANKS := runs/bank_cheap3_v2 runs/bank_rest4

.PHONY: recompute hashes banks full robustness figure excerpts told para raw strengthen control budget

recompute: hashes banks full robustness figure excerpts told para raw strengthen control budget

hashes:
	$(PY) -c "import json,hashlib,pathlib; h=json.load(open('prompts/HASHES.json')); \
	bad=[n for n,v in h.items() if hashlib.sha256(pathlib.Path(f'prompts/{n}.txt').read_text(encoding='utf-8').strip().encode()).hexdigest()!=v]; \
	print('prompt hashes OK' if not bad else f'HASH MISMATCH: {bad}')"

banks:
	$(PY) analysis/bank_tables.py --banks $(BANKS) --out analysis/out/banks > /dev/null && echo "banks -> analysis/out/banks"

full:
	@if [ -n "$(STAGE1)" ]; then \
	  $(PY) analysis/calibrate.py --scores $(STAGE1) --out analysis/out/full > /dev/null && \
	  $(PY) analysis/fit.py --scores $(STAGE1) --out analysis/out/full --perms 2000 2>/dev/null > /dev/null && echo "full -> analysis/out/full"; fi

robustness:
	@if [ -n "$(STAGE1)" ]; then $(PY) analysis/robustness.py --scores $(STAGE1) --out analysis/out/full 2>/dev/null > /dev/null && echo "robustness -> analysis/out/full/robustness.md"; fi

figure:
	@if [ -f analysis/out/full/fit.json ]; then $(PY) analysis/figures.py --cells analysis/out/full/cells.csv --fit analysis/out/full/fit.json --out analysis/out/full/fig1.png \
	  --title "Catch rate of successful attacks, blind monitors (34 tasks, 650 attacks, 698 benign)"; fi

excerpts:
	@if [ -f analysis/out/full/cells.csv ]; then $(PY) analysis/excerpts.py --scores $(STAGE1) --cells analysis/out/full/cells.csv --banks $(BANKS) --out analysis/out/full/excerpts.md --n 3 > /dev/null && echo "excerpts -> analysis/out/full/excerpts.md"; fi

told:
	@if [ -n "$(STAGE1B)" ]; then $(PY) analysis/deltas.py told --blind $(STAGE1) --told $(STAGE1B) --out analysis/out/told > /dev/null && echo "told -> analysis/out/told/deltas.md"; fi

para:
	@if [ -n "$(STAGE1C)" ]; then $(PY) analysis/deltas.py para --orig $(STAGE1) --para $(STAGE1C) --out analysis/out/para > /dev/null && echo "para -> analysis/out/para/deltas.md"; fi

raw:
	@if [ -n "$(RAW)" ]; then \
	  $(PY) analysis/calibrate.py --scores $(STAGE1) $(RAW) --attack-stage raw --out analysis/out/raw > /dev/null && \
	  $(PY) analysis/fit.py --scores $(STAGE1) $(RAW) --attack-stage raw --out analysis/out/raw --perms 2000 2>/dev/null > /dev/null && \
	  $(PY) analysis/robustness.py --scores $(STAGE1) $(RAW) --attack-stage raw --out analysis/out/raw 2>/dev/null > /dev/null && echo "raw (pre-polish attacks) -> analysis/out/raw"; fi

strengthen:
	@if [ -n "$(STAGE1)" ]; then $(PY) analysis/strengthen.py --scores $(STAGE1) --banks $(BANKS) --out analysis/out/strengthen --boots 500 2>/dev/null > /dev/null && echo "strengthen -> analysis/out/strengthen/strengthen.md, fig2_residuals.png"; fi

control:
	@if [ -n "$(STAGE1)" ]; then $(PY) analysis/control.py --scores $(STAGE1) --out analysis/out/control 2>/dev/null > /dev/null && echo "control -> analysis/out/control/control.md, fig3_audit_budget.png"; fi

budget:
	PYTHONPATH=src $(PY) -m track_a.budget | head -1
