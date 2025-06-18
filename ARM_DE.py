import numpy as np

class ARM_DE:
    def __init__(self, budget_factor=2000, population_size=50, F_init=0.55, F_end=0.85, memory_factor=0.25):
        self.budget_factor = budget_factor
        self.population_size = population_size
        self.F_init = F_init
        self.F_end = F_end
        self.memory_factor = memory_factor

    def __call__(self, problem):
        if hasattr(problem, "meta_data") and hasattr(problem, "bounds"):
            dim = problem.meta_data.n_variables
            budget = self.budget_factor * dim
            lb, ub = problem.bounds.lb, problem.bounds.ub
        else:
            dim = getattr(self, "dim", 5)
            budget = self.budget_factor * dim
            lb, ub = -5, 5

        pop = np.random.uniform(lb, ub, (self.population_size, dim))
        fit = np.array([problem(x) for x in pop])
        t = self.population_size

        best_idx = np.argmin(fit)
        xopt = pop[best_idx].copy()
        fopt = fit[best_idx]
        memory = np.zeros(dim)
        success_CR = [0.95]
        cross_mask = np.empty(dim, dtype=bool)
        trial = np.empty(dim)

        while t < budget:
            F = self.F_init + (self.F_end - self.F_init) * (t / budget)
            CR = np.clip(np.mean(success_CR[-5:]) + np.random.normal(0, 0.01), 0.85, 1.0)

            for i in range(self.population_size):
                if t >= budget: break
                idxs = [j for j in range(self.population_size) if j != i]
                x1, x2, x3 = pop[np.random.choice(idxs, 3, replace=False)]

                mutant = x1 + F * ((xopt - x1) + (x2 - x3) + self.memory_factor * memory)
                np.clip(mutant, lb, ub, out=mutant)

                np.less(np.random.rand(dim), CR, out=cross_mask)
                if not np.any(cross_mask):
                    cross_mask[np.random.randint(dim)] = True
                np.copyto(trial, pop[i])
                np.copyto(trial, mutant, where=cross_mask)

                f_trial = problem(trial)
                t += 1

                if f_trial < fit[i]:
                    memory = 0.9 * memory + 0.1 * F * (mutant - pop[i])
                    pop[i] = trial
                    fit[i] = f_trial
                    if f_trial < fopt:
                        xopt = trial.copy()
                        fopt = f_trial
                        best_idx = i
                        success_CR.append(CR)

        return fopt, xopt
