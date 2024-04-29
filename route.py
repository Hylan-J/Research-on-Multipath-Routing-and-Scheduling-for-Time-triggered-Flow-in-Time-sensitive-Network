from copy import deepcopy

import networkx as nx
from typing import List

from Objects.Flow import Flow
from utils import *
from config import *


def find_NRSs(flow: Flow, routes: List[list], length_target: int):
    """
    根据链路长度，寻找一个流量的除去起始与终止链路的所有路由的不相交路径
    """
    # 首先找到对应的长度的路由
    routes_target = []
    for route in routes:
        if len(route) == length_target:
            routes_target.append(route)

    # 如果路由个数小于流量的冗余等级，那么不可能存在NRS，返回 None
    if len(routes_target) < flow.redundancy_level:
        return []
    # 如果路由个数大于等于流量的冗余等级，那么可能存在NRS，寻找不相交的路由
    else:
        routes_target_copy = deepcopy(routes_target)
        # 将每个合适的路由的开始与结束链路移除
        for route in routes_target_copy:
            # 移除开始链路
            route.remove(route[0])
            # 移除结束链路
            route.remove(route[-1])

        NRSs = []
        for i in range(len(routes_target_copy) - 1):
            for j in range(i + 1, len(routes_target_copy)):
                # 假设不相交
                disjoint = True
                # 因为除去了开始和结束的链路，所以减2
                for k in range(length_target - 2):
                    if routes_target_copy[i][k] == routes_target_copy[j][k]:
                        disjoint = False
                # 如果没有相交链路
                if disjoint:
                    NRSs.append([routes_target[i], routes_target[j]])
        return NRSs


def candidate_routing_sets_filtering(network, flows, p_th):
    """
    候选路由集筛选算法
    : parm network: 网络对象
    : parm flows: 所有流量对象的集合
    : parm p_th: 概率阈值, 使用该阈值对路由进行筛选
    """
    candidate_routing_sets = []
    for flow in flows:
        routes = []
        routes_length = []
        # nx.all_simple_paths(network.G, flow.src, flow.dst)返回示例：[[A,B,C,D], [A,C,B,D]]
        for path in list(nx.all_simple_paths(network.G, flow.src, flow.dst)):
            route = []
            for i in range(len(path) - 1):
                route.append([path[i], path[i + 1]])
            routes.append(route)
            routes_length.append(len(route))
        # routes示例：[[[A,B],[B,C],[C,D]], [[A,C],[C,B],[B,D]]]

        # 最短 NRS 长度
        length_min = min(routes_length)
        # 最长 NRS 长度
        length_max = max(routes_length)

        length = length_min
        temp = 0

        U = []
        while temp != 2:
            if length > length_max:
                break
            else:
                # NRSs示例:[[route,route], [route,route]], 每个list中都是一个路径对
                NRSs = find_NRSs(flow, routes, length)
                # 如果找不到对应长度的NRS
                if not NRSs:
                    # 长度+1继续找
                    length += 1
                    continue
                # 如果能找到对应长度的NRS
                else:
                    for NRS in NRSs:
                        # 针对每个NRS组，计算其概率
                        p_m = cal_probability(NRS, unreliable_edges, p_r, p_ur)
                        #
                        if p_m < p_th:
                            NRSs.remove(NRS)
                    # 如果存在能正确接收到数据帧的NRS
                    if NRSs:
                        for NRS in NRSs:
                            U.append(NRS)
                    else:
                        temp += 1
                    length += 1
        candidate_routing_sets.append(U)

    return candidate_routing_sets


