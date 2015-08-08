SRC=libboltek.c st2sf.c
OBJ=libboltek.o libboltek.a libboltek.so st2sf

.PHONY: all
all: $(OBJ)

$(OBJ): $(SRC) Makefile
	gcc  -g -Wall -fPIC -c  libboltek.c
	gcc -shared -Wl,-soname,libboltek.so -o libboltek.so libboltek.o 
	ar r libboltek.a libboltek.o
	gcc -g -o st2sf st2sf.c libboltek.a -lm

.PHONY: clean
clean:
	rm  -f $(OBJ)
