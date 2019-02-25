//mm1.cpp

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void populate(char **str) {
	// 1. Not OK if later freeing the memory (mm1.cpp)
	*str = "Memory";
}

int main() {
	char *s;
	populate(&s);
	printf("%s", s);   // should print "Memory"
	free(s);
	return 0;
}