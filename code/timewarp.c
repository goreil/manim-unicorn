int main(){
    int a = ret1();
    int b = ret2();
    if (a == b){
        win();
    }
    return 0;
}
int ret1(){
    return 10;
}
int ret2(){
    return 30;
}
void win();