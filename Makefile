.PHONY: install test generate baseline extreme gpu-cpu docs
install:
	python -m pip install -e '.[dev]'
test:
	pytest -q
generate:
	music-lab generate
	python -m music_lab.generate_extreme
baseline:
	xlab ranking
extreme:
	xlab stream-sim --events 100000 --output results/stream.json
	xlab bandit-sim --output results/bandit.json
	xlab redteam-local --output results/redteam.json
gpu-cpu:
	xlab two-tower --device cpu --epochs 6 --output results/two_tower.json
