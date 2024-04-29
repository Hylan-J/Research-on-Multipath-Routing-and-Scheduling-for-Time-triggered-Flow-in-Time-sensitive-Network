#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024/4/30 3:20
# @Author  : hylan(https://github.com/Hylan-J)
# @Description :
from copy import deepcopy
from typing import List
import random
from Objects import *


def display_schedule_results_by_flows(network, flows, route_results, schedule_results):
    print('-----------------------------------------------------------------------------------')
    edges = network.links
    for flow in flows:
        print('\n| 流量 {:2d} 的调度结果:'.format(flow.id))
        route = route_results[flow.id]
        for i in range(len(route) - 1):
            for vi, vj in edges:
                if route[i] == vi and route[i + 1] == vj:
                    start_time = schedule_results[vi, vj, flow.id].varValue
                    if start_time != 0:
                        end_time = start_time + network.t_tran(flow.packet_length)
                        print('| 链路 {}-{} : {:5f} μs - {:5f} μs'.format(vi, vj, start_time, end_time))
    print('-----------------------------------------------------------------------------------')


def cal_probability(NRS, unreliable_edges, p_r, p_ur):
    """
    计算对于一组 NRS 而言，目标节点收到正确数据帧的概率计算
    :pram NRS: 不重叠路由集
    :pram unreliable_edges: 不可靠链路
    :pram p_r: 对于可靠链路，一跳之内链路错误发生的概率
    :pram p_ur: 对于不可靠链路，一跳之内链路错误发生的概率
    """
    num_route = len(NRS)
    # 可靠链路数目
    num_reliable = 0
    # 不可靠链路数目
    num_unreliable = 0

    probabilities = [0 for _ in range(num_route)]
    # 对于每一条路径
    for i in range(num_route):
        route = NRS[i]
        # 对于除了终端节点与交换机节点相连接的链路
        for j in range(1, len(route) - 1):
            # 如果该链路在不可靠链路集中
            if tuple(route[j]) in unreliable_edges:
                num_unreliable += 1
            else:
                num_reliable += 1
        probabilities[i] = ((1 - p_r) ** num_reliable) * ((1 - p_ur) ** num_unreliable)

    # 让错误发生的概率连乘
    temp = 0
    for i in range(num_route):
        if i == 0:
            temp = probabilities[0]
        else:
            temp *= probabilities[i]
    # 收到正确数据帧的概率
    probability = 1 - temp
    return probability


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
    if len(routes_target) < flow.rl:
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


def candidate_routing_sets_filtering(network: Network, flows: List[Flow], p_th: float):
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
        for path in list(nx.all_simple_paths(network.topology, flow.v_s, flow.v_d)):
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
                        p_m = cal_probability(NRS, network.unreliable_links, network.p_r, network.p_ur)
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


def generate_flows(num_flow: int, ES_nodes, range_pr, range_si):
    """
    生成流量
    :param num_flow: 流的数量
    :param ES_nodes: 终端节点
    :return:
    """
    flows = []
    for i in range(num_flow):
        # 获取流的id
        id = i
        # 获取流的源节点和目的节点
        # random.sample: 无放回抽取
        src, dst = random.sample(ES_nodes, 2)
        # 设置流的周期{1000μs, 2000μs, 4000μs}
        trans_period = random.choice(range_pr)
        # 设置流的包大小
        packet_length = random.choice(range_si)
        flows.append(Flow(id=id, v_s=src, v_d=dst, pr=trans_period, si=packet_length, dl=300, rl=2))
    return flows
