import random
from Objects.Flow import Flow


def generate_flows(num_flow: int, ES_nodes: list):
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
        trans_period = random.choice([1000, 2000, 4000])
        # 设置流的包大小[64*8 bit, 1512*8 bit]
        packet_length = 8 * random.randrange(64, 1512, 1)
        flows.append(
            Flow(id=id, src=src, dst=dst, trans_period=trans_period, packet_length=packet_length, deadline=300))
    return flows


def display_schedule_results_by_edges(network, flows, schedule_results):
    print('-----------------------------------------------------------------------------------')
    edges = network.edges
    for vi, vj in edges:
        temp = 0
        for flow in flows:
            temp += schedule_results[vi, vj, flow.id].varValue
        if temp > 0:
            print('\n| 链路 {}-{} 的调度结果:'.format(vi, vj))
            for flow in flows:
                start_time = schedule_results[vi, vj, flow.id].varValue
                if start_time > 0:
                    end_time = start_time + network.t_tran(flow.packet_length) + 6
                    print('| 流量 {} : {:5f} μs - {:5f} μs'.format(flow.id, start_time, end_time))
    print('-----------------------------------------------------------------------------------')


def display_schedule_results_by_flows(network, flows, route_results, schedule_results):
    print('-----------------------------------------------------------------------------------')
    edges = network.edges
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
