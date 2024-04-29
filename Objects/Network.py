import networkx as nx
import numpy as np


class Network:
    def __init__(self, ES_nodes, SW_nodes, edges):
        # 网络中的终端节点
        self.ES_nodes = ES_nodes
        # 网络中的交换节点
        self.SW_nodes = SW_nodes
        # 网络中的所有节点
        self.nodes = []
        self.nodes.extend(ES_nodes)
        self.nodes.extend(SW_nodes)

        # 网路中的链路
        self.edges = edges
        # 网络的拓扑
        self.G = None

        # 网络的带宽为 1 Gbit/s=10^9 bit/s
        self.BAND_WIDTH = 10 ** 9
        # 交换机处理时延
        self.DELAY_PROC = 20
        # 链路传输时延
        self.DELAY_TRAN = 0.1
        # 链路的最大带宽利用率
        self.B_max = 0.2

    def build_topology(self):
        """
        建立网络拓扑
        :return:
        """
        # 建立无向图
        self.G = nx.Graph()
        # 增加网络节点
        for node in self.nodes:
            self.G.add_node(node)
        # 增加网络链路
        self.G.add_edges_from(self.edges)

    def t_tran(self, packet_length):
        """
        计算流量的传输时间
        """
        # 传输时间，单位: μs
        trans_time = packet_length * 10 ** 6 / self.BAND_WIDTH + self.DELAY_TRAN
        return trans_time

    def bandwidth_usage_rate(self, flow):
        # 占用带宽(bit/s)
        bandwidth_usage = flow.packet_length / (flow.trans_period / 10 ** 6)
        rate = bandwidth_usage / self.BAND_WIDTH
        return rate

    def flows_lcm(self, flow_trans_periods):
        """
        获取所有流量周期的最小公倍数，即获取超周期
        :param flow_trans_periods:
        :return:
        """
        hyper_period = flow_trans_periods[0]
        for i in range(1, len(flow_trans_periods)):
            hyper_period = np.lcm(hyper_period, flow_trans_periods[i])
        return hyper_period
