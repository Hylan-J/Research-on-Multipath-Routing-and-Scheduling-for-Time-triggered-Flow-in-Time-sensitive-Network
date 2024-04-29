import random


# 主要蚁狮算法
def ALO(num_ants, num_lions, candidate_routing_sets, max_iterations):
    """
    蚁狮优化算法（ant_lion_optimization，ALO）
    """

    def init_population(num_initial_solutions, candidate_routing_sets):
        """
        随机生成初始解
        : parm num_solutions: 需要生成的初始解的个数
        : parm candidate_routing_sets: 候选路由集
        """
        initial_solutions = [random.choice(candidate_routing_sets) for _ in range(num_initial_solutions)]
        return initial_solutions

    def cost(route):
        """
        成本函数
        """
        fitness = len(route)
        return fitness

    # 步骤1：随机生成一系列初始解，作为蚂蚁和蚁狮的初始种群
    ant_population = init_population(num_ants, candidate_routing_sets)
    lion_population = init_population(num_lions, candidate_routing_sets)

    # 初始化精英蚁狮
    elite_antlion = min(lion_population, key=cost)

    for _ in range(max_iterations):
        ################################################################################################################
        # 步骤2：计算所有蚂蚁和蚁狮的成本函数
        # ------------------------------------------------------------------------------------------------------------ #
        ant_fitness = [cost(route) for route in ant_population]
        lion_fitness = [cost(route) for route in lion_population]

        ################################################################################################################
        # 步骤3：通过轮盘赌策略为每个蚂蚁选择一个相应的蚁狮
        # ------------------------------------------------------------------------------------------------------------ #
        chosen_lions = random.choices(lion_population, weights=lion_fitness, k=num_ants)

        ################################################################################################################
        # 步骤4：蚂蚁随机游走并更新位置
        # ------------------------------------------------------------------------------------------------------------ #
        for i in range(num_ants):
            ant_population[i] = random.choice(chosen_lions[i])

        ################################################################################################################
        # 步骤5：更新蚁狮种群
        # ------------------------------------------------------------------------------------------------------------ #
        for i in range(num_ants):
            # 如果该蚂蚁的成本小于其蚁狮
            if ant_fitness[i] < lion_fitness[i]:
                # 那么该蚂蚁将取代原蚁狮
                lion_population[i] = ant_population[i]

        ################################################################################################################
        # 步骤6：更新精英蚁狮
        # ------------------------------------------------------------------------------------------------------------ #
        elite_antlion = min(lion_population, key=cost)

    return elite_antlion


# 示例使用
search_space = [["A", "B", "C"], ["D", "E", "F"], ["G", "H", "I"]]
num_ants = 10
num_lions = 5
max_iterations = 100

elite_solution = ALO(num_ants, num_lions, search_space, max_iterations)
print("Elite solution:", elite_solution)
