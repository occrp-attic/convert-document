
A docker container environment to bundle the execution of `unoconv`,
a command-line utility that uses `LibreOffice` to convert documents 
of various types (such as Word, OpenDocument, etc.) to PDF.

An instance of `LibreOffice` will be run in the background, and used
by multiple requestors to perform the necessary conversions.

To build, run:

```shell
$ docker build --rm -t unoconv .
```

To start the container, run:

```shell
docker run -p 3000:3000 --mount type=tmpfs,destination=/tmp -ti unoconv
```

Now, files can be sent to the service:

```shell
curl -o out.pdf -F format=pdf -F 'file=@mydoc.doc' http://localhost:3000/convert
```