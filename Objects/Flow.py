class Flow:
    def __init__(self, id, v_s, v_d, pr, si, dl, rl):
        # 流的id
        self.id = id
        # 源节点
        self.v_s = v_s
        # 目标节点
        self.v_d = v_d
        # 帧周期, 单位: μs
        self.pr = pr
        # 帧大小, 单位: bit
        self.si = si
        # 截止时间, 单位: μs
        self.dl = dl
        # 冗余等级
        self.rl = rl
