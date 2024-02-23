build:
	docker build -t kavak-bot .

run:
	docker run -v "$(PWD)":/usr/src/app -it kavak-bot

run-windows:
	docker run -v "%cd%":/usr/src/app -it kavak-bot