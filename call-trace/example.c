int fib(int n)
{
    if (n < 2)
        return 1;
    return fib(n - 2) + fib(n - 1);
}

int main()
{
    fib(7);
    return 0;
}