########################################################################################################################
# 元启发式群智能算法：蚁狮算法
# -------------------------------------------------------------------------------------------------------------------- #
def ALO(candidate_routes, si, pr, max_iterations):
    """
    蚁狮优化算法（ant_lion_optimization，ALO）
    """

    def objective_1(route, si, pr):
        """
        目标函数1
        : parm p: 候选路由集
        : parm si: 帧大小
        : parm pr: 帧周期
        """
        D = []
        num_flow = len(si)

        for i in range(num_flow - 1):
            for j in range(i + 1, num_flow):
                # 获取两个流的帧大小
                si_i, si_j = si[i], si[j]
                # 获取两个流的帧周期
                pr_i, pr_j = pr[i], pr[j]
                # 获取两个流的NRSs
                p_i, p_j = route[i], route[j]

                temp = 0
                for NRS_i in p_i:
                    for NRS_ii in NRS_i:
                        for NRS_j in p_j:
                            if NRS_ii in NRS_j:
                                temp += 1

                D.append(temp * (si_i * si_j) / (pr_i * pr_j))

        return sum(D)

    def objective_2(routes, si):
        """
        目标函数2
        : parm p: 候选路由集
        : parm si: 帧大小
        """
        T = []
        num_flow = len(si)

        for i in range(num_flow):
            NRS = routes[i]
            temp = 0
            for _NRS_ in NRS:
                temp += len(_NRS_)
            # 计算传输延时（μs）
            t_proc = 4 * temp
            # 计算发送延时
            # _si_ = si[i]
            # t_tran= 100*1000/
            T.append(t_proc)

        return -sum(T)

    def cost(current_routes, si, pr):
        """
        成本函数
        : parm p: 当前候选路由集
        : parm si: 帧大小
        : parm pr: 帧周期
        """
        W1 = 1000
        W2 = 1
        objective_1_value = objective_1(current_routes, si, pr)
        objective_2_value = objective_2(current_routes, si)
        # 适应度计算
        fitness = W1 * objective_1_value + W2 * objective_2_value
        return fitness

    def init_population(num, candidate_routes):
        """
        随机生成初始解
        : parm num_solutions: 需要生成的初始解的个数
        : parm candidate_routing_sets: 候选路由集
        """
        init_routes = []
        for _ in range(num):
            random_routes = []
            for i in range(num_flows):
                # 获取第i个流量的U（即多组NRS）
                U = candidate_routes[i]
                # 从U（即多组NRS）中随机挑选一组NRS
                random_routes.append(random.choice(U))
            init_routes.append(random_routes)
        return init_routes

    # 蚂蚁和蚁狮的数量根据搜索空间的大小确定，近似于在网络中路由的流的数目。
    num_flows = len(si)
    num_ants = num_flows
    num_antlions = num_flows

    ####################################################################################################################
    # 步骤1：随机生成一系列初始解，作为蚂蚁和蚁狮的初始种群
    # ---------------------------------------------------------------------------------------------------------------- #
    ants = init_population(num_ants, candidate_routes)
    antlions = init_population(num_antlions, candidate_routes)

    ####################################################################################################################
    # 步骤2：拥有最高适应度，即最小成本函数的路由组合成为初始精英蚁狮
    # ---------------------------------------------------------------------------------------------------------------- #
    ants_antlions_fitness = []
    for i in range(num_ants):
        ants_antlions_fitness.append(cost(ants[i], si, pr))
    for i in range(num_antlions):
        ants_antlions_fitness.append(cost(antlions[i], si, pr))

    min_index = ants_antlions_fitness.index(min(ants_antlions_fitness))
    if 0 <= min_index <= num_ants - 1:
        elite = ants[min_index]
    else:
        elite = antlions[min_index - num_ants]

    # 计算所有蚁狮的适应度（轮盘赌策略备用）
    antlions_fitness = [cost(antlions[i], si, pr) for i in range(num_antlions)]

    # 迭代
    for _ in range(max_iterations):
        ################################################################################################################
        # 步骤 3：通过轮盘赌策略（Roulette Wheel）为每个蚂蚁选择一个相应的蚁狮
        # 步骤 4：模拟蚁狮和陷阱中蚂蚁的相互作用，更新蚂蚁位置
        # ------------------------------------------------------------------------------------------------------------ #
        antlions_index = [i for i in range(num_antlions)]
        corresponding = [0 for _ in range(num_antlions)]
        for i in range(num_ants):
            # 通过轮盘赌策略为蚂蚁选择一个相应的蚁狮
            corresponding[i] = random.choices(antlions_index, weights=antlions_fitness, k=1)

        ################################################################################################################
        # 步骤 5：更新蚁狮种群
        # ------------------------------------------------------------------------------------------------------------ #
        for i in range(num_ants):
            # 如果蚂蚁的成本小于其蚁狮，那么该蚂蚁将取代原蚁狮，成为新蚁狮种群中的一员
            if cost(ants[i], si, pr) < cost(antlions[corresponding[i]], si, pr):
                temp = ants[i]
                ants[i] = antlions[corresponding[i]]
                antlions[corresponding[i]] = temp

        ################################################################################################################
        # 步骤 6：计算蚁狮种群中所有路由组合的成本函数，取最小的路由组合作为新的精英蚁狮elite
        # ------------------------------------------------------------------------------------------------------------ #
        # 计算更新后的蚁狮种群适应度
        antlions_fitness = [cost(antlions[i], si, pr) for i in range(num_antlions)]
        # 如果更新后的最小蚁狮种群适应度小于当前精英蚁狮适应度
        if min(antlions_fitness) < cost(elite, si, pr):
            min_index = antlions_fitness.index(min(antlions_fitness))
            elite = antlions[min_index]

    return elite
