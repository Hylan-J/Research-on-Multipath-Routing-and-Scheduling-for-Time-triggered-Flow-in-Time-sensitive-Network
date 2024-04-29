from pulp import *

from Objects.Flow import Flow
from Objects.Network import Network
from Configs import *


def no_wait_schedule(flows: List[Flow], network: Network, routes: List[List]):
    edges = network.links
    ES_nodes = network.ES_nodes
    SW_nodes = network.SW_nodes

    ####################################################################################################################
    # 定义 ILP 最小化问题
    # ---------------------------------------------------------------------------------------------------------------- #
    problem = LpProblem(name="无等待调度", sense=LpMinimize)

    # 定义传输偏移变量
    Phi = LpVariable.dicts(name="Φ",
                           indices=[(flow.id, route_id, vi, vj, flow.id) for flow in flows for route_id in
                                    range(flow.rl) for vi, vj in routes[flow.id][route_id]],
                           lowBound=0,
                           upBound=5000,
                           cat=LpInteger)

    ####################################################################################################################
    # 约束
    # ---------------------------------------------------------------------------------------------------------------- #
    # 延时约束
    for flow in flows:
        for route_id in range(flow.rl):
            for vi, vj in routes[flow.id][route_id]:
                problem.addConstraint(LpConstraint(
                    e=Phi[flow.id, route_id, vi, vj],
                    sense=LpConstraintGE,
                    rhs=0))
                problem.addConstraint(LpConstraint(
                    e=Phi[flow.id, route_id, vi, vj] - flow.dl,
                    sense=LpConstraintLE,
                    rhs=0))

    # 避免竞争约束
    for i in range(len(flows) - 1):
        flow_a = flows[i]
        for j in range(i + 1, len(flows)):
            flow_b = flows[j]
            route_a = routes[flow_a.id]
            route_b = routes[flow_b.id]
            for ii in range(len(route_a)):
                for jj in range(len(route_b)):
                    for edge in route_a[ii]:
                        if edge in route_b[jj]:
                            vi, vj = edge
                            # 创建互斥二元变量a、b
                            a = LpVariable(name=f'a_{flow_a.id}_{route_a}_{flow_b.id}_{route_b}_{vi}_{vj}',
                                           cat=LpBinary)
                            b = LpVariable(name=f'b_{flow_a.id}_{route_a}_{flow_b.id}_{route_b}_{vi}_{vj}',
                                           cat=LpBinary)

                            problem.addConstraint(LpConstraint(
                                e=(Phi[flow_a.id, ii, vi, vj] + network.t_tran(flow_a.si) - Phi[
                                    flow_b.id, jj, vi, vj]) * a,
                                sense=LpConstraintLE,
                                rhs=0))
                            problem.addConstraint(LpConstraint(
                                e=(Phi[flow_b.id, jj, vi, vj] + network.t_tran(flow_b.si) - Phi[
                                    flow_a.id, ii, vi, vj]) * b,
                                sense=LpConstraintLE,
                                rhs=0))
                            problem.addConstraint(LpConstraint(
                                e=a + b,
                                sense=LpConstraintGE,
                                rhs=1))
    # 路径独立约束
    for flow in flows:
        route = routes[flow.id]
        for i in range(len(route)):
            for j in range(len(route[i]) - 1):
                current_edge = route[i][j]
                vi, vj = current_edge
                next_edge = route[i][j + 1]
                vii, vjj = next_edge
                problem.addConstraint(LpConstraint(
                    e=Phi[flow.id, i, vii, vjj] - Phi[flow.id, i, vi, vj],
                    sense=LpConstraintGE,
                    rhs=0))

    # 无等待约束
    for flow in flows:
        route = routes[flow.id]
        for i in range(len(route)):
            for j in range(len(route[i]) - 1):
                current_edge = route[i][j]
                vi, vj = current_edge
                next_edge = route[i][j + 1]
                vii, vjj = next_edge
                hop_delay = network.t_tran(flow.si) + 4
                problem.addConstraint(LpConstraint(
                    e=Phi[flow.id, i, vii, vjj] - Phi[flow.id, i, vi, vj] - hop_delay,
                    sense=LpConstraintGE,
                    rhs=0))

    ####################################################################################################################
    # 优化目标
    # ---------------------------------------------------------------------------------------------------------------- #
    max_value = 0
    for flow in flows:
        route = routes[flow.id]
        for i in range(len(route)):
            # 最后一段链路的偏移
            b_last, v_d = route[i][-1]
            temp = Phi[flow.id, i, b_last, v_d].value() + network.t_tran(flow.si)
            if max_value <= temp:
                max_value = temp

    problem.setObjective(max_value)

    # 模型求解（GUROBI求解器）
    problem.solve(GUROBI_CMD(msg=False))

    solved = False
    if problem.status == LpStatusOptimal:
        print("ILP 求得最优解\n")
        solved = True
    return solved, Phi
