all: CallTrace example

CallTrace: CallTrace.hs
	ghc --make CallTrace

example: example.c instrument.c
	gcc -g -finstrument-functions -o example example.c instrument.c

run: CallTrace example
	./example | ./CallTrace example

clean:
	rm -f example
	rm -f CallTrace CallTrace.o CallTrace.hi
