# 暴力，整理成点积的形式
class Solution:
    def minTime(self, a: List[int], b: List[int]) -> int:
        n=len(a); m=len(b); s=sum(a); a.append(0)
        u=[0]*(n+1); v=[0]*(n+1)
        for i in range(0,n): u[i]=u[i-1]+a[i-1]
        for i in range(n-2,-1,-1): v[i]=v[i+1]+a[i+1]
        sta=0
        for i in range(1,m):
            d=1e20; u1=b[i]; v1=b[i-1]
            end=sta+v1*s
            for j in range(n):
                d=min(d,v[j]*v1+u[j]*u1)
            sta=end-d
        return sta+b[m-1]*s
