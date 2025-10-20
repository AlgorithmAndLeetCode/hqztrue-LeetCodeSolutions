typedef long long ll;
const int N=1505,L=35;
struct Interval {
    int l,p,g;
}a[L];
vector<int> pos[L];
int b[N];
class Solution {
public:
    long long maxGCDScore(vector<int>& v, int k) {
        int n=v.size(),a1=1;
        ll ans=v[0]*2;
        for (int i=0;i<L;++i)pos[i].clear();
        for (int i=0;i<n;++i)b[i]=__builtin_ctz(v[i]);
        a[0]={0,b[0],v[0]};
        pos[b[0]].push_back(0);
        for (int r=1;r<n;++r) {
            int x=v[r],p=b[r],a2=0;
            pos[p].push_back(r);
            for (int i=0;i<a1;++i){
                Interval &t=a[i];
                t.p=min(t.p,p);
                t.g=__gcd(t.g,x);
                if (!i||t.g>a[i-1].g)a[a2++]=t;
            }
            a1=a2;
            if (a[a1-1].g!=x)a[a1++]={r,p,x};
            for (int i=0;i<a1;++i){
                Interval &t=a[i];
                vector<int> &pos1=pos[t.p];
                int l0=pos1.size()>k?pos1[pos1.size()-k-1]:-1;
                if (l0<t.l)ans=max(ans,(ll)t.g*(r-t.l+1)*2);
                else {
                    ans=max(ans,(ll)t.g*(r-t.l+1));
                    ans=max(ans,(ll)t.g*(r-l0)*2);
                }
            }
        }
        return ans;
    }
};
