/* see http://www.ibm.com/developerworks/library/l-graphvis/ */

#include <stdio.h>

/* TODO don't mess stdout, output to named pipe */

#if 0

static FILE *fp;

void open_fp() __attribute__ ((constructor, no_instrument_function));

void close_fp() __attribute__ ((destructor, no_instrument_function));

void open_fp() { }

void close_fp() { }

#endif

void __cyg_profile_func_exit(void *, void *) __attribute__ ((no_instrument_function));

void __cyg_profile_func_enter(void *, void *) __attribute__ ((no_instrument_function));

void __cyg_profile_func_enter(void *this, void *callsite)
{
  fprintf(stdout, "JumpEvent Call %p %p\n", this, callsite);
}

void __cyg_profile_func_exit(void *this, void *callsite)
{
  fprintf(stdout, "JumpEvent Return %p %p\n", this, callsite);
}
