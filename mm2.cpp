//mm2.cpp

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void populate(char **str) {
	// 1. OK (mm1.cpp)
	*str = (char *)malloc(sizeof(char) * 7);
	strcpy(*str, "Memory");
}

int main() {
	char *s;
	populate(&s);
	printf("%s", s);   // should print "Memory"
	free(s);
	return 0;
}