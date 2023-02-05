#include <stdio.h>

int main(){
    int a;
    printf("%d\n", 1);
    while(1){
        scanf("%d\n", &a);
        fprintf(stderr, "%d\n", a);
        printf("%d\n", a+1);
    }
}