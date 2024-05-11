from route import *
from Objects import *
from schedule import no_wait_schedule
from utils import candidate_routing_sets_filtering

# 表 3.2 示例中流集合 S 的参数
flow1 = Flow(id=0, src='ES0', dst='ES5', period=50, size=80, deadline=300, redundancy_level=2)
flow2 = Flow(id=1, src='ES1', dst='ES3', period=100, size=160, deadline=250, redundancy_level=2)
flow3 = Flow(id=2, src='ES2', dst='ES1', period=50, size=160, deadline=300, redundancy_level=2)
flow4 = Flow(id=3, src='ES1', dst='ES4', period=200, size=320, deadline=250, redundancy_level=2)
flows = [flow1, flow2, flow3, flow4]

network = Network(ES_nodes=ES_nodes,
                  SW_nodes=SW_nodes,
                  edges=edges,
                  unreliable_edges=unreliable_egdes,
                  edge_speed=1,
                  delay_switch_process=4,
                  probability_reliable=0.05,
                  probability_unreliable=0.2)
si = [80, 160, 160, 320]
pr = [50, 100, 50, 200]
candidate_routing_sets = candidate_routing_sets_filtering(network=network,
                                                          flows=flows,
                                                          p_th=0.5)
routes = ALO(candidate_flows_NRSs=candidate_routing_sets, sizes=si, periods=pr, max_iterations=100)
print(routes)
solved, Phi = no_wait_schedule(network=network, frames=flows, flows_NRS=routes)
if solved:
    print('调度成功！')
