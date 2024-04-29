import networkx as nx


class Network:
    def __init__(self, ES_nodes, SW_nodes, links, unreliable_links, link_speed, t_switch, p_r, p_ur):
        # 网络中的终端节点
        self.ES_nodes = ES_nodes
        # 网络中的交换节点
        self.SW_nodes = SW_nodes
        # 网络中的所有节点
        self.nodes = []
        self.nodes.extend(ES_nodes)
        self.nodes.extend(SW_nodes)
        # 网络中的所有链路
        self.links = links
        # 网络中的不可靠链路
        self.unreliable_links = unreliable_links
        # 网络的拓扑
        self.topology = None

        # 网络的链路速率
        self.link_speed = link_speed
        # 交换机处理时延
        self.t_switch = t_switch
        # 可靠链路错误发生的概率
        self.p_r = p_r
        # 不可靠链路错误发生的概率
        self.p_ur = p_ur

    def build_topology(self):
        """
        建立网络拓扑
        Returns:

        """
        # 建立无向图
        self.topology = nx.Graph()
        # 增加网络节点
        for node in self.nodes:
            self.topology.add_node(node)
        # 增加网络链路
        self.topology.add_edges_from(self.links)

    def t_tran(self, si):
        """
        计算帧的传输时间
        Args:
            si: 帧的大小

        Returns:

        """
        # 传输时间，单位: μs
        trans_time = si / self.link_speed
        return trans_time
