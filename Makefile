
all: build run

build:
	docker build --rm -t alephdata/unoservice .

run:
	docker run -p 5003:3000 --memory=1g --rm --mount type=tmpfs,destination=/tmp --mount type=tmpfs,destination=/root/.config -ti alephdata/unoservice

shell:
	docker run --rm -v $(PWD)/unoservice:/unoservice/unoservice -v $(PWD)/fixtures:/unoservice/fixtures --mount type=tmpfs,destination=/tmp --mount type=tmpfs,destination=/root/.config -ti alephdata/unoservice /bin/bash

push:
	docker push alephdata/unoservice