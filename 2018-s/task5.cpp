/*
这一题就明显能看出来c++的优势了, 对于这种不涉及太多计算,
主要是按照题意模拟的题用C++ 速度快很多,大概十几秒就跑出来结果,

tomfluff的py代码有比较明显的bug，每个聚类的初始元素就求错了，但是它第四问的结果是对的，而且在迭代
过程里，题意是只在每个聚类内寻找距离重心最近的点，而他的代码是遍历所有的点，而且在求重心过程里
他没用floor函数，这也可能导致不同。还有楼上的py代码在对每个点找归属的类时忘记判断等距离情况，
我调了半天才发现这个bug，在修改了上述bug后，用改进的py代码跑出来的结果跟我的c++结果相同。

image2.txt得到的结果是:
p(i=40): (98 98 98) , index 1639792
p(i=80): (137 137 137) , index 1639595
p(i=120): (181 181 181) , index 1639802

image3.txt得到的结果是:
p(i=2): (29 34 50) , index 1061557
p(i=4): (52 66 101) , index 1040155
p(i=6): (83 142 207) , index 327456

*/
#include <bits/stdc++.h>
#define int long long
#define tii tuple<int, int, int>
using namespace std;
struct Node {
    int a, b, c, val, id;
};
bool cmp(Node a, Node b) {
    if (a.val != b.val)
        return a.val < b.val;
    else
        return a.id > b.id;
}
int cal(int a, int b, int c) {
    return a * a + b * b + c * c;
}
int dis(Node a, Node b) {
    return abs(a.a - b.a) + abs(a.b - b.b) + abs(a.c - b.c);
}
void solve() {
    ifstream fin("E:/UTokyo_Entrance_Exam/CI/2019_summer/image3.txt", ios::in);
    ofstream fout("E:/UTokyo_Entrance_Exam/CI/2019_summer/ans53.txt", ios::out);
    vector<tii> vec;
    int num1, num2, num3;
    vector<Node> vec2;
    int cnt = 0;
    while (fin >> num1 >> num2 >> num3) {
        vec.push_back({num1, num2, num3});
        vec2.push_back(Node{num1, num2, num3, cal(num1, num2, num3), cnt++});
    }
    sort(vec2.begin(), vec2.end(), cmp);
    int n = vec2.size(), k = 8;
    vector<Node> repre(k); // k个代表元素
    vector<int> is_repre(n);
    for (int i = 0; i < k; i++) {
        Node ei = vec2[n * i / k];
        repre[i] = ei;
        is_repre[ei.id] = 1;
    }
    for (int repeat = 1; repeat <= 10; repeat++) {
        vector<vector<Node>> group;
        group.resize(k); // 开 k 个vector, 存每个group里面有哪些三元组
        for (int i = 0; i < k; i++)
            group[i].push_back(repre[i]); //先把代表元素放进去
        // 枚举三元组, 遍历找最近的聚类
        for (int i = 0; i < n; i++) {
            Node now = vec2[i];
            if (is_repre[now.id]) continue; // 去掉代表元素
            int i_bel = 0; // 当前元素属于的聚类编号
            for (int j = 1; j < k; j++) {
                if (dis(now, repre[j]) < dis(now, repre[i_bel]) 
                || dis(now, repre[j]) == dis(now, repre[i_bel]) && repre[j].id > repre[i_bel].id) {
                    // 距离更近或者距离相同编号更大
                    i_bel = j;
                }
            }
            group[i_bel].push_back(now);
        }
        // 重新算每个聚类里的代表元素
        for (int i = 0; i < k; i++) {
            Node centroid = Node{0, 0, 0, 0, 0}; // 每个聚类的重心
            for (auto [a, b, c, val, id] : group[i]) {
                centroid.a += a, centroid.b += b, centroid.c += c;
            }
            // c++整形默认向下整除, 也可以用浮点数再floor取整, 可能还得加个eps
            centroid.a /= group[i].size(), centroid.b /= group[i].size(), centroid.c /= group[i].size();
            // 找组里离重心最近的作为新的代表元素
            Node newrepre = repre[i];
            for (auto it : group[i]) {
                if (dis(it, centroid) < dis(newrepre, centroid) ||
                dis(it, centroid) == dis(newrepre, centroid) && it.id > newrepre.id) {
                    newrepre = it;
                }
            }
            is_repre[repre[i].id] = 0;
            repre[i] = newrepre;
            is_repre[repre[i].id] = 1;
        }
    }
    for (auto id : {2, 4, 6}) {
        fout << "p(i=" << id << "): (" << repre[id].a << " " << repre[id].b
             << " " << repre[id].c << ") , index " << repre[id].id << "\n";
    }
}
signed main() {
    ios::sync_with_stdio(0), cin.tie(0), cout.tie(0);
    int t = 1;
    // cin >> t;
    while (t--)
        solve();
    return 0;
}