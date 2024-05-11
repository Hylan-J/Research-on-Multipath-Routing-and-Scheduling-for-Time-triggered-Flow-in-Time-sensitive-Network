from time import time

import matplotlib.pyplot as plt

from route import *
from schedule import *
from utils import *

plt.rcParams['font.sans-serif'] = ['SimHei']

if __name__ == '__main__':
    # 流的个数
    # num_flows = [50, 100, 150, 200, 250, 300]
    num_flows = [10, 20, 30, 40]
    network = Network(ES_nodes=ES_nodes,
                      SW_nodes=SW_nodes,
                      edges=edges,
                      unreliable_edges=unreliable_egdes,
                      edge_speed=edge_speed,
                      delay_switch_process=delay_switch_process,
                      probability_reliable=probability_reliable,
                      probability_unreliable=probability_unreliable)

    # saved = os.path.exists('flows.npy')
    #
    # # for num_flow in num_flows:
    # num_flow = 10
    # if saved:
    #     flows = np.load('flows.npy', allow_pickle=True)
    # else:
    #     flows = generate_flows(num_flow=num_flow, ES_nodes=ES_nodes, range_pr=range_pr, range_si=range_si)

    # flows = np.load('flows.npy', allow_pickle=True)
    flows = generate_flows(num_flow=10, ES_nodes=ES_nodes, range_pr=range_pr, range_si=range_si)
    candidate_routes = candidate_routing_sets_filtering(network, flows, 0.0)
    si = [flow.size for flow in flows]
    pr = [flow.period for flow in flows]
    routes = ALO(candidate_flows_NRSs=candidate_routes, sizes=si, periods=pr, max_iterations=100)
    print(routes)
    # 获取所有帧的传输周期
    periods = [frame.period for frame in flows]
    # 计算调度的超周期
    hyper_period = calculate_lcm(periods)

    # 计算开始时间
    start_time = time()

    solved, Phi = no_wait_schedule(network=network, frames=flows, flows_NRS=routes)
    if solved:
        print('调度成功！')
        # np.save('flows.npy', flows, allow_pickle=True)
        # if not saved:
        #     np.save('flows.npy', flows, allow_pickle=True)
    # 计算结束时间
    end_time = time()
