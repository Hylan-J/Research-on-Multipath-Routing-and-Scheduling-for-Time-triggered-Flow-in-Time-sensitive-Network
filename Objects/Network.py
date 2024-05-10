import networkx as nx


class Network:
    def __init__(self, ES_nodes, SW_nodes, edges, unreliable_edges,
                 edge_speed, delay_switch_process, probability_reliable, probability_unreliable):
        # 网络中的终端节点
        self.ES_nodes = ES_nodes
        # 网络中的交换节点
        self.SW_nodes = SW_nodes
        # 网络中的所有节点
        self.nodes = []
        self.nodes.extend(ES_nodes)
        self.nodes.extend(SW_nodes)
        # 网络中的所有链路
        self.edges = edges
        # 网络中的不可靠链路
        self.unreliable_edges = unreliable_edges
        # 网络的链路速率
        self.edge_speed = edge_speed
        # 交换机处理时延
        self.delay_switch_process = delay_switch_process
        # 可靠链路错误发生的概率
        self.probability_reliable = probability_reliable
        # 不可靠链路错误发生的概率
        self.probability_unreliable = probability_unreliable
        # ------------------------------------------------------------------------------------------------------------ #
        # 建立网络拓扑
        self.topology = nx.Graph()
        # 增加网络节点
        for node in self.nodes:
            self.topology.add_node(node)
        # 增加网络链路
        self.topology.add_edges_from(self.edges)
        # ------------------------------------------------------------------------------------------------------------ #

    def t_tran(self, size):
        """
        计算帧的传输时间
        Args:
            size: 帧的大小

        Returns:

        """
        # 传输时间，单位: μs
        trans_time = size / self.edge_speed
        return trans_time
