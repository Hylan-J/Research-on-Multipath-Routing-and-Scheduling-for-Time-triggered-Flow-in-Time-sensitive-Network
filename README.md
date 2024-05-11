# Research-on-Multipath-Routing-and-Scheduling-for-Time-triggered-Flow-in-Time-sensitive-Network

论文《面向时间敏感网络的时间触发流多路径路由和调度研究》[https://kns.cnki.net/kcms2/article/abstract?v=HiJCKhV2ch5YwUlc3KbmTJiHJgay3BwEJBlgnDIaOBwtgxS2v5yf2A0Msh5LBVBIfPcdQfxBdnig0_QAp-b29Kix4IfF_JZm0bC-sEIKoKGb4GnmfxkSD-mULahbEdm_VMl0AaedyuqkKQ3nzZdhPg==&uniplatform=NZKPT&language=CHS]的python实现，ILP通过gurobipy库实现

## 部分重要实现说明

### 蚁狮算法求解路由部分
![image](https://github.com/Hylan-J/Research-on-Multipath-Routing-and-Scheduling-for-Time-triggered-Flow-in-Time-sensitive-Network/assets/77910684/a9ac97c9-fae5-4b02-8025-8828a53eba30)

步骤4的**随机游走**实现过程：

①判断所有蚂蚁ants与蚁狮$antlion_i$（其中一只蚂蚁$ant_i$对应，步骤3实现）是否有相交NRSs，如果有的话，则指定该蚂蚁为对应蚁狮的周围蚂蚁

②蚂蚁在蚁狮周边的随机游走过程定义为其与蚁狮进行路径交换的过程，将周围蚂蚁的游走（即路径交换）过程记录下来

③如果有周围蚂蚁的游走记录，根据所有记录更新$ant_i$的路径；如果没有周围蚂蚁的游走记录，那么$ant_i$的每一组NRS按照随机概率与对应的蚁狮$antlion_i$对应的NRS交换

### 无等待调度部分实现
将避免竞争约束（Contention-free Constraints）【论文公式4.6、4.7】结合其对应的二元互斥变量，转化为如下公式：

$$\Phi_{s_i}(m,l)+\Phi_{s_j}(n,l)+a\cdot(T_c\cdot w_{s_i}-2\Phi_{s_j}(n,l))+b\cdot(T_c\cdot w_{s_j}-2\Phi_{s_i}(m,l))$$
