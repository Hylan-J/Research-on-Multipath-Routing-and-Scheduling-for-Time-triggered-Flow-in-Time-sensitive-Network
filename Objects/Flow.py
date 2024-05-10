class Flow:
    def __init__(self, id, src, dst, period, size, deadline, redundancy_level):
        # 流的id
        self.id = id
        # 源节点
        self.src = src
        # 目标节点
        self.dst = dst
        # 帧周期, 单位: μs
        self.period = period
        # 帧大小, 单位: bit
        self.size = size
        # 截止时间, 单位: μs
        self.deadline = deadline
        # 冗余等级
        self.redundancy_level = redundancy_level
