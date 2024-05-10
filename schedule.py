from typing import List

from gurobipy import *
from Objects import *


def no_wait_schedule(network: Network, flows: List[Flow], routes: List[List]):
    # ---------------------------------------------------------------------------------------------------------------- #
    # 定义 ILP 最小化问题
    # ---------------------------------------------------------------------------------------------------------------- #
    problem = Model(name="无等待调度")

    # ---------------------------------------------------------------------------------------------------------------- #
    # 定义“传输偏移”变量Φ
    Phi = {}
    for flow in flows:
        for route_id in range(flow.redundancy_level):
            for vi, vj in routes[flow.id][route_id]:
                Phi[flow.id, route_id, vi, vj] = problem.addVar(lb=0, ub=40000, vtype=GRB.INTEGER,
                                                                name=f"Φ_{flow.id}_{route_id}_{vi}_{vj}")
    # ---------------------------------------------------------------------------------------------------------------- #

    ####################################################################################################################
    # 约束
    # ---------------------------------------------------------------------------------------------------------------- #
    # 延时约束
    for flow in flows:
        for route_id in range(flow.redundancy_level):
            for vi, vj in routes[flow.id][route_id]:
                # 添加约束 Phi >= 0
                problem.addConstr(Phi[flow.id, route_id, vi, vj] >= 0)
                # 添加约束 Phi - flow.dl <= 0
                problem.addConstr(Phi[flow.id, route_id, vi, vj] - flow.deadline <= 0)

    # 避免竞争约束
    for i in range(len(flows) - 1):
        flow_a = flows[i]
        for j in range(i + 1, len(flows)):
            flow_b = flows[j]
            NRS_a = routes[flow_a.id]
            NRS_b = routes[flow_b.id]
            for route_a_id in range(flow_a.redundancy_level):
                for route_b_id in range(flow_b.redundancy_level):
                    for link_a in NRS_a[route_a_id]:
                        if link_a in NRS_b[route_b_id]:
                            vi, vj = link_a
                            # 创建互斥二元变量a、b
                            a = problem.addVar(vtype=GRB.BINARY,
                                               name=f'a_{flow_a.id}_{route_a_id}_{flow_b.id}_{route_b_id}_{vi}_{vj}')
                            b = problem.addVar(vtype=GRB.BINARY,
                                               name=f'b_{flow_a.id}_{route_a_id}_{flow_b.id}_{route_b_id}_{vi}_{vj}')
                            problem.addConstr(a + b == 1)
                            problem.addConstr(Phi[flow_a.id, route_a_id, vi, vj] + Phi[flow_b.id, route_b_id, vi, vj] +
                                              a * (network.t_tran(flow_a.size) - 2 * Phi[flow_b.id, route_b_id, vi, vj]) +
                                              b * (network.t_tran(flow_b.size) - 2 * Phi[
                                flow_a.id, route_a_id, vi, vj]) <= 0)

    # 路径独立约束
    for flow in flows:
        NRS = routes[flow.id]
        for route_id in range(flow.redundancy_level):
            for j in range(len(NRS[route_id]) - 1):
                current_edge = NRS[route_id][j]
                vi, vj = current_edge
                next_edge = NRS[route_id][j + 1]
                vii, vjj = next_edge
                problem.addConstr(Phi[flow.id, route_id, vii, vjj] - Phi[flow.id, route_id, vi, vj] >= 0)

    # 无等待约束
    for flow in flows:
        NRS = routes[flow.id]
        for route_id in range(len(NRS)):
            for j in range(len(NRS[route_id]) - 1):
                current_edge = NRS[route_id][j]
                vi, vj = current_edge
                next_edge = NRS[route_id][j + 1]
                vii, vjj = next_edge
                hop_delay = network.t_tran(flow.size) + 4
                problem.addConstr(Phi[flow.id, route_id, vii, vjj] - Phi[flow.id, route_id, vi, vj] - hop_delay == 0)

    # 定义最大值变量
    F_max = problem.addVar(lb=0, ub=40000, vtype=GRB.INTEGER, name="max_phi")

    # 添加约束以确保Phi变量的最大值不超过max_phi
    for var in Phi.values():
        problem.addConstr(var <= F_max)

    # 设置优化目标，使得max_phi最小化
    problem.setObjective(F_max, GRB.MINIMIZE)

    # 模型求解（GUROBI求解器）
    problem.optimize()

    solved = False
    if problem.status == GRB.OPTIMAL:
        print("ILP 求得最优解\n")
        solved = True
    return solved, Phi
