#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024/4/30 2:41
# @Author  : hylan(https://github.com/Hylan-J)
# @Description :
import random

from Configs import *
from utils import *


########################################################################################################################
# 元启发式群智能算法：蚁狮算法
# -------------------------------------------------------------------------------------------------------------------- #
def ALO(candidate_flows_NRSs, sizes: list, periods: list, max_iterations: int):
    """
    蚁狮优化算法（ant_lion_optimization，ALO）
    """

    def objective_1(NRSs, sizes, periods):
        """
        目标函数1：冲突程度
        Args:
            NRSs: 所有帧的路由
            sizes: 所有帧的大小
            periods: 所有帧的周期

        Returns:

        """
        D = []
        num_flow = len(sizes)

        for i in range(num_flow - 1):
            for j in range(i + 1, num_flow):
                # 获取两个流的帧大小
                si_i, si_j = sizes[i], sizes[j]
                # 获取两个流的帧周期
                pr_i, pr_j = periods[i], periods[j]
                # 获取两个流的NRSs
                p_i, p_j = NRSs[i], NRSs[j]

                temp = 0
                for NRS_i in p_i:
                    for link_ii in NRS_i:
                        for NRS_j in p_j:
                            if link_ii in NRS_j:
                                temp += 1

                D.append(temp * (si_i * si_j) / (pr_i * pr_j))

        return sum(D)

    def objective_2(NRSs, sizes):
        """
        目标函数2：流延时
        Args:
            NRSs: 所有帧的路由
            sizes: 所有帧的大小

        Returns:

        """
        T = []
        num_flow = len(sizes)

        for i in range(num_flow):
            NRS = NRSs[i]
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

    def cost(current_NRSs, sizes, periods):
        """
        成本函数
        : parm p: 当前候选路由集
        : parm si: 帧大小
        : parm pr: 帧周期
        """
        objective_1_value = objective_1(current_NRSs, sizes, periods)
        objective_2_value = objective_2(current_NRSs, sizes)
        # 适应度计算
        fitness = W_1 * objective_1_value + W_2 * objective_2_value
        return fitness

    def init_population(num_populations: int, num_flows: int, candidate_flows_NRSs):
        """
        随机生成初始解
        Args:
            num_populations: 需要生成的初始解的个数
            num_flows: 流量的数量
            candidate_flows_NRSs: 候选路由集

        Returns:

        """
        init_flows_NRSs = []
        for _ in range(num_populations):
            candidate_flows_NRS = []
            for i in range(num_flows):
                # 获取第i个流量的U（即多组NRS）
                candidate_flow_NRSs = candidate_flows_NRSs[i]
                # 从U（即多组NRS）中随机挑选一组NRS
                candidate_flows_NRS.append(random.choice(candidate_flow_NRSs))
            init_flows_NRSs.append(candidate_flows_NRS)
        return init_flows_NRSs

    # 蚂蚁和蚁狮的数量根据搜索空间的大小确定，近似于在网络中路由的流的数目。
    num_flows = len(sizes)
    num_ants = 2 * num_flows
    num_antlions = 2 * num_flows
    flow_ids = [i for i in range(num_flows)]

    # 步骤1：随机生成一系列初始解，作为蚂蚁和蚁狮的初始种群 -------------------------------------------------------------------- #
    ants = init_population(num_ants, num_flows, candidate_flows_NRSs)
    antlions = init_population(num_antlions, num_flows, candidate_flows_NRSs)

    # 步骤2：拥有最高适应度，即最小成本函数的路由组合成为初始精英蚁狮 ------------------------------------------------------------ #
    ants_antlions_fitness = []
    for i in range(num_ants):
        ants_antlions_fitness.append(cost(ants[i], sizes, periods))
    for i in range(num_antlions):
        ants_antlions_fitness.append(cost(antlions[i], sizes, periods))

    min_index = ants_antlions_fitness.index(min(ants_antlions_fitness))
    if 0 <= min_index <= num_ants - 1:
        elite = ants[min_index]
    else:
        elite = antlions[min_index - num_ants]

    # 计算所有蚁狮的适应度（轮盘赌策略备用）
    antlions_fitness = [cost(antlions[i], sizes, periods) for i in range(num_antlions)]

    # 蚁狮种群迭代
    for _ in range(max_iterations):
        # 步骤 3：通过轮盘赌策略（Roulette Wheel）为每个蚂蚁选择一个相应的蚁狮 ------------------------------------------------- #
        antlions_index = [i for i in range(num_antlions)]
        corresponding = [0] * num_antlions
        for i in range(num_ants):
            # 通过轮盘赌策略为蚂蚁选择一个相应的蚁狮
            # 因为random.choices返回的是list，因此需要在最后增加索引
            corresponding[i] = random.choices(antlions_index, weights=antlions_fitness, k=1)[0]

        # 步骤 4：模拟蚁狮和陷阱中蚂蚁的相互作用，更新蚂蚁位置 ----------------------------------------------------------------- #
        for i in range(num_ants):
            # 获取相应的蚁狮（代表一个解）
            corresponding_antlion = antlions[corresponding[i]]

            # 和相应蚁狮一定几率交换
            # for j in range(num_flows):
            #     if random.uniform(0, 1) < 0.3:
            #         ants[i][j] = corresponding_antlion[j]

            records = []
            for j in range(num_ants):
                for k in range(num_flows):
                    # 如果蚂蚁的某条流量的路由在相应的蚁狮中，那么说明其在相应蚁狮的周围
                    if ants[j][k] in corresponding_antlion:
                        # 随机选择一条流量的路由交换（不实际交换，但存储记录）
                        records.append(random.choice(flow_ids))
            # 去重
            records = list(set(records))
            # 如果周边的蚂蚁发生过游走
            if len(records) > 0:
                for record in records:
                    ants[i][record] = corresponding_antlion[record]
            # 没有周边的蚂蚁
            else:
                for j in range(num_flows):
                    if random.uniform(0, 1) < 0.3:
                        ants[i][j] = corresponding_antlion[j]

        # 步骤 5：更新蚁狮种群 ------------------------------------------------------------------------------------------ #
        for i in range(num_ants):
            # 如果蚂蚁的成本小于其蚁狮，那么该蚂蚁将取代原蚁狮，成为新蚁狮种群中的一员
            if cost(ants[i], sizes, periods) < cost(antlions[corresponding[i]], sizes, periods):
                temp = ants[i]
                ants[i] = antlions[corresponding[i]]
                antlions[corresponding[i]] = temp

        # 步骤 6：计算蚁狮种群中所有路由组合的成本函数，取最小的路由组合作为新的精英蚁狮elite --------------------------------------- #
        # 计算更新后的蚁狮种群适应度
        antlions_fitness = [cost(antlions[i], sizes, periods) for i in range(num_antlions)]
        # 如果更新后的最小蚁狮种群适应度小于当前精英蚁狮适应度
        if min(antlions_fitness) < cost(elite, sizes, periods):
            min_index = antlions_fitness.index(min(antlions_fitness))
            elite = antlions[min_index]

    return elite
