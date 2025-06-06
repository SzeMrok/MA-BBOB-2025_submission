import numpy as np
from scipy.stats import qmc

def sobol_sampling(n_points, dim, lb=-5, ub=5):
    sampler = qmc.Sobol(d=dim, scramble=True)
    sample = sampler.random_base2(m=int(np.ceil(np.log2(n_points))))
    sample = sample[:n_points]
    return lb + (ub - lb) * sample

class MERADS_QFUR_V21a:
    def __init__(self, budget_factor=2000, memory_factor=0.3):
        self.budget_factor = budget_factor
        self.memory_factor = memory_factor

    def __call__(self, problem):
        dim = getattr(problem.meta_data, "n_variables", 5)
        budget = self.budget_factor * dim
        lb, ub = -5, 5
        pop_size = 50
        pop = sobol_sampling(pop_size, dim, lb, ub)
        fit = np.array([problem(x) for x in pop])
        t = pop_size
        archive = []
        memory = np.zeros(dim)
        xopt = pop[np.argmin(fit)].copy()
        fopt = np.min(fit)

        while t < budget:
            decay = 1 - t / budget
            for i in range(pop_size):
                F = np.clip(np.random.normal(0.5, 0.1), 0.1, 0.9)
                CR = 0.9
                idxs = [j for j in range(pop_size) if j != i]
                x1, x2, x3 = pop[np.random.choice(idxs, 3, replace=False)]
                direction = (xopt - x1) + (x2 - x3) + decay * self.memory_factor * memory
                mutant = x1 + F * direction
                if archive:
                    mutant = 0.9 * mutant + 0.1 * archive[np.random.randint(len(archive))]
                mutant = np.clip(mutant, lb, ub)

                mask = np.random.rand(dim) < CR
                if not np.any(mask): mask[np.random.randint(dim)] = True
                trial = np.where(mask, mutant, pop[i])
                f_trial = problem(trial)
                t += 1

                if f_trial < fit[i]:
                    memory = 0.85 * memory + 0.15 * (mutant - pop[i])
                    pop[i] = trial
                    fit[i] = f_trial
                    archive.append(trial)
                    if f_trial < fopt:
                        xopt = trial.copy()
                        fopt = f_trial
                if len(archive) > 100:
                    archive.pop(0)

        return fopt, xopt
