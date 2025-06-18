import numpy as np

class MERADS_QFUR_V10a:
    def __init__(self, budget_factor=2000, population_size=50, memory_factor=0.25):
        self.budget_factor = budget_factor
        self.population_size = population_size
        self.F_init = 0.55
        self.F_end = 0.85
        self.memory_factor = memory_factor

    def __call__(self, problem):
        if hasattr(problem, "meta_data"):
            dim = problem.meta_data.n_variables
            budget = self.budget_factor * dim
            lb, ub = problem.bounds.lb, problem.bounds.ub
        else:
            dim = 5
            budget = self.budget_factor * dim
            lb, ub = -5, 5

        pop = np.random.uniform(lb, ub, (self.population_size, dim))
        fit = np.array([problem(x) for x in pop])
        t = self.population_size
        archive = []

        best_idx = np.argmin(fit)
        xopt = pop[best_idx].copy()
        fopt = fit[best_idx]
        memory = np.zeros(dim)
        success_CR = [0.95]
        stagnation = 0

        while t < budget:
            F = self.F_init + (self.F_end - self.F_init) * (t / budget)
            CR = np.clip(np.mean(success_CR[-5:]) + np.random.normal(0, 0.01), 0.85, 1.0)

            for i in range(self.population_size):
                if t >= budget: break
                idxs = [j for j in range(self.population_size) if j != i]
                x1, x2, x3 = pop[np.random.choice(idxs, 3, replace=False)]
                direction = (xopt - x1) + (x2 - x3) + self.memory_factor * memory
                mutant = x1 + F * direction
                if archive:
                    mutant = 0.9 * mutant + 0.1 * archive[np.random.randint(len(archive))]
                mutant = np.clip(mutant, lb, ub)

                mask = np.random.rand(dim) < CR
                if not np.any(mask):
                    mask[np.random.randint(dim)] = True
                trial = np.where(mask, mutant, pop[i])
                f_trial = problem(trial)
                t += 1

                if f_trial < fit[i]:
                    memory = 0.9 * memory + 0.1 * F * (mutant - pop[i])
                    pop[i] = trial
                    fit[i] = f_trial
                    if f_trial < fopt:
                        fopt = f_trial
                        xopt = trial.copy()
                        best_idx = i
                        success_CR.append(CR)
                        stagnation = 0
                else:
                    stagnation += 1

                archive.append(trial)
                if len(archive) > 100:
                    archive.pop(0)

        return fopt, xopt
