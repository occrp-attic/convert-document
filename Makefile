
all: image run

image:
	docker build --rm -t alephdata/unoservice .

run:
	docker run -p 3000:3000 --rm --mount type=tmpfs,destination=/tmp -ti alephdata/unoservice

push:
	docker push alephdata/unoservice