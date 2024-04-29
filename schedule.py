from pulp import *

from Objects import *


def no_wait_schedule(network: Network, flows: List[Flow], routes: List[List]):
    ####################################################################################################################
    # 定义 ILP 最小化问题
    # ---------------------------------------------------------------------------------------------------------------- #
    problem = LpProblem(name="无等待调度", sense=LpMinimize)

    # 定义传输偏移变量
    Phi = LpVariable.dicts(name="Φ",
                           indices=[(flow.id, route_id, vi, vj) for flow in flows for route_id in
                                    range(flow.rl) for vi, vj in routes[flow.id][route_id]],
                           lowBound=0,
                           upBound=40000,
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
    # for i in range(len(flows) - 1):
    #     flow_a = flows[i]
    #     for j in range(i + 1, len(flows)):
    #         flow_b = flows[j]
    #         NRS_a = routes[flow_a.id]
    #         NRS_b = routes[flow_b.id]
    #         for route_a_id in range(flow_a.rl):
    #             for route_b_id in range(flow_b.rl):
    #                 for link_a in NRS_a[route_a_id]:
    #                     if link_a in NRS_b[route_b_id]:
    #                         vi, vj = link_a
    #                         # 创建互斥二元变量a、b
    #                         a = LpVariable(name=f'a_{flow_a.id}_{route_a_id}_{flow_b.id}_{route_b_id}_{vi}_{vj}',
    #                                        cat=LpBinary)
    #                         b = LpVariable(name=f'b_{flow_a.id}_{route_a_id}_{flow_b.id}_{route_b_id}_{vi}_{vj}',
    #                                        cat=LpBinary)
    #                         problem.addConstraint(LpConstraint(
    #                             e=a + b,
    #                             sense=LpConstraintEQ,
    #                             rhs=1))
    #                         problem.addConstraint(LpConstraint(
    #                             e=Phi[flow_a.id, route_a_id, vi, vj] + network.t_tran(flow_a.si) - Phi[
    #                                 flow_b.id, route_b_id, vi, vj] + a*100000,
    #                             sense=LpConstraintLE,
    #                             rhs=0))
    #                         problem.addConstraint(LpConstraint(
    #                             e=Phi[flow_b.id, route_b_id, vi, vj] + network.t_tran(flow_b.si) - Phi[
    #                                 flow_a.id, route_a_id, vi, vj] + b*100000,
    #                             sense=LpConstraintLE,
    #                             rhs=0))

    # 路径独立约束
    for flow in flows:
        NRS = routes[flow.id]
        for route_id in range(flow.rl):
            for j in range(len(NRS[route_id]) - 1):
                current_edge = NRS[route_id][j]
                vi, vj = current_edge
                next_edge = NRS[route_id][j + 1]
                vii, vjj = next_edge
                problem.addConstraint(LpConstraint(
                    e=Phi[flow.id, route_id, vii, vjj] - Phi[flow.id, route_id, vi, vj],
                    sense=LpConstraintGE,
                    rhs=0))

    # 无等待约束
    for flow in flows:
        NRS = routes[flow.id]
        for route_id in range(len(NRS)):
            for j in range(len(NRS[route_id]) - 1):
                current_edge = NRS[route_id][j]
                vi, vj = current_edge
                next_edge = NRS[route_id][j + 1]
                vii, vjj = next_edge
                hop_delay = network.t_tran(flow.si) + 4
                problem.addConstraint(LpConstraint(
                    e=Phi[flow.id, route_id, vii, vjj] - Phi[flow.id, route_id, vi, vj] - hop_delay,
                    sense=LpConstraintEQ,
                    rhs=0))

    ####################################################################################################################
    # 优化目标
    # ---------------------------------------------------------------------------------------------------------------- #
    # max_value = 0
    # for flow in flows:
    #     NRS = routes[flow.id]
    #     for route_id in range(flow.rl):
    #         # 最后一段链路的偏移
    #         b_last, v_d = NRS[route_id][-1]
    #         # temp = Phi[flow.id, route_id, b_last, v_d].value() + network.t_tran(flow.si)
    #         temp = Phi[flow.id, route_id, b_last, v_d].value()
    #         if max_value <= temp:
    #             max_value = temp

    problem.setObjective(lpSum(Phi))

    # 模型求解（GUROBI求解器）
    problem.solve(GUROBI_CMD(msg=False))

    solved = False
    if problem.status == LpStatusOptimal:
        print("ILP 求得最优解\n")
        solved = True
    return solved, Phi
