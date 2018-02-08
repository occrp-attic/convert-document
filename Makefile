
all: image run

image:
	docker build --rm -t alephdata/unoservice .

run:
	docker run -p 5002:3000 --rm --mount type=tmpfs,destination=/tmp -ti alephdata/unoservice

shell:
	docker run -ti alephdata/unoservice /bin/bash

push:
	docker push alephdata/unoservice
