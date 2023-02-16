#include <iostream>
#include <string>
#include <cmath>

using namespace std;

int main ()
{
    string W, H, N, S, trash;
    cin >> W >> H >> N >> S;

    int i = 0;
    while (1)
    {
        if (i%stoi(N)+1 == stoi(S))
        {
            cout << 0 << endl;
        }
        else
        {
            cin >> trash;
        }

        i++;
    }

    return 0;
}
