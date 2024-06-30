int ret1(){
    return 1;
}
int ret0(){
    return 0;
}
int main(){
    int a = ret1();
    int b = ret0();
    if (a == b){
        puts("WIN!");
    }
    return 0;
}