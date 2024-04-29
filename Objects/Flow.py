class Flow:
    def __init__(self, id, src, dst, trans_period, packet_length, deadline, redundancy_level=2):
        # 流的id
        self.id = id
        # 源节点
        self.src = src
        # 目的节点
        self.dst = dst
        # 发送周期, 单位: μs
        self.trans_period = trans_period
        # 报文长度, 单位: bit
        self.packet_length = packet_length
        # 截止时间, 单位: μs
        self.deadline = deadline
        # 流量的冗余等级
        self.redundancy_level = redundancy_level