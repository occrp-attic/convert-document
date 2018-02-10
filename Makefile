
all: image run

image:
	docker build --rm -t alephdata/unoservice .

run:
	docker run -p 5002:3000 --memory=1g --rm --mount type=tmpfs,destination=/tmp --mount type=tmpfs,destination=/root/.config -ti alephdata/unoservice

shell:
	docker run -ti alephdata/unoservice /bin/bash

push:
	docker push alephdata/unoservice
