import math
import os.path

import matplotlib.pyplot as plt
import numpy as np

from Configs import *
from schedule import *
from route import *
from utils import *

plt.rcParams['font.sans-serif'] = ['SimHei']

if __name__ == '__main__':
    # 流的个数
    # num_flows = [50, 100, 150, 200, 250, 300]
    num_flows = [10, 20, 30, 40]
    network = Network(ES_nodes=ES_nodes,
                      SW_nodes=SW_nodes,
                      links=links,
                      unreliable_links=unreliable_links,
                      link_speed=link_speed,
                      t_switch=t_switch,
                      p_r=p_r,
                      p_ur=p_ur)
    network.build_topology()

    saved = os.path.exists('flows.npy')
    y1 = []
    # for num_flow in num_flows:
    num_flow = 20
    if saved:
        flows = np.load('flows.npy', allow_pickle=True)
    else:
        flows = generate_flows(num_flow=num_flow, ES_nodes=ES_nodes, range_pr=range_pr, range_si=range_si)
    #
    candidate_routes = candidate_routing_sets_filtering(network, flows, 0.0)
    si = [flow.si for flow in flows]
    pr = [flow.pr for flow in flows]
    routes = ALO(candidate_routes=candidate_routes, si=si, pr=pr, max_iterations=100)
    # 计算开始时间
    start_time = time()
    # 对流量排序（传输周期小、报文长度短的邮箱）
    # flows.sort(key=lambda x: (x.pr, x.packet_length))

    solved, t = no_wait_schedule(network=network, flows=flows, routes=routes)
    if solved:
        print('调度成功！')
        if not saved:
            np.save('flows.npy', flows, allow_pickle=True)
    # 计算结束时间
    end_time = time()
    y1.append(end_time - start_time)
