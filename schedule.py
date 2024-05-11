from typing import List

from gurobipy import *
from Objects import *
from utils import *


def no_wait_schedule(network: Network, frames: List[Flow], flows_NRS: List[List]):
    # 定义 ILP 最小化问题 ----------------------------------------------------------------------------------------------- #
    problem = Model(name="无等待调度")

    # 计算超周期及帧实例个数 --------------------------------------------------------------------------------------------- #
    # 获取所有帧的传输周期
    periods = [frame.period for frame in frames]
    # 计算调度的超周期
    hyper_period = calculate_lcm(periods)
    # 计算所有帧的实例个数
    num_instances = [0] * len(frames)
    for frame in frames:
        num_instances[frame.id] = hyper_period // frame.period

    # 定义“传输偏移”变量Φ ----------------------------------------------------------------------------------------------- #
    # 定义传输偏移变量
    Phi = {}
    # 对于每个帧
    for frame in frames:
        # 对于每个副本
        for copy_id in range(frame.redundancy_level):
            # 对于每条链路
            for vi, vj in flows_NRS[frame.id][copy_id]:
                # 对于每个帧实例
                for instance_id in range(num_instances[frame.id]):
                    Phi[frame.id, copy_id, vi, vj, instance_id] = problem.addVar(lb=0, ub=hyper_period,
                                                                                 vtype=GRB.INTEGER,
                                                                                 name=f"Φ_{frame.id}_{copy_id}_{vi}_{vj}_{instance_id}")

    # 添加约束 --------------------------------------------------------------------------------------------------------- #
    # 冗余协议约束：根据IEEE 802.1 CB——冗余协议，每个帧都在源节点之后的第一个桥处被复制，并在目标节点前的最后一个桥处被消除
    # 所以帧副本的第一段和最后一段的传输偏移应当一样
    for frame in frames:
        # 对于每个副本
        for copy_id in range(frame.redundancy_level):
            # 获取第一段链路
            src, switch_first = flows_NRS[frame.id][0][0]
            # 获取最后一段链路
            switch_last, dst = flows_NRS[frame.id][0][-1]
            # 对于每个帧实例
            for instance_id in range(num_instances[frame.id]):
                problem.addConstr(Phi[frame.id, copy_id, src, switch_first, instance_id] -
                                  Phi[frame.id, 0, src, switch_first, instance_id] == 0)
                problem.addConstr(Phi[frame.id, copy_id, switch_last, dst, instance_id] -
                                  Phi[frame.id, 0, switch_last, dst, instance_id] == 0)

    # 延时约束：确保每个流都能在截止时间之前到达其目标节点
    for frame in frames:
        for copy_id in range(frame.redundancy_level):
            for vi, vj in flows_NRS[frame.id][copy_id]:
                if num_instances[frame.id] > 1:
                    # 对于其余的帧实例
                    for instance_id in range(1, num_instances[frame.id]):
                        problem.addConstr(Phi[frame.id, copy_id, vi, vj, instance_id] -
                                          Phi[frame.id, copy_id, vi, vj, 0] -
                                          instance_id * frame.period == 0)
                # 第一个帧实例需要大于0
                problem.addConstr(Phi[frame.id, copy_id, vi, vj, 0] >= 0)
                # 第一个帧实例需要小于其截止时间
                problem.addConstr(Phi[frame.id, copy_id, vi, vj, 0] - frame.deadline <= 0)

    # 避免竞争约束：对于拥有重叠路径的一对数据流，避免其竞争
    for i in range(len(frames) - 1):
        frame_a = frames[i]
        for j in range(i + 1, len(frames)):
            frame_b = frames[j]
            for flow_a_copy_id in range(frame_a.redundancy_level):
                for flow_b_copy_id in range(frame_b.redundancy_level):
                    for flow_a_instance_id in range(num_instances[frame_a.id]):
                        for flow_b_instance_id in range(num_instances[frame_b.id]):
                            for a_edge in flows_NRS[frame_a.id][flow_a_copy_id]:
                                if a_edge in flows_NRS[frame_b.id][flow_b_copy_id]:
                                    vi, vj = a_edge
                                    # 创建互斥二元变量a、b
                                    a = problem.addVar(vtype=GRB.BINARY,
                                                       name=f"a_{frame_a.id}_{flow_a_copy_id}_{flow_a_instance_id}_{frame_b.id}_{flow_b_copy_id}_{flow_b_instance_id}_{vi}_{vj}")
                                    b = problem.addVar(vtype=GRB.BINARY,
                                                       name=f"b_{frame_a.id}_{flow_a_copy_id}_{flow_a_instance_id}_{frame_b.id}_{flow_b_copy_id}_{flow_b_instance_id}_{vi}_{vj}")
                                    problem.addConstr(a + b == 1)
                                    problem.addConstr(
                                        Phi[frame_a.id, flow_a_copy_id, vi, vj, flow_a_instance_id] +
                                        Phi[frame_b.id, flow_b_copy_id, vi, vj, flow_b_instance_id] +
                                        a * (network.t_tran(frame_a.size) -
                                             2 * Phi[frame_b.id, flow_b_copy_id, vi, vj, flow_b_instance_id]) +
                                        b * (network.t_tran(frame_b.size) -
                                             2 * Phi[frame_a.id, flow_a_copy_id, vi, vj, flow_a_instance_id]) <= 0)

    # 路径独立约束：每条流量需要按照其路径次序而传输
    for frame in frames:
        frame_NRS = flows_NRS[frame.id]
        for copy_id in range(frame.redundancy_level):
            frame_route = frame_NRS[copy_id]
            for j in range(len(frame_route) - 1):
                current_edge = frame_route[j]
                vi, vj = current_edge
                next_edge = frame_route[j + 1]
                vii, vjj = next_edge
                # 只要第一个帧实例满足，那么对于超周期内的所有帧实例来说都满足路径独立约束
                problem.addConstr(Phi[frame.id, copy_id, vii, vjj, 0] - Phi[frame.id, copy_id, vi, vj, 0] >= 0)

    # 无等待约束：
    for frame in frames:
        frame_NRS = flows_NRS[frame.id]
        for copy_id in range(len(frame_NRS)):
            frame_route = frame_NRS[copy_id]
            for j in range(len(frame_route) - 1):
                current_edge = frame_route[j]
                vi, vj = current_edge
                next_edge = frame_route[j + 1]
                vii, vjj = next_edge
                hop_delay = network.t_tran(frame.size) + 4
                # 只要第一个帧实例满足，那么对于超周期内的所有帧实例来说都满足路径独立约束
                problem.addConstr(
                    Phi[frame.id, copy_id, vii, vjj, 0] - Phi[frame.id, copy_id, vi, vj, 0] - hop_delay == 0)

    # 定义最大值变量 ---------------------------------------------------------------------------------------------------- #
    F_max = problem.addVar(lb=0, ub=2 * hyper_period, vtype=GRB.INTEGER, name="max_phi")
    # 添加约束，确保其为最大值
    for frame in frames:
        for copy_id in range(frame.redundancy_level):
            for vi, vj in flows_NRS[frame.id][copy_id]:
                for instance_id in range(num_instances[frame.id]):
                    problem.addConstr(Phi[frame.id, copy_id, vi, vj, instance_id] + network.t_tran(frame.size) <= F_max)

    # 设置优化目标，使得max_phi最小化
    problem.setObjective(F_max, GRB.MINIMIZE)
    # 模型求解（GUROBI求解器）
    problem.optimize()

    solved = False
    if problem.status == GRB.OPTIMAL:
        print("ILP 求得最优解\n")
        solved = True
        for frame in frames:
            for copy_id in range(frame.redundancy_level):
                for instance_id in range(hyper_period // frame.period):
                    for vi, vj in flows_NRS[frame.id][copy_id]:
                        start = Phi[frame.id, copy_id, vi, vj, instance_id].X
                        end = start + network.t_tran(frame.size)+4
                        print(f"流量{frame.id} 副本{copy_id} 链路{vi}-{vj} 实例{instance_id}：{start}-{end}")
    return solved, Phi
