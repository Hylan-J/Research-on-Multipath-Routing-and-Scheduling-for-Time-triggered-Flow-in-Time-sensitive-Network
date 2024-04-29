import math

import matplotlib.pyplot as plt

from schedule import *
from route import *
from utils import *

plt.rcParams['font.sans-serif'] = ['SimHei']


if __name__ == '__main__':
    # 流的个数
    # num_flows = [50, 100, 150, 200, 250, 300]
    num_flows = [10, 20, 30, 40]
    network = Network(ES_nodes, SW_nodes, edges)
    network.build_topology()

    y1 = []
    # for num_flow in num_flows:
    num_flow = 20
    flows = generate_flows(num_flow=num_flow, ES_nodes=ES_nodes)
    routes = candidate_routing_sets_filtering(network, flows, 0.9)
    for route in routes:
        print(route)
    # 计算开始时间
    start_time = time()
    # 对流量排序（传输周期小、报文长度短的邮箱）
    flows.sort(key=lambda x: (x.trans_period, x.packet_length))
    # dynamic_flow_balancing_schedule(flows, network, ES_nodes, SW_nodes, edges, routes)
    # solved, t = dynamic_flow_balancing_schedule(flows, network, routes)
    # if solved:
    #     display_schedule_results_by_flows(network, flows, routes, t)
    #     display_schedule_results_by_edges(network, flows, t)
    # 计算结束时间
    end_time = time()
    y1.append(end_time - start_time)
